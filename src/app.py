import os
import secrets
import sqlite3
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from src import loans
from src.approval import decide_loan
from src.config import EXAMPLE_CART_TOTAL, MAX_INSTALLMENT_SHARE_OF_INCOME, TERMS_MONTHS
from src.db import connect, init_db
from src.pricing import CENT, calculate_quote

MAX_CART_TOTAL = Decimal("100000.00")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["DATABASE"] = os.environ.get("PAGAFACIL_DB", "pagafacil.db")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_today() -> date:
    return date.today()


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = connect(app.config["DATABASE"])
        init_db(g.db)
    return g.db


@app.teardown_appcontext
def close_db(_error: BaseException | None) -> None:
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


app.jinja_env.globals["csrf_token"] = csrf_token


@app.before_request
def check_csrf() -> None:
    if request.method == "POST":
        sent = request.form.get("csrf_token", "")
        if not secrets.compare_digest(sent, session.get("csrf", "")):
            abort(400)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        user = get_db().execute(
            "SELECT * FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
        if user is None:
            session.clear()
            return redirect(url_for("login"))
        g.user = user
        return view(*args, **kwargs)

    return wrapped


@app.template_filter("mxn")
def format_mxn(amount: Decimal) -> str:
    formatted = f"{amount:,.2f}"
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    return f"${formatted} MXN"


@app.template_filter("pct")
def format_percent(value: Decimal) -> str:
    return f"{value:,.1f}%"


def parse_cart(raw: str | None) -> tuple[Decimal, str | None]:
    """Parse a checkout amount, returning a visible error for invalid input."""
    if not raw:
        return EXAMPLE_CART_TOTAL, None
    try:
        value = Decimal(raw).quantize(CENT)
        if not value.is_finite():
            raise InvalidOperation
    except (InvalidOperation, ValueError):
        return EXAMPLE_CART_TOTAL, "The cart total must be a number."
    if value <= 0 or value > MAX_CART_TOTAL:
        return EXAMPLE_CART_TOTAL, "The cart total must be above $0 and at most $100,000 MXN."
    return value, None


def build_offers(user: sqlite3.Row, cart_total: Decimal, checkout_date: date):
    """Quote every term and apply the approval rule using this user's own data."""
    income = Decimal(user["declared_monthly_income"])
    limit = Decimal(user["credit_limit"])
    offers = []
    for term_months in TERMS_MONTHS:
        quote = calculate_quote(cart_total, term_months, checkout_date)
        decision = decide_loan(
            cart_total, quote.monthly_payment, income, limit, MAX_INSTALLMENT_SHARE_OF_INCOME
        )
        offers.append((quote, decision))
    return offers


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user is not None and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            csrf_token()
            return redirect(url_for("checkout"))
        error = "Wrong username or password."
    return render_template("login.html", error=error)


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.get("/")
@login_required
def checkout():
    cart_total, cart_error = parse_cart(request.args.get("cart"))
    offers = build_offers(g.user, cart_total, get_today())
    income = Decimal(g.user["declared_monthly_income"])
    return render_template(
        "checkout.html",
        user=g.user,
        cart_total=cart_total,
        cart_error=cart_error,
        offers=offers,
        declared_income=income,
        credit_limit=Decimal(g.user["credit_limit"]),
        max_monthly_payment=income * MAX_INSTALLMENT_SHARE_OF_INCOME,
    )


@app.post("/loans")
@login_required
def accept_loan():
    cart_total, cart_error = parse_cart(request.form.get("cart"))
    term_months = request.form.get("term", type=int)
    if cart_error or term_months not in TERMS_MONTHS:
        abort(400)

    # Recompute the quote and approval on the server; do not trust browser-submitted amounts.
    matching_offer = next(
        (
            decision
            for quote, decision in build_offers(g.user, cart_total, get_today())
            if quote.term_months == term_months
        ),
        None,
    )
    if matching_offer is None or not matching_offer.approved:
        abort(400)

    db = get_db()
    merchant = db.execute("SELECT id FROM merchants ORDER BY id LIMIT 1").fetchone()
    if merchant is None:
        abort(503, "Demo merchant data is not initialized. Run python -m src.seed.")
    loan_id = loans.create_loan(
        db, g.user["id"], merchant["id"], cart_total, term_months, get_today()
    )
    return redirect(url_for("loan_detail", loan_id=loan_id))


def loan_summary(loan: sqlite3.Row) -> dict:
    return {
        "id": loan["id"],
        "price": Decimal(loan["price"]),
        "term_months": loan["term_months"],
        "total_to_repay": Decimal(loan["total_to_repay"]),
        "status": loan["status"],
        "created_on": loan["created_on"],
        "balance": loans.balance(get_db(), loan["id"]),
    }


@app.get("/loans")
@login_required
def my_loans():
    db = get_db()
    rows = db.execute(
        "SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)
    ).fetchall()
    for row in rows:
        loans.refresh_statuses(db, row["id"], get_today())
    rows = db.execute(
        "SELECT * FROM loans WHERE user_id = ? ORDER BY id DESC", (g.user["id"],)
    ).fetchall()
    return render_template("loans.html", user=g.user, loans=[loan_summary(row) for row in rows])


def own_loan_or_404(loan_id: int) -> sqlite3.Row:
    loan = loans.get_loan_for_user(get_db(), loan_id, g.user["id"])
    if loan is None:
        abort(404)
    return loan


@app.get("/loans/<int:loan_id>")
@login_required
def loan_detail(loan_id: int):
    own_loan_or_404(loan_id)
    db = get_db()
    today = get_today()
    loans.refresh_statuses(db, loan_id, today)
    loan = own_loan_or_404(loan_id)
    return render_template(
        "loan.html",
        user=g.user,
        loan=loan,
        today=today,
        summary=loan_summary(loan),
        merchant_fee=Decimal(loan["merchant_fee"]),
        funded_amount=Decimal(loan["funded_amount"]),
        total_interest=Decimal(loan["total_interest"]),
        installments=[
            {
                "number": row["number"],
                "due_date": row["due_date"],
                "amount": Decimal(row["amount"]),
                "status": row["status"],
                "paid_date": row["paid_date"],
            }
            for row in loans.list_installments(db, loan_id)
        ],
    )


@app.post("/loans/<int:loan_id>/installments/<int:number>/<action>")
@login_required
def update_installment(loan_id: int, number: int, action: str):
    own_loan_or_404(loan_id)
    try:
        loans.mark_installment(get_db(), loan_id, number, action, get_today())
    except LookupError:
        abort(404)
    except ValueError:
        abort(400)
    return redirect(url_for("loan_detail", loan_id=loan_id))


if __name__ == "__main__":
    app.run()
