# Checklist Building Rules — reference

Sources: ISTQB CTFL v4.0, ISTQB CTAL-TA v4.0,
widely accepted practices of requirements-based testing.

## What is a Checklist Item

According to ISTQB, a test condition is an aspect or event of a component
or system that can be verified by one or more
test cases. A checklist item is an atomic test condition
with an unambiguous expected result.

A checklist item answers the question: "what to verify
and what result is expected". A test case (the next skill)
answers "how to verify".

## Quality Attributes of a Checklist Item

### Atomicity
One item = one check with one pass/fail.
"Button is visible and clickable" — two items.
If an item can be "partially pass" — break it down further.

### Traceability
Each item has a REQ-ID. Each requirement has at least one
item. No items without a source and no requirements
without any verification.

### Unambiguity
One interpretation. Any two people reading the item
must make the same pass/fail conclusion.

### Self-sufficiency
The item is clear without opening the requirements file
and without the context of other items.

### Independence
The item can be verified separately. Not "after
REQ-1.2 is executed the results are updated", but "when
a state is selected the results are updated".

### Absence of Duplication
One verification is not repeated in different items,
even under different REQ-IDs.

### Consistency
Identical types of elements receive the same basic set
of checks. The difference is only in specific checks
on top of the basic set.

## Formulation Rules

An item consists of two parts:
- What is being verified (element, state, behavior)
- What is the expected result (value, state, text)

Both parts are mandatory. An item without an expected
result is not a verification.

### Forbidden Words

Make verification ambiguous — do not use:
- "correctly", "right", "properly"
- "appropriate", "adequate", "acceptable"
- "as needed", "if necessary"
- "several", "some", "enough"
- "quickly", "smoothly", "conveniently"
- "looks good", "works fine"

Instead — specific value, state, text, number.

## Requirement Decomposition into Checklist Items

### Process According to ISTQB

Test Analysis: requirement → test conditions (aspects
to verify). Each test condition becomes
a checklist item.

For each requirement consecutively determine:
1. What elements or states the requirement describes
2. What actions or behaviors the requirement describes
3. What conditions or constraints the requirement describes
4. Are there dependencies on other requirements

Each item from steps 1-4 that has an unambiguous pass/fail
becomes a checklist item.

### Check Types

Not every type applies to every requirement —
generate only those that follow from the specific requirement.

**Positive Scenario** — basic behavior works
as described (happy path). Always applicable.

**Negative Scenario** — behavior when invalid actions
or data. Only when requirement describes interactivity.

**Boundary Values** — behavior at the edges. Only when
requirement describes numeric or text constraints.

**Default State** — initial state before user actions.
Only when requirement describes element
with initial state.

**Element States** — visibility, activity depending on
conditions. Only when requirement describes conditional behavior.

**State Transitions** — state change upon action.
Only when requirement describes state change.

**Reset** — return to initial state.
Only when requirement describes reset or clearing.

**Validation** — rules and messages. Only when
requirement describes validation.

**Data** — fields, formats, mappings. Only when
requirement describes specific fields or data formats.

**Condition Combinations** — behavior under various combinations.
Only when requirement has multiple independent conditions.

**UI Compliance** — labels, texts, positioning.
Only when requirement describes specific text or position.

### Checks at Requirement Boundaries

After decomposing each requirement separately — check
groups of related requirements. At the boundaries between requirements
there may be checks that are not visible during decomposition
of a single requirement: dependencies, conflicts, shared states.

## Sufficiency Criterion

### Sufficient when
- Each requirement has at least one verification
- Each item has exactly one pass/fail
- Each item is clear without context of other items
- Similar types of elements have the same basic set

### Excessive when
- Items duplicate each other in different words
- 10+ items for a simple requirement with one element
  and one behavior
- Item verifies a detail not in the requirement

## Basic Set for Typical Elements

Minimal scope for typical UI elements.
Use as a starting point — generate
only those items that follow from the specific requirement.

**Select:** presence → element type → options →
default state → main action → reset

**Text Input:** presence → field type → label →
placeholder (if any) → default value (if any) →
validation (if described) → constraints (if described)

**Button:** presence → text → action on click →
states and transition conditions

**Table / List:** presence → columns/fields →
data is displayed → sorting (if any) →
pagination (if any) → empty state

## Filtering Unnecessary Checks

Do not generate checks for:
- standard browser or platform behavior
- implementation details (architecture, cache, libraries)
- general infrastructure (server errors, timeouts)
- boundary values where requirement does not describe constraints
- negative scenarios for requirements without interactivity
- UX details (animations, timings, hover) not described in requirement
- checks for behavior not in the requirements

## Anti-patterns

**Duplication through rephrasing.**
"Button Save is present" and "Button Save is displayed" —
one item twice. Delete the duplicate.

**Implementation instead of behavior.**
"API returns 200", "Component uses useEffect" —
checklist verifies behavior for the user,
not implementation details.

**Non-atomic item.**
"Filter is present and on selection filters results" —
two items: presence + filtering. Split.

**Dependent item.**
"After executing REQ-1.2 the results are updated" —
the item must be self-sufficient.

**Made-up check.**
"List loads in 2 seconds" — if requirement
does not describe performance, the item should not exist.

**Ambiguous formulation.**
"Filtering works correctly" — what does "correctly" mean?
Instead: "Selecting state California displays
only leads from California state".
