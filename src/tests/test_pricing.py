from datetime import date
from decimal import Decimal

import pytest

from src.pricing import add_months, calculate_quote


@pytest.mark.parametrize(
    ("term_months", "interest", "total_repayment", "monthly_payment"),
    [
        (3, "300.00", "2800.00", "933.33"),
        (6, "600.00", "3100.00", "516.67"),
        (9, "900.00", "3400.00", "377.78"),
        (12, "1200.00", "3700.00", "308.33"),
    ],
)
def test_calculate_quote_for_example_cart(
    term_months: int,
    interest: str,
    total_repayment: str,
    monthly_payment: str,
) -> None:
    quote = calculate_quote(Decimal("2500.00"), term_months, date(2026, 1, 15))

    assert quote.interest == Decimal(interest)
    assert quote.total_repayment == Decimal(total_repayment)
    assert quote.monthly_payment == Decimal(monthly_payment)
    assert sum(
        (installment.amount for installment in quote.installments), Decimal("0")
    ) == quote.total_repayment
    assert len(quote.installments) == term_months


@pytest.mark.parametrize(
    ("checkout_date", "months", "expected_due_date"),
    [
        (date(2026, 1, 31), 1, date(2026, 2, 28)),
        (date(2024, 1, 31), 1, date(2024, 2, 29)),
        (date(2026, 1, 31), 2, date(2026, 3, 31)),
    ],
)
def test_add_months_clamps_to_last_day_when_needed(
    checkout_date: date, months: int, expected_due_date: date
) -> None:
    assert add_months(checkout_date, months) == expected_due_date


@pytest.mark.parametrize("cart_total", [Decimal("0"), Decimal("-1"), Decimal("NaN")])
def test_calculate_quote_rejects_invalid_cart_total(cart_total: Decimal) -> None:
    with pytest.raises(ValueError, match="finite amount greater than zero"):
        calculate_quote(cart_total, 3, date(2026, 1, 15))


@pytest.mark.parametrize("term_months", [0, 1, 4, 24])
def test_calculate_quote_rejects_unsupported_term(term_months: int) -> None:
    with pytest.raises(ValueError, match="Term must be one of"):
        calculate_quote(Decimal("2500.00"), term_months, date(2026, 1, 15))
