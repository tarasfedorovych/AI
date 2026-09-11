# Example Checklist — reference

This example demonstrates the quality and level of detail
expected from a checklist. Use as a reference
for calibration.

## Input Requirements (example)

- REQ-1: State Filter — select for filtering by state
- REQ-2: City Filter — select for filtering by city
- REQ-2a: Search by city within City select
- REQ-2b: Filter list of cities by selected state
- REQ-2c: Display state id next to city name
- REQ-2d: Field `order.lead.city_details` — search by city
  uses city_details array of ids separated by comma

## Checklist (example)

### REQ-1: State Filter — select for filtering by state
- [ ] REQ-1.1: State Filter is present on the page
- [ ] REQ-1.2: State Filter is a select (dropdown)
- [ ] REQ-1.3: List of states is populated with options
- [ ] REQ-1.4: Default state — nothing is selected
- [ ] REQ-1.5: Selecting a state filters the results
- [ ] REQ-1.6: Resetting the state selection removes the filter

### REQ-2: City Filter — select for filtering by city
- [ ] REQ-2.1: City Filter is present on the page
- [ ] REQ-2.2: City Filter is a select (dropdown)
- [ ] REQ-2.3: List of cities is populated with options
- [ ] REQ-2.4: Default state — nothing is selected
- [ ] REQ-2.5: Selecting a city filters the results
- [ ] REQ-2.6: Resetting the city selection removes the filter

### REQ-2a: Search by city within City select
- [ ] REQ-2a.1: Search field is present within City select
- [ ] REQ-2a.2: Typing text filters the list of cities
- [ ] REQ-2a.3: Search works by partial match
- [ ] REQ-2a.4: Search is case-insensitive
- [ ] REQ-2a.5: When there is no match — empty state (no results)
- [ ] REQ-2a.6: Clearing the search returns the full list of cities

### REQ-2b: Filter list of cities by selected state
- [ ] REQ-2b.1: When a state is selected, the list of cities shows
  only cities of that state
- [ ] REQ-2b.2: When the state is reset, the list of cities shows all cities
- [ ] REQ-2b.3: When the state changes, the previous city selection is reset
- [ ] REQ-2b.4: Search within City works within the scope of cities
  filtered by state

### REQ-2c: Display state id next to city name
- [ ] REQ-2c.1: Each city option in the list displays
  state id next to the city name
- [ ] REQ-2c.2: State id is displayed in the selected value
  in the closed select

### REQ-2d: Field order.lead.city_details — array of ids
- [ ] REQ-2d.1: Selecting a city writes the value
  to `order.lead.city_details`
- [ ] REQ-2d.2: Value is stored as array of ids
  separated by comma
- [ ] REQ-2d.3: Selecting multiple cities forms the correct string
  of ids separated by comma
- [ ] REQ-2d.4: Clearing the selection clears `city_details`
