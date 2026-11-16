from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from src.config import MONTHLY_INTEREST_RATE, TERMS_MONTHS


CENT = Decimal("0.01")
ZERO = Decimal("0")


@dataclass(frozen=True)
class InstallmentQuote:
    number: int
    due_date: date
    amount: Decimal


@dataclass(frozen=True)
class PriceQuote:
    term_months: int
    interest: Decimal
    total_repayment: Decimal
    monthly_payment: Decimal
    installments: tuple[InstallmentQuote, ...]
    # Reference cost on the balance still owed, in percent per year (see effective_annual_rate).
    effective_annual_rate: Decimal


def add_months(start_date: date, months: int) -> date:
    month_index = start_date.year * 12 + start_date.month - 1 + months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(start_date.day, monthrange(year, month)[1])
    return date(year, month, day)


def effective_annual_rate(
    principal: Decimal, payments: tuple[Decimal, ...]
) -> Decimal:
    """Return the annualized internal rate of return of the customer's payments, in percent.

    What it computes: the monthly rate r for which the present value of the scheduled
    payments (one per month, starting one month after checkout) equals the price the
    customer receives today, annualized as (1 + r)^12 - 1.

    Why this formula: flat interest on the original price hides the real cost, because the
    customer repays part of the principal every month and so owes less than the full price
    for most of the term. The internal rate of return measures the cost on the balance
    actually owed. This is a reference figure, not the official CAT (Banxico Circular
    21/2009), which includes every cost of the credit. TODO-verify the CAT with Condusef.
    """
    if principal <= ZERO or not payments:
        raise ValueError("Principal and payments are required.")

    def present_value(monthly_rate: Decimal) -> Decimal:
        return sum(
            (
                payment / (Decimal(1) + monthly_rate) ** month
                for month, payment in enumerate(payments, start=1)
            ),
            ZERO,
        )

    # present_value falls as the rate rises, so a bisection finds the rate where it equals
    # the principal. The upper bound of 100% per month is far above any price we offer.
    low, high = ZERO, Decimal(1)
    for _ in range(100):
        middle = (low + high) / 2
        if present_value(middle) > principal:
            low = middle
        else:
            high = middle
    monthly_rate = (low + high) / 2
    annual_rate = ((Decimal(1) + monthly_rate) ** 12 - Decimal(1)) * 100
    return annual_rate.quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_quote(
    cart_total: Decimal, term_months: int, checkout_date: date
) -> PriceQuote:
    if not cart_total.is_finite() or cart_total <= ZERO:
        raise ValueError("Cart total must be a finite amount greater than zero.")
    if term_months not in TERMS_MONTHS:
        raise ValueError(f"Term must be one of: {', '.join(map(str, TERMS_MONTHS))}.")

    # Flat interest is price × 4% × term, based on the original price as required by SPEC.
    interest = (cart_total * MONTHLY_INTEREST_RATE * term_months).quantize(CENT)
    total_repayment = (cart_total + interest).quantize(CENT)
    # Round regular installments to cents; currency cannot represent fractional cents.
    monthly_payment = (total_repayment / term_months).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
    # Set the final installment to the remaining balance so the schedule equals the total exactly.
    final_payment = total_repayment - monthly_payment * (term_months - 1)
    installments = tuple(
        InstallmentQuote(
            number=number,
            due_date=add_months(checkout_date, number),
            amount=final_payment if number == term_months else monthly_payment,
        )
        for number in range(1, term_months + 1)
    )

    return PriceQuote(
        term_months=term_months,
        interest=interest,
        total_repayment=total_repayment,
        monthly_payment=monthly_payment,
        installments=installments,
        effective_annual_rate=effective_annual_rate(
            cart_total, tuple(installment.amount for installment in installments)
        ),
    )
