from datetime import date
from decimal import Decimal

import pytest

import src.app as app_module
from src import loans
from src.db import connect


def take_loan(post, cart: str = "2500", term: str = "6"):
    return post("/loans", cart=cart, term=term)


def test_accepting_a_loan_records_payout_and_schedule(client, login, post) -> None:
    login("leon")

    response = take_loan(post)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/loans/1")
    page = client.get("/loans/1").get_data(as_text=True)
    assert "Merchant fee (4% of the price): $100 MXN" in page
    assert "Simulated payout to the bookstore: $2,400 MXN" in page
    assert "Total to repay: $3,100 MXN" in page
    assert "Balance: <strong>$3,100 MXN</strong>" in page
    assert page.count("Mark as paid") == 6


def test_stored_loan_matches_the_quote(client, login, post) -> None:
    login("leon")
    take_loan(post)

    connection = connect(app_module.app.config["DATABASE"])
    loan = connection.execute("SELECT * FROM loans WHERE id = 1").fetchone()
    amounts = [Decimal(row["amount"]) for row in loans.list_installments(connection, 1)]
    connection.close()

    assert loan["status"] == "active"
    assert (loan["price"], loan["merchant_fee"], loan["funded_amount"]) == (
        "2500.00", "100.00", "2400.00",
    )
    assert sum(amounts) == Decimal(loan["total_to_repay"]) == Decimal("3100.00")


def test_a_rejected_loan_cannot_be_accepted(client, login, post) -> None:
    login("leon")

    assert take_loan(post, cart="8000").status_code == 400
    assert "You have no loans yet" in client.get("/loans").get_data(as_text=True)


def test_invalid_term_or_cart_is_refused(client, login, post) -> None:
    login("leon")

    assert take_loan(post, term="7").status_code == 400
    assert take_loan(post, cart="abc").status_code == 400


def test_marking_installments_paid_lowers_the_balance_until_the_loan_is_paid(
    client, login, post
) -> None:
    login("leon")
    take_loan(post, cart="1200", term="3")

    post("/loans/1/installments/1/paid")
    page = client.get("/loans/1").get_data(as_text=True)
    assert "Balance: <strong>$896 MXN</strong>" in page

    post("/loans/1/installments/2/paid")
    post("/loans/1/installments/3/paid")
    page = client.get("/loans/1").get_data(as_text=True)
    assert "Status: <strong>paid</strong>" in page
    assert "Balance: <strong>$0 MXN</strong>" in page


def test_installment_cannot_be_marked_late_before_its_due_date(
    client, login, post
) -> None:
    login("leon")
    take_loan(post)

    page = client.get("/loans/1").get_data(as_text=True)
    assert "Mark as late" not in page
    assert post("/loans/1/installments/1/late").status_code == 400

    connection = connect(app_module.app.config["DATABASE"])
    status = loans.list_installments(connection, 1)[0]["status"]
    connection.close()
    assert status == "pending"


def test_an_installment_can_be_marked_late_after_its_due_date(
    client, login, post, monkeypatch
) -> None:
    login("leon")
    take_loan(post)
    monkeypatch.setattr(app_module, "get_today", lambda: date(2026, 12, 17))

    page = client.get("/loans/1").get_data(as_text=True)
    assert "Mark as late" in page
    assert post("/loans/1/installments/1/late").status_code == 302

    connection = connect(app_module.app.config["DATABASE"])
    status = loans.list_installments(connection, 1)[0]["status"]
    connection.close()
    assert status == "late"


def test_default_starts_only_after_45_days_past_due(client, login, post) -> None:
    login("leon")
    take_loan(post)
    connection = connect(app_module.app.config["DATABASE"])
    due = date.fromisoformat(loans.list_installments(connection, 1)[0]["due_date"])

    loans.refresh_statuses(connection, 1, date.fromordinal(due.toordinal() + 45))
    assert loans.list_installments(connection, 1)[0]["status"] == "late"
    assert connection.execute("SELECT status FROM loans").fetchone()["status"] == "active"

    loans.refresh_statuses(connection, 1, date.fromordinal(due.toordinal() + 46))
    assert loans.list_installments(connection, 1)[0]["status"] == "defaulted"
    assert connection.execute("SELECT status FROM loans").fetchone()["status"] == "defaulted"
    connection.close()


def test_overdue_installment_becomes_defaulted_before_payment_is_allowed(
    client, login, post, monkeypatch
) -> None:
    login("leon")
    take_loan(post)
    monkeypatch.setattr(app_module, "get_today", lambda: date(2027, 2, 1))

    assert post("/loans/1/installments/1/paid").status_code == 400

    connection = connect(app_module.app.config["DATABASE"])
    installment = loans.list_installments(connection, 1)[0]
    loan_status = connection.execute("SELECT status FROM loans WHERE id = 1").fetchone()["status"]
    connection.close()
    assert installment["status"] == "defaulted"
    assert loan_status == "defaulted"


def test_unknown_action_or_installment_is_refused(client, login, post) -> None:
    login("leon")
    take_loan(post)

    assert post("/loans/1/installments/1/refund").status_code == 400
    assert post("/loans/1/installments/99/paid").status_code == 404


def test_loans_list_shows_the_balance(client, login, post) -> None:
    login("leon")
    take_loan(post)

    page = client.get("/loans").get_data(as_text=True)

    assert "/loans/1" in page
    assert "$3,100 MXN" in page


@pytest.mark.parametrize("cart", ["2500.005", "2500.5"])
def test_cart_totals_are_rounded_to_cents(client, login, post, cart: str) -> None:
    login("leon")

    assert take_loan(post, cart=cart).status_code == 302
