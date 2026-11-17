import sqlite3

# Amounts are stored as text so that Decimal values never pass through binary floats.
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    declared_monthly_income TEXT NOT NULL,
    credit_limit TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS merchants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    fee_rate TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS loans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    merchant_id INTEGER NOT NULL REFERENCES merchants(id),
    price TEXT NOT NULL,
    term_months INTEGER NOT NULL,
    merchant_fee TEXT NOT NULL,
    funded_amount TEXT NOT NULL,
    total_interest TEXT NOT NULL,
    total_to_repay TEXT NOT NULL,
    status TEXT NOT NULL,
    created_on TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS installments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    loan_id INTEGER NOT NULL REFERENCES loans(id),
    number INTEGER NOT NULL,
    due_date TEXT NOT NULL,
    amount TEXT NOT NULL,
    status TEXT NOT NULL,
    paid_date TEXT,
    UNIQUE (loan_id, number)
);
"""


def connect(path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()
