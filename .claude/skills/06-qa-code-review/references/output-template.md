# <ISSUEKEY> - Code Review

Test cases: <path to test-cases file>
PR: <URL>

## Results

| TC | Name | Status |
|----|------|--------|
| TC-REQ-1.1 | <scenario name> | PASS |
| TC-REQ-1.2 | <scenario name> | FAIL |
| TC-REQ-1.3 | <scenario name> | QA |
| TC-REQ-2.1 | <scenario name> | N/A |

## Findings

### FAIL: TC-REQ-1.2 — <scenario name>

- **File:** <path>, line <N>
- **Expected:** <expected result from test case>
- **Actual:** <what the code does>

### N/A: TC-REQ-2.1 — <scenario name>

- **Reason:** <why not applicable — what exactly is missing in PR>

---

Section Rules:
- Results — table of all test cases in order from test-cases file.
- Findings — only for FAIL and N/A. PASS and QA do not require explanations.
- Each FAIL has file, line, expected/actual.
- Each N/A has reason why the item does not apply to the PR.
- If FAIL and N/A are absent — Findings section is not created.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| QA     | <N>   |
| N/A    | <N>   |
| Total  | <N>   |
