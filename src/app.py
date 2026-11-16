from datetime import date
from decimal import Decimal

from flask import Flask, render_template

from src.approval import decide_loan
from src.config import (
    CREDIT_LIMIT,
    DECLARED_MONTHLY_INCOME,
    EXAMPLE_CART_TOTAL,
    MAX_INSTALLMENT_SHARE_OF_INCOME,
    TERMS_MONTHS,
)
from src.pricing import calculate_quote


app = Flask(__name__)


@app.template_filter("mxn")
def format_mxn(amount: Decimal) -> str:
    formatted = f"{amount:,.2f}"
    if formatted.endswith(".00"):
        formatted = formatted[:-3]
    return f"${formatted} MXN"


@app.template_filter("pct")
def format_percent(value: Decimal) -> str:
    return f"{value:,.1f}%"


@app.get("/")
def checkout():
    checkout_date = date.today()
    quotes = [
        calculate_quote(EXAMPLE_CART_TOTAL, term_months, checkout_date)
        for term_months in TERMS_MONTHS
    ]
    decisions = {
        quote.term_months: decide_loan(EXAMPLE_CART_TOTAL, quote.monthly_payment)
        for quote in quotes
    }
    return render_template(
        "checkout.html",
        cart_total=EXAMPLE_CART_TOTAL,
        quotes=quotes,
        decisions=decisions,
        declared_income=DECLARED_MONTHLY_INCOME,
        credit_limit=CREDIT_LIMIT,
        max_monthly_payment=DECLARED_MONTHLY_INCOME * MAX_INSTALLMENT_SHARE_OF_INCOME,
    )


if __name__ == "__main__":
    app.run()
