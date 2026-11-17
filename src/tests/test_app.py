from decimal import Decimal

import src.app as checkout_app


def test_format_mxn_keeps_two_decimals_when_there_are_cents() -> None:
    assert checkout_app.format_mxn(Decimal("516.50")) == "$516.50 MXN"
    assert checkout_app.format_mxn(Decimal("0.50")) == "$0.50 MXN"


def test_format_mxn_drops_decimals_for_whole_amounts() -> None:
    assert checkout_app.format_mxn(Decimal("2800.00")) == "$2,800 MXN"


def test_format_percent_uses_one_decimal() -> None:
    assert checkout_app.format_percent(Decimal("113.33")) == "113.3%"


def test_student_login_serves_branded_local_assets(client) -> None:
    page = client.get("/login")

    assert page.status_code == 200
    assert 'alt="PagaFácil"' in page.get_data(as_text=True)
    assert "/static/app.css" in page.get_data(as_text=True)
    assert client.get("/static/app.css").mimetype == "text/css"
    assert client.get("/static/pagafacil-logo.jpg").mimetype == "image/jpeg"


def test_checkout_shows_every_term_with_costs(client, login) -> None:
    login("leon")

    page = client.get("/").get_data(as_text=True)

    for text in ("3 months", "6 months", "9 months", "12 months", "$3,100 MXN", "$516.67 MXN"):
        assert text in page
    assert "2026-12-16" in page
    assert "Simulated environment" in page


def test_checkout_shows_effective_annual_rate_and_disclaimer(client, login) -> None:
    login("leon")

    page = client.get("/").get_data(as_text=True)

    assert "Effective annual rate (reference)" in page
    assert "113.3%" in page
    assert "not the official CAT" in page


def test_checkout_approves_the_example_cart_for_every_term(client, login) -> None:
    login("leon")

    page = client.get("/").get_data(as_text=True)

    assert page.count("Approved") == 4
    assert "Rejected" not in page


def test_checkout_rejects_a_cart_above_the_credit_limit(client, login) -> None:
    login("leon")

    page = client.get("/?cart=8000").get_data(as_text=True)

    assert page.count("Rejected") == 4
    assert "above the credit limit" in page


def test_checkout_rejects_short_term_payment_above_income_limit(client, login) -> None:
    login("leon")

    page = client.get("/?cart=5000").get_data(as_text=True)

    assert "Declared monthly income: $6,000 MXN" in page
    assert "Maximum monthly payment: $1,800 MXN" in page
    assert "$1,866.67 MXN" in page
    assert page.count("Approved") == 3
    assert "Rejected: Monthly payment is above 30% of declared income" in page


def test_invalid_cart_total_shows_an_error_and_example_cart(client, login) -> None:
    login("leon")

    page = client.get("/?cart=abc").get_data(as_text=True)

    assert "The cart total must be a number." in page
    assert "$2,500 MXN" in page


def test_cart_total_of_zero_or_above_the_maximum_is_refused(client, login) -> None:
    login("leon")

    assert "must be above $0" in client.get("/?cart=0").get_data(as_text=True)
    assert "must be above $0" in client.get("/?cart=1000000").get_data(as_text=True)
    assert "must be a number" in client.get("/?cart=NaN").get_data(as_text=True)
