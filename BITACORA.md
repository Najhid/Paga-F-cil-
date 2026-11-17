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
