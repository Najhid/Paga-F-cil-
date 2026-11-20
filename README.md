# PagaFácil

A Buy Now, Pay Later (BNPL) prototype for university students in Mexico, designed around a
fintech-bank partnership. The demo simulates merchant payout and installment tracking;
the bank partner's role in lending, funding, receivable ownership, revenue and losses is
not represented as a real contract.
We never hold client money and never pay yield.

Course: FIN506 Financial Technology · Universidad Panamericana · Fall 2026

Team: Angel Najhid Flores Cartagena · Luciano Yitani Chapa

> **Prototype only.** All users, merchants and transactions are invented. There are no real
> payments, no real credit checks and no real personal data.

Hosted test environment: [https://najhid21.pythonanywhere.com](https://najhid21.pythonanywhere.com)

The free PythonAnywhere site must be renewed by signing in at least once a month and
selecting **Run until 1 month from today** on the Web tab. PythonAnywhere currently shows
the next disable date in the web app settings.

## What the demo shows

1. A student signs in to a student-facing account, checks out at the campus bookstore and chooses 3, 6, 9 or 12 months. The demo uses León's invented account.
2. The app shows interest, total repayment, installments, schedule and an effective annual
   rate as a reference figure, not the official CAT.
3. A server-side rule-based check automatically approves or rejects the student's offer based
   on the credit limit and monthly-income share; there is no staff approval screen or admin role.
4. Once accepted, the app records the simulated merchant payout and installment schedule.
   The student can mark installments paid or late and see the remaining balance.
5. Unpaid installments become late after their due date, and defaulted after more than 45
   calendar days past due.

The interface uses the PagaFácil logo and a responsive student-facing layout for sign-in,
checkout quotes and installment tracking. Approval and payment status remain simulated.

## Run locally

Requirements: Python 3.11 or newer.

From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.seed
python -m src.app
```

Open the local URL printed by Flask. If port 5000 is busy (for example, by macOS AirPlay),
run `flask --app src.app run --port 5001`.

The seed command creates `pagafacil.db` with invented users, merchant and sample history.
It prints each test password once. Store those credentials in the Blackboard submission,
never in this repository. To start over, remove the local database file and run the seed
command again.

Optional environment variables:

- `SECRET_KEY`: stable signing key for the session cookie. If unset, a random key is
  generated on each app start.
- `PAGAFACIL_DB`: database file path. Defaults to `pagafacil.db`.
- `LEON_PASSWORD` and `ANA_PASSWORD`: set test-account passwords during seeding. If unset,
  random passwords are generated and printed once.

## Test accounts and demo

- `leon`: León Lara, no loans initially. Use him to accept a loan and track payments.
- `ana`: Ana Mora, with a defaulted loan and a recent loan to demonstrate history.

Try this flow:

1. Sign in as `leon`. The example $2,500 cart shows all four terms.
2. Accept six months. The app records a $2,400 simulated payout after the $100 merchant fee,
   along with six installments and the balance.
3. Mark an installment paid or, after its due date, late to see the balance or status update.
4. Enter a $5,000 cart. The three-month plan is rejected because its $1,866.67 monthly
   payment exceeds 30% of León's assumed $6,000 income; the longer plans are approved.
5. Enter a cart over $6,500 to show rejection by the credit limit.
6. Sign in as `ana` to see the seeded defaulted loan.
7. While signed in as `leon`, try opening Ana's loan. The app returns 404.

## Simulated services and security

- The merchant payout is a database record; no money moves.
- Credit approval uses the project's own rules; no credit bureau is queried.
- Payments are marked manually; no payment processor or bank is used.
- No KYC or identity verification is performed; all data is invented.
- Passwords are stored as hashes. Loan pages and payment actions are limited to the signed-in
  user's loans. Forms use CSRF tokens, and amounts are recalculated on the server.
- No credentials or secret keys are stored in the repository.

## Tests

With the virtual environment active, run:

```sh
python -m pytest
```

The test suite evaluates the financial-model workbook formulas and checks scheduled cash
collections. Valuation outputs remain blank until PagaFácil's bank-partner revenue and
cost allocation and the required financing structure are defined. Earlier valuation
outputs were illustrative only and are superseded.

The prior 60% debt / 40% equity split and SOFOM-specific fees have been superseded for the
bank-partner scenario. Loan-level contribution is shown only as a portfolio illustration.
PagaFácil standalone revenue, funding cost, credit-loss allocation, partner charges,
EBITDA, break-even and valuation require the bank agreement and related quotes; they are
not inferred from Kueski's consumer APR or public benchmark rates.
In the workbook, the `Bank Partner Economics` sheet holds these evidence-gated inputs, and
the company `P&L` calculates only from them. Blank inputs mean unknown, not zero.

The market inputs are finalized for this delivery as follows: Data México reports 14,693
matriculated students for Universidad Panamericana overall in 2022, while 6,763 is associated
with Zacatecas / Benito Juárez and not with UP CDMX. Neither number is used as a verified
UP CDMX population or market ceiling. The workbook retains 14,693 only for an institution-
wide 100%-adoption context scenario, not as TAM, SAM or demand.

The transaction range is a planning range, not a measured average: MXN 2,500 is the central
P&L ticket and MXN 2,500–4,000 is the sensitivity range. The 25 student interviews support
this range as a product-design hypothesis. Public Kueski/Amazon prices do not replace
measured bookstore or campus spending.

The project used 25 real student questionnaires: 13 Finance and 12 Law students in 3rd to
5th semester. The sample is a convenience sample and supports product hypotheses, not
full-population demand. It reported 48% without own formal credit history, 88% willing to
allow a Buró consultation, 76% willing to accept transparent interest, and 92% preferring
3-month or 6-month terms.

The workbook formulas are evaluated in memory; open the file in Excel to refresh displayed
cached values.

## Project files

- `SPEC.md`: scope, core flow, data model and unit economics; source of truth
- `AGENTS.md`: project rules for AI assistance
- `DECISIONS.md`: design decisions and rationale
- `BITACORA.md`: work and review log
- `PROJECT_METHOD.md`: course method
