---
name: 04-qa-test-cases
description: Stage 4 of the QA pipeline. Takes the checklist created by the 03-qa-checklist skill and generates test cases with concrete steps, test data and expected results — input for 06-qa-code-review and for manual testing. Use when the user says "write test cases", "generate test cases", "test cases for requirements", or after 03-qa-checklist completes.
---

# QA Test Cases

Generates test cases with concrete steps, test data
and expected results based on checklist.

Test cases are NOT a checklist. Checklist says "what to check".
Test case says "how to check": concrete scenario
with concrete actions and concrete data.

## Input Data

Input — file `<ISSUEKEY>-checklist.md` created by 03-qa-checklist
skill, read from the story folder.

## Story Folder

All inputs and outputs live in the story folder built by
01-task-context:

```
stories/**/{ISSUEKEY}/
```

Locate it by globbing `stories/**/{ISSUEKEY}/` — one glob matches both
`stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

If the folder does not exist, or it holds no
`{ISSUEKEY}-checklist.md` — stop and tell the user which earlier
stage to run. Do not create the structure here, and do not fall back
to the working directory.

From the checklist, the skill takes:
- The requirement text from the heading of each section — to generate
  test cases and grounding of expected results.
- Decomposition into checks — to define scope:
  if checks are only for presence, type, or label
  of an element — the requirement is structural, test case is not needed.
- REQ-ID — for traceability.

Additional sources:
- User's answers to questions before generation.

First, read the checklist file completely. If something
in the requirements is unclear or ambiguous for building
test cases — ask the user before starting generation.
Do not start generation while there are unresolved questions.

Do not go to the tracker, do not use external tools,
do not search the internet, do not inspect code.

Checklist file is read-only.
Do not modify, do not rewrite, do not clean its content.

If checklist file is missing, empty or corrupted —
stop and inform the user that 03-qa-checklist skill
needs to be completed first.

## Rules

- All communication and all output file content — in English.
- Messages in chat are short.
- Test cases are built only from what is in the checklist file.
  Do not guess, do not add, do not interpret requirements on your own.
  Do not invent routes, selectors, roles, states, data, or expected
  behavior that is not in the requirements.
- Do not change the meaning and wording of requirements. Checklist file is
  final. The skill has no right to change or rephrase anything in it.
- If a requirement describes a concrete value (number, text, label,
  field name, state) — the test case uses exactly that value.
  Do not replace with another, do not generalize.
- If a requirement does NOT describe a concrete value but the test case
  needs test data — use realistic examples
  and mark them as `[test data]`.
- If a requirement was left unchanged after grooming
  (user skipped question in skill 2) — build test cases
  on what there is. Do not skip such requirement and do not mark
  it as incomplete. Checklist file is final.
- Do not add general QA advice that is not tied
  to a specific requirement of the task.
- After saving the file — stop. Do not continue
  to code review, PR summary or planning.

## Numeration

Test cases inherit requirement IDs from the checklist file.

The order of requirements in the test case file must match the order
of requirements in the checklist file. Do not change, do not rearrange,
do not group requirements differently than they appear in the file.

One requirement can produce several test cases.
Each test case receives a sub-number: TC-REQ-3.1, TC-REQ-3.2.

The main number REQ-* does not change — it is the same
as in the checklist file and later in code review.

If a requirement already has sub-points (REQ-5a, REQ-5b) —
each sub-point is numbered separately: TC-REQ-5a.1, TC-REQ-5a.2.

## Test Cases Scope

Each requirement from the checklist file is covered: behavioral ones —
by test cases, structural ones (only presence, type, label) —
by the checklist. For structural requirements, test case is not generated —
the checklist is sufficient level of verification.

Each behavioral requirement receives at least one test case.

Who then executes these test cases — code review agent on code
or a person in UI — is a matter for the next stages, not this skill.

## Test Case Building Method

For each behavioral requirement, determine which test design technique
is applicable. Choice of technique, coverage criteria
and rules of application — in references/test-case-design-rules.md.

Not every technique applies to every requirement —
apply only those that follow from the specific requirement.

The technique is indicated once in the heading of the group
of test cases for a requirement, not in each test case separately.

By default, use the standard coverage level
(defined in references/test-case-design-rules.md).
Extended level — only if user explicitly requests it.

### Grounding Rule

Each test case must be tied to specific
behavior described in the requirement.

If a test case contains an expected result — that result
must follow from the requirement text. If the expected result
for a scenario cannot be determined from the requirement text —
do not generate the test case, mark that the requirement needs
clarification.

If a test case uses a concrete value (number,
text, ID) — and that value is in the requirement, use it
literally. If the value is not in the requirement — mark
as `[test data]` and use a realistic example.

### Filtering Unnecessary Test Cases

Do not generate test cases for:
- standard browser or platform behavior
  (scroll, focus, opening a tab) if the requirement
  does not describe custom behavior
- implementation details (cache, performance, architecture)
  if this is not specified in the requirement
- general infrastructure (server errors, timeouts,
  network failures) if the ticket is not about this
- edge values for fields where the requirement does not describe
  constraints or ranges
- UX details (animations, timings, hover effects) if
  they are not specified in the requirement
- scenarios for which the expected result cannot be determined
  from the requirement text

Full list of anti-patterns —
in references/test-case-design-rules.md, section "Anti-patterns".

## Verification Before Saving

After generating test cases and before saving the file:

1. Filter test cases for unnecessary ones.
2. Go through test cases and verify:

- Each requirement from the checklist file has at least one test case.
- No test cases without REQ-ID.
- The order of requirements matches the order in the checklist file.
- No duplication: the same scenario does not appear twice.
  Two test cases from one equivalence class — duplicate.
- Each test case has a precondition, steps, test data
  and expected result. If any part is empty —
  delete or complete it.
- The expected result of each test case follows
  from the requirement text, not made up.
- Expected results do not contain ambiguous words:
  "correctly", "properly", "appropriate", "as needed",
  "appropriately". Instead — concrete value,
  state or behavior.
- Test data is realistic and marked where not from requirement.

If a problem is found — fix before saving.

## Output Files

Write into the `test-cases/` folder of the story folder —
**one file per test case**, plus an index:

```
stories/**/{ISSUEKEY}/test-cases/
  index.md          ← REQ grouping, techniques, statistics
  TC-REQ-1.1.md
  TC-REQ-1.2.md
  TC-REQ-2.1.md
