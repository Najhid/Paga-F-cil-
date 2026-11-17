from datetime import date

import src.app as app_module
from src.db import connect
from src.seed import seed


def test_pages_require_sign_in(client) -> None:
    for url in ("/", "/loans", "/loans/1"):
        response = client.get(url)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/login")


def test_wrong_password_is_refused_without_revealing_which_part_failed(client, login) -> None:
    response = login("leon", "not-the-password")

    assert "Wrong username or password." in response.get_data(as_text=True)
    assert client.get("/").status_code == 302


def test_unknown_user_gets_the_same_message(client, login) -> None:
    response = login("nobody", "whatever")

    assert "Wrong username or password." in response.get_data(as_text=True)


def test_post_without_the_csrf_token_is_refused(client, login) -> None:
    login("leon")

    assert client.post("/loans", data={"cart": "2500", "term": "6"}).status_code == 400
    assert client.post("/logout").status_code == 400


def test_sign_out_ends_the_session(client, login, post) -> None:
    login("leon")

    post("/logout")

    assert client.get("/").status_code == 302


def test_passwords_are_stored_hashed(client) -> None:
    connection = connect(app_module.app.config["DATABASE"])
    hashes = [row["password_hash"] for row in connection.execute("SELECT * FROM users")]
    connection.close()

    assert all(value.startswith(("scrypt:", "pbkdf2:")) for value in hashes)
    assert not any("pw-" in value for value in hashes)


def test_cross_user_isolation(client, login, post) -> None:
    login("leon")
    post("/loans", cart="2500", term="6")
    assert client.get("/loans/1").status_code == 200

    post("/logout")
    login("ana")

    assert client.get("/loans/1").status_code == 404
    assert post("/loans/1/installments/1/paid").status_code == 404
    assert post("/loans/1/installments/1/late").status_code == 404
    page = client.get("/loans").get_data(as_text=True)
    assert "/loans/1" not in page
    assert "You have no loans yet" in page


def test_seed_creates_two_users_and_a_defaulted_loan(tmp_path) -> None:
    path = str(tmp_path / "seeded.db")
    today = date(2026, 11, 16)

    assert seed(path, today, {"leon": "x-leon", "ana": "x-ana"})
    assert not seed(path, today, {"leon": "y", "ana": "y"})

    connection = connect(path)
    users = [
        row["username"]
        for row in connection.execute("SELECT username FROM users ORDER BY id")
    ]
    loans_by_user = connection.execute(
        "SELECT u.username, l.status FROM loans l JOIN users u ON u.id = l.user_id "
        "ORDER BY l.id"
    ).fetchall()
    connection.close()

    assert users == ["leon", "ana"]
    assert [(row["username"], row["status"]) for row in loans_by_user] == [
        ("ana", "defaulted"), ("ana", "active"),
    ]
