from decimal import Decimal

# All values below are our own assumptions (see SPEC.md and DECISIONS.md), not market data.

# Flat interest charged per month of term, on the ORIGINAL price (not on the remaining
# balance). Total interest = price x rate x term in months (3 months = 12%, 12 months = 48%).
# Raised from 2% to 4% on 2026-11-06 so every term recovers CAC in the first loan.
MONTHLY_INTEREST_RATE = Decimal("0.04")

# Share of each sale that the merchant pays us. We advance price minus this fee to the
# merchant, so it is a second revenue stream next to interest (SPEC.md, DECISIONS.md).
MERCHANT_FEE_RATE = Decimal("0.04")

# Terms offered at checkout, in months (SPEC.md core flow).
TERMS_MONTHS = (3, 6, 9, 12)

# Sample cart for the demo, in MXN. $2,500 is our assumed average bookstore ticket and has
# not been validated against real bookstore prices yet.
EXAMPLE_CART_TOTAL = Decimal("2500.00")

# León's declared monthly income in MXN. Invented for the demo (SPEC.md data model).
DECLARED_MONTHLY_INCOME = Decimal("12000.00")

# Initial credit limit in MXN: the largest cart total we approve (SPEC.md approval rule).
CREDIT_LIMIT = Decimal("6500.00")

# Largest share of declared monthly income that one monthly installment may take.
# The credit limit and this share are product-design assumptions, not regulatory limits.
MAX_INSTALLMENT_SHARE_OF_INCOME = Decimal("0.30")
