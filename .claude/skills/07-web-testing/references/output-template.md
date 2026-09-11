# <ISSUEKEY> - Web Testing

Code Review: <path to code-review file>
Test Cases: <path to test-cases file>
Date: <YYYY-MM-DD>

## Scope

Number of test cases for web testing: <N>
- QA (UI check): <N>
- FAIL (bug confirmation): <N>

## Results

| TC | Name | Source | Status | Comment |
|----|------|--------|--------|---------|
| TC-REQ-1.1 | <scenario name> | QA | PASS | — |
| TC-REQ-1.2 | <scenario name> | QA | FAIL | Step 3: expected "X", got "Y" |
| TC-REQ-2.1 | <scenario name> | FAIL | FAIL CONFIRMED | UI confirms bug |
| TC-REQ-2.2 | <scenario name> | FAIL | FAIL REJECTED | UI works correctly |
| TC-REQ-3.1 | <scenario name> | QA | BLOCKED | Element not found |
| TC-REQ-4.1 | <scenario name> | QA | PASS | OBSERVATION: <what was noticed> |

## Findings

### FAIL: TC-REQ-1.2 — <scenario name>

- **Source:** QA
- **Step:** #3 — <step description from test case>
- **Test Data:** <what was entered>
- **Expected:** <expected result from test case>
- **Actual:** <what the agent saw on the page>

### FAIL CONFIRMED: TC-REQ-2.1 — <scenario name>

- **Source:** FAIL (code-review)
- **Code Review Finding:** <file, line, problem description from code-review>
- **Step:** #<N> — <step description>
- **Expected:** <expected result>
- **Actual:** <what the agent saw — confirms bug>

### FAIL REJECTED: TC-REQ-2.2 — <scenario name>

- **Source:** FAIL (code-review)
- **Code Review Finding:** <file, line, problem description from code-review>
- **Actual in UI:** <what the agent saw — works correctly>
- **Conclusion:** <why the bug doesn't appear in UI>

### BLOCKED: TC-REQ-3.1 — <scenario name>

- **Source:** QA
- **Reason:** <why execution failed>
- **Page State:** <what the agent saw at the moment of blocking>

---

Section Rules:
- Results — table of all QA and FAIL test cases in order from test-cases file.
- Source Column: QA or FAIL — where the test case comes from in code-review.
- Comment Column: for PASS — dash or OBSERVATION. For FAIL — short description. For BLOCKED — reason. For FAIL CONFIRMED/REJECTED — short description.
- Findings — for FAIL, FAIL CONFIRMED, FAIL REJECTED and BLOCKED.
- PASS does not require explanations.
- FAIL REJECTED also has finding — to make it clear what exactly is refuted.
- If findings are absent — section is not created.

## Observations

Additional defects or anomalies noticed during test case execution
not covered by requirements:

- <OBS-1>: <what was noticed, where, under what conditions>
- <OBS-2>: <what was noticed, where, under what conditions>

If no observations — section is not created.

## Statistics

| Status | Count |
|--------|-------|
| PASS   | <N>   |
| FAIL   | <N>   |
| FAIL CONFIRMED | <N> |
| FAIL REJECTED  | <N> |
| BLOCKED | <N>      |
| OBSERVATION | <N>  |
| Total | <N>       |

Verdict: <Web testing successful (all PASS and FAIL REJECTED) / Web testing unsuccessful — there are N FAIL, N FAIL CONFIRMED>
