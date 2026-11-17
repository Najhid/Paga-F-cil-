"""Create invented demo data with ``python -m src.seed``.

Passwords come from LEON_PASSWORD and ANA_PASSWORD, or are generated randomly and printed
once. They are never stored in the repository. To reset the demo, remove its database file
and run the seed script again.
"""

import os
import secrets
from datetime import date, timedelta
from decimal import Decimal

from werkzeug.security import generate_password_hash

from src import loans
from src.config import CREDIT_LIMIT, DECLARED_MONTHLY_INCOME, MERCHANT_FEE_RATE
from src.db import connect, init_db


def seed(path: str, today: date, passwords: dict[str, str]) -> bool:
    """Create test records once; return False if users already exist."""
    connection = connect(path)
    init_db(connection)
    if connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        connection.close()
        return False

    connection.execute(
        "INSERT INTO merchants (name, fee_rate) VALUES (?, ?)",
        ("Campus Bookstore (invented)", str(MERCHANT_FEE_RATE)),
    )
    merchant_id = connection.execute("SELECT id FROM merchants").fetchone()["id"]

    students = (
        ("leon", "León Lara", DECLARED_MONTHLY_INCOME),
        ("ana", "Ana Mora", Decimal("8000.00")),
    )
    user_ids = {}
    for username, display_name, income in students:
        cursor = connection.execute(
            "INSERT INTO users (username, display_name, password_hash, "
            "declared_monthly_income, credit_limit) VALUES (?, ?, ?, ?, ?)",
            (
                username,
                display_name,
                generate_password_hash(passwords[username]),
                str(income),
                str(CREDIT_LIMIT),
            ),
        )
        user_ids[username] = cursor.lastrowid
    connection.commit()

    # Ana's seeded history demonstrates default without waiting; León remains ready for checkout.
    old_loan = loans.create_loan(
        connection, user_ids["ana"], merchant_id, Decimal("3000.00"), 6,
        today - timedelta(days=130),
    )
    first_due = connection.execute(
        "SELECT due_date FROM installments WHERE loan_id = ? AND number = 1", (old_loan,)
    ).fetchone()["due_date"]
    connection.execute(
        "UPDATE installments SET status = 'paid', paid_date = ? "
        "WHERE loan_id = ? AND number = 1",
        (first_due, old_loan),
    )
    connection.commit()
    loans.refresh_statuses(connection, old_loan, today)

    recent_loan = loans.create_loan(
        connection, user_ids["ana"], merchant_id, Decimal("1200.00"), 3,
        today - timedelta(days=20),
    )
    loans.refresh_statuses(connection, recent_loan, today)
    connection.close()
    return True


def main() -> None:
    path = os.environ.get("PAGAFACIL_DB", "pagafacil.db")
    passwords = {
        "leon": os.environ.get("LEON_PASSWORD") or secrets.token_urlsafe(9),
        "ana": os.environ.get("ANA_PASSWORD") or secrets.token_urlsafe(9),
    }
    if seed(path, date.today(), passwords):
        print("Invented test data created. Test accounts (copy into the Blackboard")
        print("submission, never into the repository):")
        for username, password in passwords.items():
            print(f"  username: {username}   password: {password}")
    else:
        print("The database already has users. Remove the demo database to start over.")


if __name__ == "__main__":
    main()
