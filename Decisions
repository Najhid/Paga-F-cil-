DECISIONS: PagaFácil

One line per irreversible choice, with the reason. These are the questions asked at the Demo Day Q&A. Never rewrite a line: add a new one that supersedes it.

Date	Decision	Reason
2026-11-03	Vertical: lending, specifically BNPL	Our team's choice; students with no credit card cannot split a large one-off purchase
2026-11-03	We never hold client money and never pay yield; we lend and pay the merchant directly	Keeps the model to one regulated activity (lending) and avoids deposit-taking and yield rules
2026-11-03	Legal vehicle analyzed: SOFOM E.N.R.	The only vehicle consistent with lend / no deposits / no yield. TODO-verify registration, timeline and costs
2026-11-03	One user (León Lara, 21, student) and one merchant (campus bookstore)	One end-to-end flow that works beats several that don't (SPEC core flow)
2026-11-03	Stack: Python 3 + Flask + SQLite, tests with pytest	Simplest stack that completes the core flow; SQLite ships with Python, so no extra database dependency
2026-11-03	Pricing: flat interest of 2% per month of term on the original price (6%, 12%, 18%, 24% total)	Simple to explain to the user; effective annual rate is about 42% to 51%, so CAT must be shown (TODO-verify with Condusef)
2026-11-03	Merchant fee: 4% of the sale, deducted from the payout to the merchant	Second revenue stream; we advance 96% of the price
2026-11-03	Unit economics assumptions: ticket $2,500, cost of funds 10% annual, default 5%, servicing $40 per loan, CAC $180, 3 loans per customer, year-1 fixed costs about $120,000	Recomputed after the first deck had inconsistent numbers; all are our own assumptions, computed from the data model
2026-11-03	Base case for the model is the 6-month plan (about $163 contribution per loan)	Middle plan; the 3-month plan has almost no margin (about $45)
2026-11-03	Late fees and collections are out of scope this semester	Not needed for the core flow; default is modeled only as a 5% assumption
