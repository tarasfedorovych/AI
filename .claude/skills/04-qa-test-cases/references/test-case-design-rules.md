# Test Case Design Rules — reference

## Technique Selection by Requirement Type

| Requirement Type | Technique | Coverage Criterion |
|-----------------|-----------|--------------------|
| Ranges, limits, numeric constraints | EP + BVA | Each partition + each boundary value covered |
| Input data categories without numeric bounds | EP | Each partition (valid and invalid) covered |
| Multiple conditions → different actions | Decision Table | Each rule (combination of conditions) covered |
| Object with statuses/modes | State Transition | Each valid transition covered |
| Complete user scenario | Use Case | Main + alternative + exception scenarios |
| Many parameters with different values | Pairwise | Each pair of values for any two parameters covered |

Techniques are combined: one requirement may need
both Use Case (for flow), and EP+BVA (for input fields),
and State Transition (for statuses).

## Coverage Levels

**Standard (default for each task):**
- Main scenario (happy path)
- Invalid partitions (where any in requirements)
- Boundary values 2-value BVA (where limits in requirements)
- Alternative and exceptional scenarios (where described)
- Valid state transitions (where any states)

**Extended (only if user explicitly requests):**
- 3-value BVA
- Decision Table for complex business logic
- Invalid state transitions
- Pairwise for forms with 3+ parameters

## Mandatory Attributes of Each Test Case

- Identifier (TC-REQ-N.N)
- Scenario name
- Precondition
- Steps with input data
- Expected result for each significant step
- Postcondition — only if system state changes

The test design technique is specified once in the header
of the test case group for the requirement, not in each test case
separately.

## Quality Rules

**Accuracy.** One interpretation. Forbidden words
in expected results: "correctly", "properly",
"appropriate", "if needed", "as appropriate", "several".
Instead — specific value, state or behavior.

**Completeness.** Test case without expected result —
not a test case. Do not generate.

**Traceability.** Each test case is tied to REQ-ID.
Each behavioral requirement has at least one test case.

**Conciseness.** One test case = one scenario with one
focus of verification. Do not combine multiple independent
checks in one test case.

## EP Rules

- One representative from each class is sufficient.
  Do not generate multiple test cases from one class.
- Each invalid partition — separate test case.
  Do not combine multiple invalid values in one case.

## BVA Rules

- Apply only when the requirement has explicit numeric
  or text constraints (min/max, length, quantity).
- By default 2-value: boundary + nearest neighbor
  from adjacent partition.
- Do not generate BVA if requirement has no constraints.

## State Transition Rules

- Test case on transition = sequence of events that leads
  through several states. One test case can cover
  several transitions.
- Invalid transitions test only if requirement
  explicitly describes forbidden transitions.

## Decision Table Rules

- Use simplified (collapsed) table:
  if the value of a condition does not affect the action — merge
  rules.
- Do not generate full enumeration if part of combinations
  gives the same behavior.

## Anti-patterns (Prohibitions)

- Test case without expected result → do not generate
- Ambiguous formulation in requirement → do not generate test case, mark that requirement needs clarification
- Two test cases from one EP class → delete duplicate
- Test case for behavior absent in requirement → do not generate
- Test case without REQ-ID → do not generate
