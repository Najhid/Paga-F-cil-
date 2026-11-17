# Bitacora: PagaFácil

One entry per work session. Three lines is enough. This is graded at every entrega and it is your audit trail for the live defense.

Template:

## <date> · <who worked>
- Goal: <what we set out to do>
- AI did: <what the agent generated or changed, which tool and model>
- We decided: <what we accepted, rejected or changed, and why>
- Reviewer flags: <what the reviewer report raised, and what we did about it>

---

## 2026-11-03 · Najhid + Luciano
- Goal: restart the project with a clean structure: fix the unit economics and write the SPEC and AGENTS files for PagaFácil (BNPL for university students).
- AI did: Claude (claude.ai, agent mode an Copilot agent mode) reviewed our deck and the course templates, found inconsistencies in the numbers (payback, ARPU, flat 2% monthly rate), recomputed effective annual rates and contribution per loan, and drafted SPEC.md and AGENTS.md. Copilot suggested the commit message for the SPEC.
- We decided: kept the BNPL idea and León Lara as the user; accepted the new assumptions (ticket $2,500, 4% merchant fee, 10% cost of funds, 5% default, $40 servicing, CAC $180, 3 loans per customer); pasted the SPEC directly in GitHub because we could not make the change from VS Code yet; the 3-month plan is still an open decision (almost no margin).
- Reviewer flags: none yet, the reviewer is not set up. Regulatory figures in SPEC are marked TODO-verify.

