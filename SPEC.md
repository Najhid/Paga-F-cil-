[SPEC.md](https://github.com/user-attachments/files/34494239/SPEC.md)

# SPEC: PagaFácil

Last updated: 2026-11-06 · Owners: Angel Najhid Flores Cartagena + Luciano Yitani Chapa

## Problem
University students in Mexico often have no credit card and a thin credit history, so they
cannot split a large one-off purchase (textbooks and school supplies at the start of the
semester) into payments. Today they either pay all at once, borrow from family, or use
informal credit. PagaFácil is a Buy Now, Pay Later (BNPL) lender: it pays the merchant
and the student repays PagaFácil in monthly installments with interest.

## User
León Lara, 21, a university student who has just started working part-time, has no credit
card and no credit history. He needs to buy textbooks and supplies at the campus bookstore
at the start of the semester and can only afford them in 3 to 12 monthly payments.

## Core flow (the MVP)
The single flow that must work end to end at Demo Day:

1. León checks out at the campus bookstore (single fake merchant) with a cart total and
   chooses a term: 3, 6, 9 or 12 months.
2. The app shows the full cost before he accepts: interest, total to repay, installment
   amount and schedule.
3. A simple rule-based check approves or rejects the loan (requested amount within his
   credit limit; installment within the max share of his declared income).
4. If approved, the app records the payout to the merchant (price minus the 4% merchant
   fee) and creates the installment schedule; León can mark an installment as paid or late
   and see his updated balance.

## Data model (plain words)
User has Loans; Merchant has Loans; each Loan has Installments.
- **User:** name, declared monthly income, credit limit (all invented).
- **Merchant:** name, merchant fee rate (4%).
- **Loan:** user, merchant, price, term in months, merchant fee, funded amount (price minus
  fee), total interest, total to repay, status (approved / active / paid / defaulted).
- **Installment:** loan, number, due date, amount, status (pending / paid / late), paid date.

Pricing rule: flat interest of 4% per month of term on the original price (3 months = 12%,
6 = 24%, 9 = 36%, 12 = 48%).

## Dependencies (closed list)
Anything not on this list needs both partners plus a bitacora entry.

- Python 3 standard library (includes SQLite)
- Flask
- pytest

## Out of scope this semester
- Real payments, real KYC, real credit bureau queries
- Native mobile app; more than one user role or more than one merchant
- Late fees and collections process (default is modeled only as an assumption)
- Savings, deposits, yield or investment features (PagaFácil never holds client money)
- Real regulatory registration (SOFOM E.N.R. is analyzed, not implemented)

## Unit economics the model must show
All values are our own assumptions and must be computed from the data model
(`economics.py`), not typed in by hand.

Assumptions: average ticket $2,500 MXN; merchant fee 4%; cost of funds 10% annual; default
rate 5% of loan amount; servicing and credit-check cost $40 per loan; CAC $180; 3 loans per
customer over their university life; year-1 fixed costs about $120,000 (legal and
incorporation, PLD/AML compliance, other; TODO-verify with a fintech lawyer).

Contribution per loan = interest + merchant fee − cost of funds − expected default loss −
servicing cost. Base case is the 6-month plan:

| Term | Total interest | Effective annual rate (approx.) | Contribution per loan |
|---|---|---|---|
| 3 months | 12% | ~98% | ~$193 |
| 6 months | 24% | ~113% | ~$462 |
| 9 months | 36% | ~116% | ~$731 |
| 12 months | 48% | ~116% | ~$1,000 |

- LTV (6-month base) = $462 × 3 loans ≈ $1,390; LTV ÷ CAC ≈ 7.7x.
- Payback: CAC is recovered within the first loan for every term (first loan contributes
  $193 to $1,000 vs CAC $180; the 3-month plan is the tightest case).
- Break-even: about 260 loans per year in the 6-month base case (about 130 customers at 2
  loans per year). Worst case, if every customer chose the 3-month plan: about 620 loans
  per year (about 310 customers at 2 loans per year).
- Open decision: keep or drop the 3-month plan (it now recovers CAC but is still the
  lowest margin).
- Risk: the 5% default rate is an assumption that may rise with higher prices
  (TODO-verify with a sensitivity test in `economics.py`).
- Effective annual rate is the cost to the user and must be shown to them as CAT.
  TODO-verify the CAT calculation and disclosure rules with Condusef.

## Regulatory notes (all TODO-verify)
- Vehicle considered: SOFOM E.N.R. TODO-verify registration authority, timeline (3 to 4
  months) and cost range ($40,000 to $80,000 MXN).
- AML/PLD compliance cost ($20,000 to $40,000 MXN per year). TODO-verify.

## Changelog
| Date | Change | Why | Approved by |
|---|---|---|---|
| 2026-11-03 | Initial SPEC drafted | Project restarted with corrected unit economics | 2026-11-04|
| 2026-11-06 | Flat interest raised from 2% to 4% per month of term; economics table, LTV, payback and break-even recomputed | Every term must recover CAC in the first loan and lower the break-even volume | 2026-11-06 |
