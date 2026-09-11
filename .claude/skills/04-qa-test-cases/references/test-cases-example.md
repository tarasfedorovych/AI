# Test Cases Example

This example demonstrates expected detail level,
format, technique application, and distinction from checklist.

Requirements for the example (identical with checklist-example):

- REQ-1: State select filters leads by selected
  state. Default state — nothing selected (All States).
  List of states loads from API.
- REQ-2: City select filters leads by city.
  Depends on selected state — when state changes, list
  of cities updates. When "All States" is selected,
  list of cities is empty and select is inactive.
- REQ-3: Label "State" is displayed above State select.
- REQ-4: Button "Reset Filters" resets both selects
  and returns list of leads to full.

---

## REQ-1: State select filters leads by state

Applied Techniques: Use Case, EP

### TC-REQ-1.1: Filtering by state — main scenario

**Precondition:** Leads page is open, list contains
leads from different states, filter State = "All States"

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Select state in State select | California [test data] | List of leads is updated |
| 2 | Verify list of leads | — | All leads in list have state California |
| 3 | Verify result count | — | Count matches number of leads from California |

**Postcondition:** Filter State = California, list
is filtered

### TC-REQ-1.2: Return to full list

**Precondition:** Filter State = California [test data],
list is filtered

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Select "All States" in State select | All States | List of leads is updated |
| 2 | Verify list of leads | — | Leads from all states are displayed |

**Postcondition:** Filter State = All States, list is full

### TC-REQ-1.3: State with no leads — empty valid partition

**Precondition:** Leads page is open, database has states
with no leads

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Select state with no leads | Wyoming [test data] | List of leads is empty |
| 2 | Verify display | — | Message displayed that no leads found |

---

## REQ-2: Select City depends on selected state

Applied Techniques: State Transition

### TC-REQ-2.1: Activation of City when state is selected

**Precondition:** Leads page is open,
State = "All States", City is inactive

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Select state in State select | California [test data] | City select becomes active |
| 2 | Open City select | — | List contains only cities from California |
| 3 | Select city | Los Angeles [test data] | List of leads is filtered by California + Los Angeles |

**Postcondition:** State = California, City = Los Angeles,
list is filtered by both filters

### TC-REQ-2.2: Changing state resets selected city

**Precondition:** State = California, City = Los Angeles
[test data]

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Change state | Texas [test data] | City select is reset |
| 2 | Verify City select | — | City value is empty, list of cities updated with Texas cities |
| 3 | Verify list of leads | — | All leads from Texas without city filtering are displayed |

**Postcondition:** State = Texas, City = empty

### TC-REQ-2.3: Deactivation of City when All States is selected

**Precondition:** State = California, City = Los Angeles
[test data]

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Select "All States" | All States | City select becomes inactive |
| 2 | Verify City select | — | Value is reset, element not clickable |
| 3 | Verify list of leads | — | Leads from all states are displayed |

**Postcondition:** State = All States, City is inactive

---

## REQ-3: Label "State" is displayed above State select

Applied Techniques: Use Case

### TC-REQ-3.1: Label State is present and positioned above select

**Precondition:** Leads page is open

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Find State select label | — | Label with text "State" is displayed above State select |

---

## REQ-4: Button Reset Filters resets both selects

Applied Techniques: Use Case, EP

### TC-REQ-4.1: Reset when both filters are active

**Precondition:** State = California, City = Los Angeles
[test data], list is filtered

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Click "Reset Filters" | — | State select = "All States" |
| 2 | Verify City select | — | City is inactive, value is reset |
| 3 | Verify list of leads | — | Leads from all states are displayed |

**Postcondition:** State = All States, City is inactive,
list is full

### TC-REQ-4.2: Reset with partial filter

**Precondition:** State = California [test data],
City is not selected

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Click "Reset Filters" | — | State select = "All States" |
| 2 | Verify list of leads | — | Leads from all states are displayed |
