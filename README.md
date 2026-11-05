PagaFácil

A Buy Now, Pay Later (BNPL) lending prototype for university students in Mexico. PagaFácil pays the merchant and the student repays in monthly installments with interest. We never hold client money and never pay yield.

Course: FIN506 Financial Technology · Universidad Panamericana · Fall 2026 Team: Angel Najhid Flores Cartagena · Luciano Yitani Chapa

Prototype only. All users, merchants and transactions are invented. There are no real payments, no real credit checks and no real personal data.

The user and the problem

León Lara, 21, is a university student who has just started working part-time and has no credit card or credit history. He needs to buy textbooks and supplies at the campus bookstore at the start of the semester, and can only afford them in monthly payments.

What the demo shows (core flow)
León checks out at the campus bookstore and chooses a term: 3, 6, 9 or 12 months.
The app shows the full cost before he accepts: interest, total to repay, installment and schedule.
A simple rule-based check approves or rejects the loan.
If approved, the payout to the merchant (price minus the 4% fee) and the installment schedule are recorded; León can mark installments as paid or late and see his balance.
How to run it

TODO: fill in once the first version of the app exists. Planned stack: Python 3, Flask, SQLite, pytest.

# 1. Clone the repo and open the folder
# 2. Create a virtual environment and install dependencies   TODO: exact commands
# 3. Load the invented seed data                              TODO: exact command
# 4. Start the app                                            TODO: exact command
# 5. Open the URL it prints in your browser
How to run the tests

TODO: python3 -m pytest once tests exist.

Unit economics

The model computes contribution per loan, LTV, CAC and payback from the data model (see economics.py, TODO once built). Assumptions and results are in SPEC.md. All values are our own assumptions.

Regulatory note

PagaFácil is a classroom prototype and is not a regulated financial entity. The legal vehicle we analyzed (SOFOM E.N.R.) and its costs are assumptions. TODO-verify.

Project files
SPEC.md: scope, core flow, data model, unit economics (source of truth)
AGENTS.md: standing rules for the AI agent
DECISIONS.md: irreversible choices and their reasons
BITACORA.md: log of what the AI did and what we decided
PROJECT_METHOD.md: the course method we follow