```

File naming: one file per test case ID, `<TC-ID>.md` — the ID exactly
as generated (`TC-REQ-1.1.md`). No renumbering, no zero-padding.

`01-task-context` creates `test-cases/` with a `.gitkeep`. Remove that
`.gitkeep` once real case files are written.

### index.md

Carries everything that is not a single test case: the REQ grouping,
applied techniques per requirement, requirements flagged as needing
clarification, and the statistics block. Each test case appears as a
link to its own file, not as inlined content.

### Per-case files

Each holds exactly one test case: its ID and scenario name, the
requirement it covers, precondition, the step table, and
postcondition where the state changes.

### Rewriting

On every run, regenerate the whole folder: delete existing
`TC-*.md` files and `index.md` first, then write fresh. Do not merge
with the previous version, do not append, do not keep stale case
files — a test case that no longer exists must not survive as an
orphan file.

Before finishing verify:
- One top-level heading per file
- Every test case in `index.md` has a matching file, and every
  `TC-*.md` file is listed in `index.md`
- No `TC-*.md` file left over from a previous run

Template file structure — in references/output-template.md.
Example detail level — in references/test-cases-example.md.
Technique rules and coverage — in references/test-case-design-rules.md.

## Final Response

After saving the file inform:
- Path to saved file
- Number of test cases
- Number of requirements covered
- Recommendation: "For next skills (05-pr-summary,
  06-qa-code-review) it is recommended to continue in new chat
  with test-cases and checklist files."
