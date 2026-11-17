from datetime import date

import pytest
from werkzeug.security import generate_password_hash

import src.app as app_module
from src.config import DECLARED_MONTHLY_INCOME
from src.db import connect, init_db

TODAY = date(2026, 11, 16)


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = str(tmp_path / "test.db")
    app_module.app.config.update(DATABASE=path, TESTING=True)
    monkeypatch.setattr(app_module, "get_today", lambda: TODAY)
    connection = connect(path)
    init_db(connection)
    connection.execute(
        "INSERT INTO merchants (name, fee_rate) VALUES ('Campus Bookstore', '0.04')"
    )
    for username, name, income in (
        ("leon", "León Lara", str(DECLARED_MONTHLY_INCOME)),
        ("ana", "Ana Mora", "8000.00"),
    ):
        connection.execute(
            "INSERT INTO users (username, display_name, password_hash, "
            "declared_monthly_income, credit_limit) VALUES (?, ?, ?, ?, '6500.00')",
            (username, name, generate_password_hash(f"pw-{username}"), income),
        )
    connection.commit()
    connection.close()
    return app_module.app.test_client()


@pytest.fixture
def login(client):
    def _login(username: str, password: str | None = None):
        with client.session_transaction() as session:
            session["csrf"] = "test-token"
        return client.post(
            "/login",
            data={
                "username": username,
                "password": password if password is not None else f"pw-{username}",
                "csrf_token": "test-token",
            },
        )

    return _login


@pytest.fixture
def post(client):
    def _post(url: str, **data):
        with client.session_transaction() as session:
            token = session.get("csrf", "")
        return client.post(url, data={"csrf_token": token, **data})

    return _post
