from datetime import date

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
