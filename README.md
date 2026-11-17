# PagaFácil

A Buy Now, Pay Later (BNPL) lending prototype for university students in Mexico.
PagaFácil pays the merchant and the student repays in monthly installments with interest.
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

1. León signs in, checks out at the campus bookstore and chooses 3, 6, 9 or 12 months.
2. The app shows interest, total repayment, installments, schedule and an effective annual
   rate as a reference figure, not the official CAT.
3. A rule-based check approves a loan only within the credit limit and monthly-income share.
4. Once accepted, the app records the simulated merchant payout and installment schedule.
   The student can mark installments paid or late and see the remaining balance.
5. Unpaid installments become late after their due date, and defaulted after more than 45
   calendar days past due.

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
4. Enter a cart over $6,500 to show rejection.
5. Sign in as `ana` to see the seeded defaulted loan.
6. While signed in as `leon`, try opening Ana's loan. The app returns 404.

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

## Project files

- `SPEC.md`: scope, core flow, data model and unit economics; source of truth
- `AGENTS.md`: project rules for AI assistance
- `DECISIONS.md`: design decisions and rationale
- `BITACORA.md`: work and review log
- `PROJECT_METHOD.md`: course method
