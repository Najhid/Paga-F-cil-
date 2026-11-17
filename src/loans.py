import sqlite3
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from src.pricing import CENT, calculate_quote

# An installment becomes defaulted only after it is more than 45 days past due.
DEFAULT_AFTER_DAYS = 45


def create_loan(
    connection: sqlite3.Connection,
    user_id: int,
    merchant_id: int,
    cart_total: Decimal,
    term_months: int,
    created_on: date,
) -> int:
    """Record an approved loan, simulated merchant payout and installment schedule.

    The merchant fee is price times the merchant fee rate, and the simulated payout is
    price minus that fee. This is the SPEC's payout model; no money actually moves.
    """
    merchant = connection.execute(
        "SELECT fee_rate FROM merchants WHERE id = ?", (merchant_id,)
    ).fetchone()
    if merchant is None:
        raise LookupError("Merchant not found.")

    quote = calculate_quote(cart_total, term_months, created_on)
    fee_rate = Decimal(merchant["fee_rate"])
    merchant_fee = (cart_total * fee_rate).quantize(CENT, rounding=ROUND_HALF_UP)
    funded_amount = cart_total - merchant_fee

    cursor = connection.execute(
        "INSERT INTO loans (user_id, merchant_id, price, term_months, merchant_fee, "
        "funded_amount, total_interest, total_to_repay, status, created_on) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)",
        (
            user_id,
            merchant_id,
            str(cart_total),
            term_months,
            str(merchant_fee),
            str(funded_amount),
            str(quote.interest),
            str(quote.total_repayment),
            created_on.isoformat(),
        ),
    )
    loan_id = int(cursor.lastrowid)
    connection.executemany(
        "INSERT INTO installments (loan_id, number, due_date, amount, status) "
        "VALUES (?, ?, ?, ?, 'pending')",
        [
            (loan_id, item.number, item.due_date.isoformat(), str(item.amount))
            for item in quote.installments
        ],
    )
    connection.commit()
    return loan_id


def refresh_statuses(connection: sqlite3.Connection, loan_id: int, today: date) -> None:
    """Apply the late and default rules from SPEC.md and update the loan status."""
    rows = connection.execute(
        "SELECT number, due_date, status FROM installments WHERE loan_id = ?", (loan_id,)
    ).fetchall()
    for row in rows:
        days_past_due = (today - date.fromisoformat(row["due_date"])).days
        status = row["status"]
        new_status = status
        if status in ("pending", "late"):
            if days_past_due > DEFAULT_AFTER_DAYS:
                new_status = "defaulted"
            elif status == "pending" and days_past_due > 0:
                new_status = "late"
        if new_status != status:
            connection.execute(
                "UPDATE installments SET status = ? WHERE loan_id = ? AND number = ?",
                (new_status, loan_id, row["number"]),
            )

    statuses = [
        row["status"]
        for row in connection.execute(
            "SELECT status FROM installments WHERE loan_id = ?", (loan_id,)
        )
    ]
    if "defaulted" in statuses:
        loan_status = "defaulted"
    elif all(status == "paid" for status in statuses):
        loan_status = "paid"
    else:
        loan_status = "active"
    connection.execute("UPDATE loans SET status = ? WHERE id = ?", (loan_status, loan_id))
    connection.commit()


def mark_installment(
    connection: sqlite3.Connection, loan_id: int, number: int, action: str, today: date
) -> None:
    """Mark one installment as paid or late, applying any date-based transitions first."""
    refresh_statuses(connection, loan_id, today)
    row = connection.execute(
        "SELECT status, due_date FROM installments WHERE loan_id = ? AND number = ?",
        (loan_id, number),
    ).fetchone()
    if row is None:
        raise LookupError("Installment not found.")
    status = row["status"]
    if status in ("paid", "defaulted"):
        raise ValueError(f"A {status} installment cannot be changed.")
    if action == "paid":
        connection.execute(
            "UPDATE installments SET status = 'paid', paid_date = ? "
            "WHERE loan_id = ? AND number = ?",
            (today.isoformat(), loan_id, number),
        )
    elif action == "late":
        if status == "late":
            return
        if status != "pending":
            raise ValueError("Only a pending installment can be marked late.")
        if today <= date.fromisoformat(row["due_date"]):
            raise ValueError("An installment cannot be late before its due date.")
        connection.execute(
            "UPDATE installments SET status = 'late' WHERE loan_id = ? AND number = ?",
            (loan_id, number),
        )
    else:
        raise ValueError("Action must be paid or late.")
    connection.commit()
    refresh_statuses(connection, loan_id, today)


def get_loan_for_user(
    connection: sqlite3.Connection, loan_id: int, user_id: int
) -> sqlite3.Row | None:
    """Return a loan only if it belongs to the signed-in user."""
    return connection.execute(
        "SELECT * FROM loans WHERE id = ? AND user_id = ?", (loan_id, user_id)
    ).fetchone()


def list_installments(connection: sqlite3.Connection, loan_id: int) -> list[sqlite3.Row]:
    return connection.execute(
        "SELECT * FROM installments WHERE loan_id = ? ORDER BY number", (loan_id,)
    ).fetchall()


def balance(connection: sqlite3.Connection, loan_id: int) -> Decimal:
    """Sum unpaid installments to calculate the remaining amount owed."""
    return sum(
        (
            Decimal(row["amount"])
            for row in list_installments(connection, loan_id)
            if row["status"] != "paid"
        ),
        Decimal("0"),
    )
