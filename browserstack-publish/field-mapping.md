# Field Mapping Reference

Detailed mapping from test-case.md and ApprovedCaseSet formats to BrowserStack Test Management API.

---

## Source Format: test-case.md

### Frontmatter Fields

| test-case.md Field | BrowserStack Field | Transformation |
|--------------------|-------------------|----------------|
| `title` | `name` | Direct copy |
| `type` (Positive/Negative/Edge) | `case_type` | Map to Functional |
| `priority` (High/Medium/Low) | `priority` | Direct: Critical, High, Medium, Low |
| `test_case_id` | — | Used for tracking only |
| `story_id` | `tags[]` | Add as tag: `story:STORY-XXX` |
| `package_id` | `tags[]` | Add as tag: `package:FDP-XXX` |

### Body Sections

| test-case.md Section | BrowserStack Field | Transformation |
|---------------------|-------------------|----------------|
| `## Preconditions` | `preconditions` | Convert to `<ol><li>...</li></ol>` |
| `## Test Steps` table | `test_case_steps[]` | Parse Action → `step`, Expected Result → `result` |
| `## Expected Outcome` | `description` | Use as description |
| `## AC Mapping` | `description` | Append AC IDs to description |
| `## Test Data` table | `preconditions` | Append under "Test Data:" heading |
| `## Automation Candidate` | `automation_status` | Yes → automated, No → not_automated |

---

## Source Format: ApprovedCaseSet YAML

### Case Fields

| ApprovedCaseSet Field | BrowserStack Field | Transformation |
|----------------------|-------------------|----------------|
| `Title` | `name` | Direct copy |
| `Priority` | `priority` | Direct: Critical, High, Medium, Low |
| `Type` (Functional/GUI) | `case_type` | Direct mapping |
| `Specification` | `description` | Use as description |
| `Preconditions[]` | `preconditions` | Convert to `<ol><li>...</li></ol>` |
| `TestData[]` | `preconditions` | Append under "Test Data:" heading |
| `References[]` | `issues[]` | Extract keys: `[key1, key2]` |
| `Steps[]` | `test_case_steps[]` | Map Action → `step`, Expected Result → `result` |
| `Postconditions[]` | `preconditions` | Append under "Postconditions:" heading |

### Metadata Fields

| ApprovedCaseSet Metadata | Usage |
|-------------------------|-------|
| `SourceJiraIssueKeys[]` | Add all to `issues[]` |
| `PublishMode` | Determines create/update/upsert behavior |
| `ReviewStatus` | Validation only (must be Reviewed) |

---

## Preconditions Formatting

Convert preconditions to HTML ordered list:

### Input (test-case.md)
```markdown
## Preconditions

- 1. The user should be logged in as an Administrator.
- 2. The application should be on the Dashboard screen.
```

### Input (ApprovedCaseSet)
```yaml
Preconditions:
  - "1. The user should be logged in as an Administrator."
  - "2. The application should be on the Dashboard screen."
```

### Output (BrowserStack)
```html
<ol>
<li>The user should be logged in as an Administrator.</li>
<li>The application should be on the Dashboard screen.</li>
</ol>
```

**Rules:**
- Strip leading `^\d+\.\s*` from each line
- Use `<ol><li>` only (no `<ul>` bullets)
- Preserve "should" phrasing verbatim

---

## Test Steps Formatting

### Input (test-case.md)
```markdown
| Step | Action | Expected Result |
|---|---|---|
| 1 | Click the "Submit" button. | The form should be submitted. |
| 2 | Verify success message. | A success message should display. |
```

### Input (ApprovedCaseSet)
```yaml
Steps:
  - Action: "Click the \"Submit\" button."
    Expected Result: "The form should be submitted."
  - Action: "Verify success message."
    Expected Result: "A success message should display."
```

### Output (BrowserStack)
```json
{
  "test_case_steps": [
    {
      "step": "Click the \"Submit\" button.",
      "result": "The form should be submitted."
    },
    {
      "step": "Verify success message.",
      "result": "A success message should display."
    }
  ]
}
```

---

## Priority Mapping

| Source Value | BrowserStack Value |
|--------------|-------------------|
| Critical | `Critical` |
| High | `High` |
| Medium | `Medium` |
| Low | `Low` |

BrowserStack accepts display names directly.

---

## Type Mapping

| Source Value | BrowserStack `case_type` |
|--------------|-------------------------|
| Functional | `Functional` |
| GUI | `Functional` |
| Positive | `Functional` |
| Negative | `Functional` |
| Edge | `Functional` |
| Regression | `Regression` |
| Smoke | `Smoke & Sanity` |

---

## Automation Status Mapping

| Source Value | BrowserStack `automation_status` |
|--------------|--------------------------------|
| Yes | `automated` |
| No | `not_automated` |
| Partial | `not_automated` |
| (not specified) | `not_automated` |

Valid BrowserStack values:
- `not_automated`
- `automated`
- `automation_not_required`
- `cannot_be_automated`
- `obsolete`

---

## Issue Linking

### From test-case.md
Extract from story context or AC Mapping:
```yaml
issues: ["STORY-XXX"]
```

### From ApprovedCaseSet
```yaml
# Input
References:
  - key: "PROJ-123"
    url: "https://jira.example.com/browse/PROJ-123"
  - key: "PROJ-456"
    url: "https://jira.example.com/browse/PROJ-456"

# Output
issues: ["PROJ-123", "PROJ-456"]
issue_tracker:
  name: "jira"
  host: "https://jira.example.com"
```

---

## Tags Generation

Generate tags from metadata:

| Source | Tag Format |
|--------|-----------|
| story_id | `story:STORY-XXX` |
| package_id | `package:FDP-XXX` |
| type | `type:positive`, `type:negative`, `type:edge` |
| priority | `priority:high`, `priority:medium` |

---

## Combined Preconditions Block

When source has multiple sections, combine into single `preconditions` field:

```html
<ol>
<li>The user should be logged in as an Administrator.</li>
<li>The application should be on the Dashboard screen.</li>
</ol>

<p><strong>Test Data:</strong></p>
<ul>
<li>Email: test@example.com</li>
<li>Password: TestPass123!</li>
</ul>

<p><strong>Postconditions:</strong></p>
<ol>
<li>User session should be active.</li>
</ol>
```
