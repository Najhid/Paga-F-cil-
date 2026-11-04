Agent instructions: PagaFácil (FIN506)

PagaFácil is a Buy Now, Pay Later (BNPL) lending prototype that pays campus merchants and lets university students with no credit history repay in monthly installments with interest.

Golden rules
SPEC.md is the source of truth. If a task conflicts with it, stop and say so instead of improvising.
Comment every financial formula: what it computes, and why this formula (CAC, LTV, contribution margin, interest, fees).
Never invent regulatory claims (Ley Fintech, CNBV, Banxico, Condusef, LFPDPPP). If a regulatory statement is needed and unverified, write TODO-verify next to it.
Ask before: adding any dependency, creating a new top-level folder, or changing the data model. These need both partners present.
Never read or write .env or any credentials file. This project contains no real secrets and no real personal data: all data is invented.
Prefer the simplest implementation that completes the core flow end to end. No features outside SPEC.md scope without flagging them first.
When a request is ambiguous, ask one clarifying question instead of guessing.
After significant changes, state plainly what you changed and where, so it can be logged in BITACORA.md.
Project facts
Vertical: lending (BNPL)
Core flow (the ONE flow that must work): a student checks out at the campus bookstore, picks a 3, 6, 9 or 12 month term and sees the full cost; a rule-based check approves or rejects the loan; if approved, the payout to the merchant (price minus 4% fee) and the installment schedule are recorded, and the student can mark installments as paid or late and see the updated balance.
Stack: Python 3 + Flask + SQLite (standard library), tests with pytest
Out of scope this semester: real payments, real KYC or credit bureau queries, native mobile app, more than one user role or merchant, late fees and collections, any savings, deposit or yield feature (see SPEC.md)
Fake data source: a seed script in src/ that creates the invented students and the single fake merchant; the payment processor is a simulated function
Language: code, comments, docs and UI text in English
