from datetime import date

from decimal import Decimal
def test_format_mxn_keeps_two_decimals_when_there_are_cents():
    assert checkout_app.format_mxn(Decimal("516.50")) == "$516.50 MXN"
    assert checkout_app.format_mxn(Decimal("0.50")) == "$0.50 MXN"


def test_format_mxn_drops_decimals_for_whole_amounts():
    assert checkout_app.format_mxn(Decimal("2800.00")) == "$2,800 MXN"

import src.app as checkout_app
from pytest import MonkeyPatch


def test_checkout_displays_all_example_quotes(monkeypatch: MonkeyPatch) -> None:
    class FixedDate(date):
        @classmethod
        def today(cls) -> date:
            return cls(2026, 1, 31)

    monkeypatch.setattr(checkout_app, "date", FixedDate)
    response = checkout_app.app.test_client().get("/")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Example bookstore cart: $2,500 MXN" in page
    assert "3 months" in page
    assert "$300 MXN" in page
    assert "$2,800 MXN" in page
    assert "$933.33 MXN" in page
    assert "6 months" in page
    assert "$600 MXN" in page
    assert "$3,100 MXN" in page
    assert "$516.67 MXN" in page
    assert "9 months" in page
    assert "$900 MXN" in page
    assert "$3,400 MXN" in page
    assert "$377.78 MXN" in page
    assert "12 months" in page
    assert "$1,200 MXN" in page
    assert "$3,700 MXN" in page
    assert "$308.33 MXN" in page
    assert "2026-02-28" in page
    assert "2026-03-31" in page
    assert "2026-04-30" in page
    assert "final installment is adjusted for rounding" in page


def test_checkout_shows_effective_annual_rate_and_disclaimer() -> None:
    response = checkout_app.app.test_client().get("/")
    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Effective annual rate (reference)" in page
    assert "113.3%" in page
    assert "not the official CAT" in page


def test_format_percent_uses_one_decimal() -> None:
    assert checkout_app.format_percent(Decimal("113.33")) == "113.3%"
