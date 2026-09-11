---
name: 07-web-testing
description: Stage 7 of the QA pipeline. Takes QA and FAIL points from the 06-qa-code-review results and test cases, executes them in a browser via the Claude in Chrome extension, verifies expected results and forms a detailed report. Use when the user says "web testing", "test in browser", "go through QA points", "manual testing", or after 06-qa-code-review completes.
---

# Web Testing

Executes QA and FAIL test cases in real browser.
QA — points that cannot be checked by code.
FAIL — points that code review identified as problematic,
require verification in UI that bug really exists.
Input — code review and test case files. Output —
detailed report with results of each test case
executed in UI.

## Input Data

Inputs, all read from the story folder:
1. Code review file `<ISSUEKEY>-code-review.md` created
   by the 06-qa-code-review skill.
2. Test cases in `test-cases/` created by 04-qa-test-cases —
   `index.md` plus one `TC-*.md` file per test case. Read only the
   case files for the QA and FAIL points taken from the code review;
   there is no need to load the whole folder.

Optional input:
- Checklist file `<ISSUEKEY>-checklist.md` — for structural
  checks that were not included in test cases.

## Story Folder

All file inputs and outputs live in the story folder built by
01-task-context:

```
stories/**/{ISSUEKEY}/
```

Locate it by globbing `stories/**/{ISSUEKEY}/` — one glob matches both
`stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

If the folder does not exist, or `{ISSUEKEY}-code-review.md` is
absent, or `test-cases/` holds no case files — stop and tell the user
which earlier stage to run. Do not create the structure here, and do
not fall back to the working directory.

If a `TC-*.md` file named by the code review is missing — report it as
a gap. Do not silently skip that point.
If any file is empty or corrupted — stop
and inform the user.

Data sources for this skill:
- code-review file — source of QA and FAIL points
- test-cases file — source of steps, test data
  and expected results
- checklist file (optional) — structural checks
- UI of the product via Chrome extension — source of actual
  results
- navigation_paths.json (in the skill directory) — memory of
  navigation paths, persists across tasks
- references/login-config.md — login instructions

All input files are read-only.
Do not modify, do not rewrite, do not clean their content.

Do not go to the tracker, do not use external tools,
do not inspect code.

## Rules

- All communication and all output file content — in English.
- Messages in chat are short.
- Browser tool: Claude in Chrome extension.
  Do not use Playwright MCP.
- Test cases with PASS and N/A statuses in code review
  are not executed in the browser. Only QA and FAIL are executed.
- Do not change data in the system without a direct test case step
  that requires this change. If the step says "enter value" —
  enter. If it doesn't say — don't enter. Do not create records,
  do not delete data, do not change settings if this
  is not an explicit step of the test case.
- Test data is taken from the "Test Data" column of the test case table.
  If there is a specific value — use it literally. If marked as
  `[test data]` with a realistic example — use that example.
  Do not make up test data yourself.
- After saving the file — stop. Do not continue
  to the next skills or planning.

## Chrome Extension Tools

Before touching the browser, invoke the `claude-in-chrome` skill —
it is required to activate the extension tools. Only after that are the
tools below available, exposed as `mcp__claude-in-chrome__<name>`
(for example `mcp__claude-in-chrome__navigate`). Short names are used
in this document for readability.

If the extension is not connected — stop and inform the user.
Do not fall back to Playwright MCP or any other browser tool.

To work with the browser, use these tools:

- **navigate** — navigate to URL.
- **find** — search for element on the page by natural language description.
  Main way to find elements.
- **read_page** — get page structure (accessibility
  tree). With `filter: "interactive"` — only interactive
  elements (buttons, fields, links).
- **computer** with `action: "screenshot"` — take screenshot.
  Use only as proof for FAIL
  and FAIL CONFIRMED. Do not take screenshots for PASS.
- **computer** with `action: "left_click"` — click on element.
- **computer** with `action: "type"` — enter text.
- **computer** with `action: "key"` — press key.
- **computer** with `action: "scroll"` — scroll page.
- **form_input** — set form field value by ref.
- **get_page_text** — get page text.
- **tabs_context_mcp** — get list of tabs.

Full interaction rules — in references/browser-rules.md.

## Workflow Order

### Step 1 — Gather Scope

Read `<ISSUEKEY>-code-review.md`. Find all test cases
with `QA` or `FAIL` status in the results table.
This is the working list for execution in the browser.

- `QA` — requires manual verification because code review
  could not verify from code.
- `FAIL` — code review found a problem from code,
  need to confirm or refute in UI.

Test cases with PASS and N/A statuses in code review
are not included in scope — they are already verified from code.

Then, for each QA and FAIL test case, read its own file —
`test-cases/<TC-ID>.md` — and extract full data:
- Precondition
- Table of steps (step, test data, expected result)
- Postcondition (if any)

For FAIL points additionally extract finding from code review:
file, line, what was expected, what actually in the code.
This information will help understand what exactly to check in UI.

If there are no QA and FAIL points (all PASS/N/A) — inform
user that there are no points for web testing and stop.

Inform user briefly:
```
Scope: [N] test cases for execution in browser.
- QA (check in UI): [N]
- FAIL (verify bug): [N]
Starting.
```

### Step 2 — Determine Target Pages

From test cases determine which pages or sections of the product
are needed. Usually visible from preconditions or
from test case names.

Group test cases by pages. If all test cases
are about one page — one group. If different
pages — several groups, execute sequentially by groups.

For the first (or only) group extract `TARGET_PAGE_NAME`.

### Step 3 — Check Navigation Memory

Read `navigation_paths.json` from the skill directory
(next to this SKILL.md). It is the only file in the skill this skill
may write to — navigation memory is reused across tasks.
If the file does not exist — create it with an empty structure:
```json
{"navigation_paths": {}}
```

Search for `TARGET_PAGE_NAME` as a key in `navigation_paths`.

**If found:**
- Extract `url` — direct URL if available.
- Extract `login_required` — whether login is needed.
- Extract `navigation_steps` — array of navigation steps.
- Set `PATH_EXISTS = true`.

**If not found:**
- Set `PATH_EXISTS = false`.

### Step 4 — Login (if needed)

Read `references/login-config.md` from the skill directory.

**If the file is filled** (contains URL, field descriptions,
credentials source):
- Execute login according to instructions from the file.
- Login rules — in references/browser-rules.md,
  section "Login".

**If the file is not filled** (contains placeholders
`<login page URL>`, `<how to find field>` etc)
or the file is missing:
- Ask user: login URL, where username
  and password fields are, which button is submit, where credentials come from.
- Execute login according to user instructions.

### Step 5 — Navigate to Target Page

**If `PATH_EXISTS = true`:**
Execute each step from `navigation_steps` sequentially,
following rules from references/browser-rules.md.

If a step from memory doesn't work (element not found,
page changed) — ask user for a new path
and update the record in `navigation_paths.json`.

**If `PATH_EXISTS = false`:**
Ask user:
```
Path to "[TARGET_PAGE_NAME]" not found in memory.
Describe step-by-step how to navigate to this page:
1. [First step]
2. [Second step]
3. ...
```

Wait for response. Execute user's steps.
Save steps as `USER_NAVIGATION_STEPS`.
Set `IS_NEW_PATH = true`.

### Step 6 — Execute Test Cases

For each test case from scope:

1. **Verify precondition:**
   - If precondition describes page state (e.g.
     "form is open", "list is loaded") — verify
     that current state matches. If not — navigate
     to the right page or perform actions to reach
     the state.
   - If precondition describes data presence (e.g.
     "there is a record with type Individual") and such data
     doesn't exist in the system — ask user how to prepare
     data: where to create, what values to specify, or if there is
     a ready record to use. Do not create
     data without user instructions.
   - If the next test case requires another
     page — navigate to it (check memory
     or ask user).

2. **Execute steps** — for each row of the test case table,
   interpreting the step as a browser action:

   **How to interpret steps:**
   - "Open [page/form/modal]" → `navigate`
     to URL or `find` + `computer click` on element
     that opens.
   - "Enter [value] in [field]" → `find` field
     by description → `form_input` or `computer type`.
   - "Click [button]" → `find` button by text
     → `computer left_click`.
   - "Select [option] in [dropdown]" → `find` dropdown
     → `computer left_click` → `find` option
     → `computer left_click`. Or `form_input` with value.
   - "Verify that [element/text] is displayed"
     → `find` element or `get_page_text` and search text.
   - "Scroll to [element]" → `computer scroll`
     or `find` + `computer scroll_to`.

**For each step:**
   a. `read_page` or `find` — see current state.
   b. Find target element.
   c. Execute action.
   d. Verify expected result from the table column
      "Expected result": search text,
      element or state on the page via `find`,
      `read_page` or `get_page_text`.
   e. Record step result: matches
      or doesn't match.

3. **Classify test case** according to section
   "Classification".

4. **If FAIL or FAIL CONFIRMED** — take screenshot
   (`computer screenshot`) as proof. Do not take screenshot
   for PASS, BLOCKED, FAIL REJECTED.

5. **Continue to the next test case** without stopping.

### Step 7 — Save Navigation Path (if new)

If `IS_NEW_PATH = true`:
- Read `navigation_paths.json` from the skill directory.
- Add new record:
```json
"[TARGET_PAGE_NAME]": {
  "url": "[URL if there is direct]",
  "login_required": true,
  "navigation_steps": ["step 1", "step 2", "..."],
  "last_used": "[ISO timestamp]"
}
```
- Save the file, do not overwrite existing records.

### Step 8 — Generate Report

Create file `<ISSUEKEY>-web-testing.md` with results.

Template — in references/output-template.md.

Report should be detailed:
- Table of results for each test case.
- For each FAIL and FAIL CONFIRMED — specifically:
  which step, what was expected, what agent actually saw.
- For each FAIL REJECTED — what code review finding showed
  and why UI works correctly.
- For each BLOCKED — reason and what agent saw.
- For each OBSERVATION — what exactly was noticed.
- Summary statistics.

## Classification

Each test case receives one status:

- `PASS` — UI behavior matches expected result
  from the test case. All steps executed successfully.
- `FAIL` — UI behavior does not match expected result.
  There is a specific discrepancy between expected and actual.
  Used for test cases that came with QA status
  from code review.
- `FAIL CONFIRMED` — test case came with FAIL status
  from code review and UI confirms: bug really appears
  in the interface. Include finding from code review + what agent saw
  in UI.
- `FAIL REJECTED` — test case came with FAIL status
  from code review but UI shows correct work. Bug from code
  does not appear in UI — possibly compensated by another
  mechanism, or code review was wrong.
- `BLOCKED` — test case cannot be executed. Element
  not found, page didn't load, no access,
  precondition unreachable.
- `OBSERVATION` — test case passed (PASS), but noticed
  defect or anomaly outside requirements scope.

Rules:
- Do not set PASS if there are doubts — better FAIL with description.
- Do not set FAIL without specific description of discrepancy.
- BLOCKED is not FAIL. Test didn't fail, it couldn't be executed.
- OBSERVATION does not replace FAIL. If expected result
  doesn't match — it's FAIL, not OBSERVATION.
- For points with FAIL from code review use only
  FAIL CONFIRMED or FAIL REJECTED — not regular FAIL/PASS.
  This allows seeing in the report what exactly was bug verification
  and what was new UI check.

## Browser Error Handling

- Page didn't load (timeout, 500, blank) —
  try to reload once via `navigate`.
  If didn't help — BLOCKED for all test cases
  on this page.
- Session expired during execution — repeat login
  according to step 4, continue from current test case.
- Element not found after 2 attempts (including scroll) —
  BLOCKED for this test case with description of what was searched and where.
- Alert or dialog appears — read text,
  record, close and continue. If dialog
  blocks execution — BLOCKED.
- Chrome extension doesn't respond — stop, inform
  user.

## Additional Checks (exploratory)

After executing all test cases, if agent noticed
something suspicious during navigation or step execution
that is not covered by test cases — record in "Observations"
section of the output file.

Do not search for bugs specially. Record only what
struck during test case execution.

## Verification Before Saving

Before saving, verify:

- Number of test cases in the report equals number of
  QA + FAIL points from code review file. If
  doesn't match — find missing and add.
- Test case order matches test-cases file order.
- Each FAIL and FAIL CONFIRMED has: which step,
  expected result, actual result.
- Each FAIL REJECTED has: code review finding and what
  agent saw in UI.
- Each BLOCKED has reason.
- No test cases without status.
- For points with FAIL from code review — used
  FAIL CONFIRMED or FAIL REJECTED, not PASS/FAIL.

## Output File

Create file `<ISSUEKEY>-web-testing.md` in the story folder:

```
stories/**/{ISSUEKEY}/{ISSUEKEY}-web-testing.md
```

This is the last pipeline stage — nothing reads the file downstream.

If file already exists — delete completely and create new.
On output always one file with result of last run.
Do not merge with previous version, do not append, do not save
data from previous write.

Before finishing verify:
- One header of top level
- One integral document without duplicate sections

Template — in references/output-template.md.

## Final Response

After saving the file inform:
- Path to saved file
- PASS / FAIL / FAIL CONFIRMED / FAIL REJECTED / BLOCKED / OBSERVATION counters
- Overall verdict: web testing successful
  (all PASS and FAIL REJECTED) or unsuccessful
  (there are FAIL or FAIL CONFIRMED)
- If there are FAIL or FAIL CONFIRMED — briefly list
  found problems
- If there are OBSERVATION — briefly list observations
- If there are BLOCKED — list what failed to execute and why
