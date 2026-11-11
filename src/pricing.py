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


def add_months(start_date: date, months: int) -> date:
    month_index = start_date.year * 12 + start_date.month - 1 + months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    day = min(start_date.day, monthrange(year, month)[1])
    return date(year, month, day)


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
    )