## 2026-11-05 · Najhid + Luciano
- Goal: finish the project's context and configuration files before writing any code (DECISIONS, README skeleton, .gitignore, VS Code settings, reviewer agent).
- AI did: Claude Sonnet 5.5 and Copilot (claude.ai chat, agent mode) drafted DECISIONS.md, a README.md skeleton with the run commands left as TODO because no code exists yet, and a .gitignore that keeps .env out of the repo. It adapted the course templates for .vscode/settings.json (added python3 commands for Mac) and for the reviewer agent (.github/agents/reviewer.agent.md), and walked us through uploading files to GitHub with a branch and a pull request.
- We decided: to add the files through pull requests so both partners approve; Luciano reviewed and approved them today and the files are now in the repo. We will review the open points one by one next (3-month plan, maximum installment-to-income share, CAT disclosure, reviewer file path, the professor's eight rules, and the approval row in SPEC.md).
- Reviewer flags: none, the reviewer has not run yet because there is no code to review.
- Correction to the 2026-11-03 entry: the chat tool was Claude Sonnet 5.5.

## 2026-11-10 · Najhid + Luciano
- Goal: close the repo and tooling items from our review checklist (file names, VS Code settings, reviewer agent) so the project is ready to start building.
- AI did: Claude Sonnet 5.5 guided us step by step: it spotted wrongly named files (Agent.md, Decisions.md, Reviewer.Agent without .md and outside .github/agents/), an unclosed brace in .vscode/settings.json, and reviewer tool names that no longer exist in our VS Code version (codebase, search, changes, findTestFiles); it suggested replacing them with read-only tools (view, grep, glob, rg). GitHub Copilot Code Review commented on settings.json, and Copilot Chat in VS Code (model selector showed "Copilot Fusion, Standard") helped us check the reviewer agent file. The reviewer agent itself ran for the first time on settings.json.
- We decided: renamed the files to AGENTS.md, DECISIONS.md and .github/agents/reviewer.agent.md; closed the missing brace in settings.json; replaced the reviewer's tools with read-only ones, so it still cannot edit files or run commands; applied Copilot's comment that explains "dial position 2 and 3", and did not apply the one that explains how to enable approve-everything, because course policy keeps that OFF on our laptops. Changes go through pull request for Luciano's approval.
- Reviewer flags: the reviewer returned STOP AND TALK because it had no diff to compare, and raised three findings on settings.json: (1) cat and Get-Content were auto-approved and could read .env, against AGENTS.md rule 5; (2) git add, commit, branch and checkout were auto-approved; (3) npm and pnpm test commands were auto-approved. We removed type, cat and Get-Content from the auto-approve list, removed checkout (kept add, commit, branch and restore --staged), and deleted the npm/pnpm line because the project uses Python (pytest stays auto-approved). Open limit: these settings only control terminal commands, so keeping the agent away from .env also depends on the rule in AGENTS.md.

## 2026-11-11 · Najhid + Luciano
- Goal: review the five repo documents for consistency and fix their formatting before we start coding.
- AI did: Claude Sonnet 5.5 and Copilot compared SPEC, DECISIONS, AGENTS, README and BITACORA against each other. It found that four files had lost their Markdown formatting when pasted, a stray upload link on the first line of SPEC.md, and DECISIONS.md still showing the 2% pricing after the SPEC moved to 4%. It recomputed the SPEC's 4% table (matches within about 1%). It regenerated AGENTS.md, DECISIONS.md and README.md with formatting restored, added the professors' working-style rules to AGENTS.md (professional context rewritten for our project) and drafted two DECISIONS lines for the 4% pricing.
- We decided: replaced the three files through a pull request and removed the stray link from SPEC.md; the old 2% line stays in DECISIONS.md because the log is append-only, and the new lines supersede it.
- Reviewer flags: reviewer not run on this change (documentation only). Claude flagged that the 4% price was chosen so every term recovers CAC, and that the 5% default assumption may be too low at about 113% effective annual rate; the sensitivity test in economics.py should vary price and default together. Numeric items stay with Luciano.
- Still open: approval rule (maximum installment share and credit limit), CAT disclosure, regulatory TODO-verify items.

## 2026-11-11 · Najhid
- Goal: implement the first checkout slice on `checkout-pricing`, showing the example cart's price across all four terms.
- AI did: Copilot added the Flask checkout page, Decimal-based pricing, monthly installment schedules, and tests under `src/`; updated README run instructions. All 15 tests pass.
- We decided: monthly due dates start one month after checkout on the same calendar day, using the month's last day when needed. The final installment absorbs cent rounding so scheduled payments equal the total.
- Reviewer flags: the reviewer identified the missing schedule and the possibility that rounded installments would not sum to the total; both were addressed and tested. CAT/effective annual rate remains TODO-verify per SPEC.md and is not included in this slice.

## 2026-11-14 · Najhid + Luciano
- Goal: apply the small fixes found in the repo review (money formatting, config comments, reviewer path decision) and add PROJECT_METHOD.md.
- AI did: Claude Sonnet 5.5 (claude.ai chat, not agent mode) reviewed the repo zip: it ran the 15 tests in a clean environment, recomputed prices and installment schedules, and found format_mxn showing $516.5 instead of $516.50, a duplicate SPEC2.md and missing comments in config.py. It gave us the code and comment changes step by step. <If Copilot applied or checked any of them, say exactly which and with what model.>
- We decided: added PROJECT_METHOD.md unchanged from the course version; fixed format_mxn and added two tests (17 tests pass); commented the constants in config.py; recorded in DECISIONS.md why the reviewer lives in .github/agents/. The minus sign in SPEC.md and the port change wait: the first until Luciano's updated SPEC is merged, the second only if the app fails to start.

## 2026-11-16 · Najhid + Luciano
- Goal: apply and verify the final core-flow changes for checkout, loans, installments and test-account isolation.
- AI did: Copilot in VS Code reviewed `final_push.zip`, integrated its Flask/SQLite flow, tests and docs, corrected the premature late-payment behavior in `src/loans.py`, and added regression tests. The selected model was not recorded in this session.
- We decided: both partners approved adding the SQLite users, merchant, loans and installments schema. We kept test credentials out of the repository and did not add dependencies.
- Reviewer flags: the ZIP allowed marking an installment late before its due date; the implementation now rejects that action and tests the future-due and overdue cases. No separate reviewer agent was run.

## 2026-11-16 · Najhid
- Goal: deploy the core flow to PythonAnywhere and verify the public test URL.
- AI did: Copilot guided the manual Flask deployment, configured the Python 3.11 virtual environment and WSGI import, and updated the README with the URL. No credentials or secret keys were added to the repository.
- We decided: use `https://najhid21.pythonanywhere.com` for the demo. The site loaded, León signed in, a six-month loan was recorded, and marking one installment paid reduced the displayed balance. PythonAnywhere's free site needs a monthly renewal; its dashboard showed a disable date of 2026-12-17.
- Reviewer flags: none. The deployed loan detail displayed 2026-11-17 as its creation date while the local date was 2026-11-16, so the server timezone/date difference remains to be checked.

## 2026-11-16 · Najhid + Luciano
- Goal: choose a conservative repeat-loan assumption for the financial model and update the unit-economics calculations.
- AI did: Copilot recalculated six-month lifetime contribution, LTV/CAC, CAC allocation and break-even sensitivity using the selected four-loan lifetime case.
- We decided: model 1 loan per customer per year for 4 years, or 4 lifetime loans, replacing the unsupported 24-loan case. At the six-month base term, estimated lifetime contribution before CAC is $1,660 and LTV/CAC is 8.3x; these remain assumption-based estimates.
- Reviewer flags: none. Five-year customer-acquisition, operating-cost, financing and valuation inputs are still needed before the complete Excel model can be populated.

## 2026-11-16 · Najhid
- Goal: create a financial-model workbook without presenting missing forecasts or valuation inputs as facts.
- AI did: Copilot generated `PagaFacil_Financial_Model.xlsx` with assumptions, five-year P&L, cash flow, unit economics and three valuation methods. It left unapproved forecasts and valuation inputs blank, added explanatory comments to formulas, and corrected the cash-flow proxy so borrower collections are not double-counted as P&L revenue. The selected model was not recorded.
- We decided: keep unresolved customer, cost, collection-timing and valuation assumptions blank until the team agrees on documented inputs. No project dependency was added.
- Reviewer flags: none. The workbook structure, 213 formulas and comments on every formula were checked with openpyxl; financial outputs still require the team's missing assumptions and spreadsheet recalculation.

## 2026-11-16 · Najhid
- Goal: add an initial customer-acquisition target to the financial model.
- AI did: Copilot entered a preliminary target of about 100 new students in Year 1 in the workbook and documented it in SPEC.md and DECISIONS.md. At the existing $200 CAC assumption, the workbook calculates $20,000 of acquisition expense.
- We decided: treat 100 as a team planning hypothesis, not a market forecast; leave Years 2 to 5 blank until an agreed growth basis exists.
- Reviewer flags: none. Workbook formulas and comments were revalidated; remaining forecasts and cost inputs are still open.

## 2026-11-16 · Najhid + Luciano
- Goal: extend the customer-acquisition scenario through Year 5 without assuming accelerated growth.
- AI did: Copilot updated the workbook and documentation to use 25 new students per year in Years 2 to 5, in addition to about 100 in Year 1.
- We decided: use 100 total additional customers spread evenly over Years 2 to 5. The scenario totals 200 new customers and implies $20,000 of acquisition expense in Year 1 plus $5,000 per year in Years 2 to 5 at the assumed $200 CAC. These are planning assumptions, not a market forecast.
- Reviewer flags: none. Workbook formulas continue to apply the four-year customer lifetime, so Year 1's cohort expires after Year 4.

## 2026-11-16 · Najhid + Luciano
- Goal: prevent double counting in the Year 1 fixed-cost budget.
- AI did: Copilot changed the workbook to treat the approximately $120,000 amount as the total fixed-cost envelope; any supplied personnel, technology, and legal allocations reduce the unallocated remainder.
- We decided: keep the $120,000 amount as an unverified aggregate, not as an extra cost above categories. Cost-category details remain pending.
- Reviewer flags: none. Formula comments and the budget-overrun check were validated. Under the six-month base case, Year 1 modeled EBITDA is -$98,500 before any costs beyond the assumed total fixed-cost envelope; this remains a planning result, not an observed outcome.

## 2026-11-16 · Najhid + Luciano
- Goal: allocate the Year 1 fixed-cost envelope using the team's revised estimates.
- AI did: Copilot added assumption inputs and workbook formulas for 25% personnel ($30,000), 50% technology ($60,000), and 25% office costs ($30,000) from the $120,000 total.
- We decided: treat the percentages as preliminary estimates; they do not establish market costs. Legal/regulatory costs are not separately budgeted, and the technology amount still needs to be split between setup and recurring expense.
- Reviewer flags: none. The three allocations reconcile to $120,000 and all 216 workbook formulas have explanatory comments.

## 2026-11-16 · Najhid + Luciano
- Goal: revise technology costs into setup and recurring components and keep the Year 1 budget internally consistent.
- AI did: Copilot updated the workbook and SPEC.md to use $45,000 one-time technology setup plus $25,000 recurring technology, while retaining $30,000 personnel and $30,000 office costs. Year 1 fixed costs therefore increase to $130,000; $25,000 technology expense is carried through Years 2 to 5.
- We decided: the estimates are preliminary; personnel and office recurrence and legal/regulatory costs remain unknown. The workbook no longer reports steady-state break-even until recurring fixed costs are defined.
- Reviewer flags: none. Year 1 amounts reconcile to $130,000, formulas and comments were validated, first-year cost-recovery values were recalculated, and the six-month Year 1 EBITDA estimate is -$108,500.

## 2026-11-16 · Najhid + Luciano
- Goal: revise the fixed-cost allocation to retain the $120,000 Year 1 total.
- AI did: Copilot updated the workbook and SPEC.md to use $25,000 personnel, $45,000 one-time technology setup, $25,000 recurring technology, and $25,000 office costs. Personnel, office and recurring technology are modeled through Years 2 to 5.
- We decided: this supersedes the $130,000 draft. Known recurring costs total $75,000 annually; legal/regulatory costs remain unbudgeted, so steady-state break-even stays pending.
- Reviewer flags: none. The Year 1 categories reconcile to $120,000, 228 workbook formulas have comments, first-year break-even values were recalculated, and six-month Year 1 EBITDA is -$98,500.

## 2026-11-16 · Najhid + Luciano
- Goal: add the current official regulatory fee that can be supported by a government source.
- AI did: Copilot checked CNBV's FAQ and the Cámara de Diputados 2026 update of amounts. It added MXN 34,229.19 for LFD Article 29, fraction XXVI as a potential Year 1 technical-opinion fee and updated the workbook, SPEC.md and DECISIONS.md.
- We decided: model the fee as a one-time Year 1 scenario expense, bringing modeled fixed costs to MXN 154,229.19. Applicability and renewal frequency remain TODO-verify; private legal counsel and ongoing compliance costs remain blank pending quotes.
- Reviewer flags: the CNBV FAQ still displays the 2016 fee of MXN 21,292. The official 2026 update lists MXN 34,229.19 for fraction XXVI; the workbook notes this discrepancy and does not treat the fee as a complete legal/compliance budget. Validation passed with 229 commented formulas; Year 1 break-even is 718 six-month loans, and steady-state break-even remains pending.

## 2026-11-16 · Najhid + Luciano
- Goal: calculate annual borrower collections and assign an illustrative funding mix in the financial model.
- AI did: Copilot added January/August origination-share inputs and formulas to the workbook. The formulas include all six installments for January originations, five for August originations in the same year, and the final August installment in the following year. It also set the required-capital split to 60% debt and 40% equity. SPEC.md and DECISIONS.md record both scenarios.
- We decided: use a 50% January and 50% August split for the six-month base case, and a 60% debt / 40% equity split only as an illustrative allocation. Collections are scheduled gross amounts before missed-payment effects; intra-year liquidity and actual payment dates remain unmodeled. Debt interest, term, fees, repayment schedule, and availability are also unknown and unmodeled.
- Reviewer flags: no separate reviewer run. Workbook formulas, comments and expected annual collection values were checked; the funding percentages total 100%. Recalculation in Excel or another spreadsheet engine remains to be confirmed.
