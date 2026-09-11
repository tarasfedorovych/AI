# Output Templates

Test cases are written as one file per case plus an index, into
`stories/**/{ISSUEKEY}/test-cases/`.

---

## index.md

```markdown
# <ISSUEKEY> - Test Cases

Checklist: <path to checklist file>
Generated: <YYYY-MM-DD>

---

## REQ-1: <requirement text>

Applied techniques: <EP, BVA, State Transition, Use Case, etc.>

- [TC-REQ-1.1](TC-REQ-1.1.md): <scenario name>
- [TC-REQ-1.2](TC-REQ-1.2.md): <scenario name>

---

## REQ-2: <requirement text>

> ⚠️ Requirement needs clarification: <what exactly is ambiguous>.
> Test cases not generated.

---

## Statistics

- Requirements covered: <N>
- Requirements needing clarification: <N>
- Total number of test cases: <N>
```

The index lists each test case as a link. It never inlines step
tables — those live in the per-case files.

---

## TC-REQ-<N>.<M>.md

One file per test case. Filename is the test case ID.

```markdown
# TC-REQ-1.1: <scenario name>

Requirement: REQ-1 — <requirement text>
Applied technique: <EP, BVA, State Transition, Use Case, etc.>

**Precondition:** <what must be set up before start>

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | <action> | <data or —> | <result> |
| 2 | <action> | <data or —> | <result> |

**Postcondition:** <new system state — only if changed>
```

Rules:
- One top-level heading, matching the filename's test case ID.
- `Requirement:` repeats the REQ id and text so the file is readable
  standalone, without opening the index.
- Omit `**Postcondition:**` entirely when no state changes.
- A requirement flagged as needing clarification produces no case
  file — it is recorded in `index.md` only.
