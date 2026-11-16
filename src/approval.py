from dataclasses import dataclass
from decimal import Decimal

from src.config import (
    CREDIT_LIMIT,
    DECLARED_MONTHLY_INCOME,
    MAX_INSTALLMENT_SHARE_OF_INCOME,
)


@dataclass(frozen=True)
class ApprovalDecision:
    approved: bool
    reasons: tuple[str, ...]


def decide_loan(
    cart_total: Decimal,
    monthly_payment: Decimal,
    declared_monthly_income: Decimal = DECLARED_MONTHLY_INCOME,
    credit_limit: Decimal = CREDIT_LIMIT,
    max_share_of_income: Decimal = MAX_INSTALLMENT_SHARE_OF_INCOME,
) -> ApprovalDecision:
    """Approve a loan only when both checks from SPEC.md pass.

    What it computes: (1) the cart total must not exceed the credit limit, and (2) the
    regular monthly payment must not exceed the allowed share of declared monthly income.

    Why these checks: the credit limit caps how much we lend to one customer, and the income
    share is an affordability test so the payment leaves room for the customer's other
    expenses. Both thresholds are product-design assumptions, not regulatory limits.
    """
    reasons: list[str] = []
    if cart_total > credit_limit:
        reasons.append(f"Requested amount is above the credit limit of ${credit_limit:,.2f} MXN.")

    max_monthly_payment = declared_monthly_income * max_share_of_income
    if monthly_payment > max_monthly_payment:
        reasons.append(
            f"Monthly payment is above {max_share_of_income:.0%} of declared income "
            f"(${max_monthly_payment:,.2f} MXN)."
        )
    return ApprovalDecision(approved=not reasons, reasons=tuple(reasons))
