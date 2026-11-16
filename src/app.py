from datetime import date
from decimal import Decimal

from flask import Flask, render_template

from src.config import EXAMPLE_CART_TOTAL, TERMS_MONTHS
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
    return render_template(
        "checkout.html",
        cart_total=EXAMPLE_CART_TOTAL,
        quotes=quotes,
    )


if __name__ == "__main__":
    app.run()
