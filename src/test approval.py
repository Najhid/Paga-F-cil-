from decimal import Decimal

import pytest

from src.approval import decide_loan

INCOME = Decimal("12000.00")
LIMIT = Decimal("6500.00")
SHARE = Decimal("0.30")


def decide(cart: str, payment: str, income: Decimal = INCOME):
    return decide_loan(Decimal(cart), Decimal(payment), income, LIMIT, SHARE)


def test_approves_when_amount_and_payment_fit() -> None:
    decision = decide("2500.00", "516.67")

    assert decision.approved
    assert decision.reasons == ()


def test_amount_exactly_at_the_credit_limit_is_approved() -> None:
    assert decide("6500.00", "1343.33").approved


def test_amount_above_the_credit_limit_is_rejected() -> None:
    decision = decide("6500.01", "1343.34")

    assert not decision.approved
    assert len(decision.reasons) == 1
    assert "credit limit" in decision.reasons[0]


def test_payment_exactly_at_the_income_share_is_approved() -> None:
    # 30% of 12,000 is 3,600.00, so a payment of exactly 3,600.00 passes.
    assert decide("5000.00", "3600.00").approved


def test_payment_above_the_income_share_is_rejected() -> None:
    decision = decide("5000.00", "3600.01")

    assert not decision.approved
    assert "30% of declared income" in decision.reasons[0]


@pytest.mark.parametrize(
    ("income", "approved"),
    [("1722.24", True), ("1722.23", False)],
)
def test_spec_minimum_income_for_the_six_month_example(income: str, approved: bool) -> None:
    # SPEC.md: a 516.67 payment needs declared income of at least 1,722.24.
    assert decide("2500.00", "516.67", Decimal(income)).approved is approved


def test_both_reasons_are_reported_when_both_checks_fail() -> None:
    decision = decide("8000.00", "4000.00")

    assert not decision.approved
    assert len(decision.reasons) == 2
