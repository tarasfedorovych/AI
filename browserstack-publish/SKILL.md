---
name: browserstack-publish
description: Publish test cases to BrowserStack Test Management via MCP. Use when syncing test cases to BrowserStack, pushing TC files, or publishing ApprovedCaseSet to BrowserStack.
---

# BrowserStack Test Case Publish

Publish test cases to BrowserStack Test Management using the BrowserStack MCP. Supports both `test-case.md` files and `ApprovedCaseSet` YAML as input sources.

## Purpose

Take test cases from either:
- **test-case.md files** from `stories/STORY-XXX/test-cases/`
- **ApprovedCaseSet YAML** (same format as jira-to-testrail-steps-design)

And sync them to BrowserStack Test Management with **preview + explicit confirmation** before any writes.

---

## Accepted Inputs

### Option 1: test-case.md Files

Stories follow an **Epic-rooted hierarchy**. Resolve the path before reading files:

```
stories/{EPIC-KEY}/{STORY-KEY}/test-cases/TC-{STORY-KEY}-NNN.md
```

If a Feature level exists:
```
stories/{EPIC-KEY}/{FEATURE-KEY}/{STORY-KEY}/test-cases/TC-{STORY-KEY}-NNN.md
```

If the story has no Epic parent:
```
stories/STANDALONE/{STORY-KEY}/test-cases/TC-{STORY-KEY}-NNN.md
```

To resolve the path, check the `package_id` frontmatter in `story.md` — it holds the Epic key.

Parse files from the resolved path, e.g. `stories/AISD-1/AISD-6/test-cases/TC-AISD6-001.md`:

```yaml
---
package_id: {EPIC-KEY}        # Epic key
story_id: {STORY-KEY}         # Story key
test_case_id: TC-{STORY-KEY}-001
title: Verify user can submit form
type: Positive
priority: High
---
```

### Option 2: ApprovedCaseSet YAML

Same structure as jira-to-testrail-steps-design:

```yaml
ApprovedCaseSet:
  Metadata:
    SourceJiraIssueKeys: ["PROJ-123"]
    ReviewStatus: "Reviewed"
  PublishMode: "create"
  Cases:
    - Title: "Verify ..."
      Priority: "High"
      Type: "Functional"
      Steps:
        - Action: "..."
          Expected Result: "..."
```

---

## Workflow

### Step 1: Validate Payload

Check each test case has:
- Title/name (required)
- At least one step with action and expected result
- Valid priority (Critical/High/Medium/Low)
- Valid type (Functional, Regression, etc.)

### Step 2: Resolve Target

Use BrowserStack MCP tools to resolve:

1. **Project** — `listFolders` with `project_identifier`
2. **Folder structure** — Mirror the local Epic → Story hierarchy in BrowserStack folders:

```
BrowserStack project
  └── {EPIC-KEY} — {Epic Title}        ← Top-level folder (Test Suite for Epic)
        └── {STORY-KEY} — {Story Title} ← Sub-folder (Test Suite for Story)
              └── [test cases here]
```

Create missing folders with `createProjectOrFolder` before publishing test cases.

3. If project or folder not specified, prompt the user to select or confirm creation.

### Step 3: Normalize to BrowserStack Format

**Use the conversion script** instead of manual/AI transformation:

```bash
python scripts/tc_to_browserstack.py <path-to-test-cases.md> --project PR-XXX --folder 123 --pretty --out /tmp/bs-payload.json
```

This outputs a JSON array of BrowserStack-ready payloads. Each element maps directly to `createTestCase` parameters:

```yaml
createTestCase:
  project_identifier: "PR-XXX"
  folder_id: "123"
  name: "Verify user can submit form"
  description: "This test case verifies..."
  priority: "High"
  case_type: "Functional"
  preconditions: "<ol><li>User should be logged in</li></ol>"
  test_case_steps:
    - step: "Click the Submit button"
      result: "Form should be submitted successfully"
  issues: ["PROJ-123"]
  automation_status: "not_automated"
  tags: ["positive", "high-priority"]
```

**Do NOT spend tokens** on format conversion — the script handles parsing markdown tables, HTML wrapping, priority mapping, and field normalization deterministically.

### Step 4: Determine Publish Mode

| Mode | Behavior |
|------|----------|
| `create` | Always create new cases; warn on title duplicates |
| `update` | Requires `test_case_identifier` per case |
| `upsert` | Match by title in folder; update if found, else create |

For upsert, use `listTestCases` to find existing cases by name match.

### Step 5: Show Publish Preview

Display preview table (see [templates.md](templates.md)) and **wait for user confirmation**.

### Step 6: Execute Publish

After user confirms:
- Call `createTestCase` for new cases
- Call `updateTestCase` for existing cases

### Step 7: Report Results

Output publication report with created/updated case IDs and any errors.

---

## BrowserStack MCP Tools

Read tool descriptors before calling:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `listFolders` | List folders in project | Discover folder_id for target |
| `listTestCases` | List cases in project/folder | Find existing cases for upsert |
| `createTestCase` | Create new test case | PublishMode: create or upsert (new) |
| `updateTestCase` | Update existing case | PublishMode: update or upsert (existing) |
| `createProjectOrFolder` | Create project/folder | When target doesn't exist |

### Tool Parameters Quick Reference

**createTestCase** (required):
- `project_identifier`: PR-XXX format
- `folder_id`: Folder ID string
- `name`: Test case title
- `test_case_steps[]`: Array of `{step, result}`

**updateTestCase** (required):
- `project_identifier`: PR-XXX format
- `test_case_identifier`: TC-XXX or case ID

---

## Field Mapping Summary

| Source | BrowserStack | Notes |
|--------|--------------|-------|
| title / Title | `name` | Required |
| type / Type | `case_type` | Functional, Regression, Smoke & Sanity |
| Priority | `priority` | Critical, High, Medium, Low |
| Preconditions | `preconditions` | HTML: `<ol><li>...</li></ol>` |
| Test Steps / Steps[] | `test_case_steps[]` | `[{step, result}]` |
| Expected Outcome | `description` | Brief description |
| Jira keys / References | `issues[]` | Array of issue IDs |
| Automation Candidate | `automation_status` | not_automated, automated |

See [field-mapping.md](field-mapping.md) for detailed mapping rules.

---

## Issue Tracker Integration

When linking Jira issues:

```yaml
issues: ["{STORY-KEY}", "{EPIC-KEY}"]   # Story key first, then Epic key
issue_tracker:
  name: "jira"
  host: "https://hannakhivrenko.atlassian.net"   # from story's jira_link frontmatter
```

Extract the host from the `jira_link` field in the story's frontmatter. Always include both the Story key and Epic key in `issues[]` so BrowserStack links trace back to the full hierarchy.

---

## Preconditions for MCP Writes

Before calling write tools:

1. **Read tool descriptors** — Check current MCP tool schemas
2. **User confirmed** — Never write without explicit "confirm publish"
3. **Target resolved** — Valid `project_identifier` and `folder_id`
4. **Payload validated** — All required fields present

---

## Quality Rules

- Preserve test case wording verbatim from source
- Use numbered list (`<ol><li>`) for preconditions, not bullets
- Map priority strings directly (Critical/High/Medium/Low)
- Include all Jira references in `issues[]` array
- Set `automation_status` based on Automation Candidate field

---

## What This Skill Does NOT Do

- Draft new test cases (use test-case-generator skill)
- Pull requirements from Jira (use jira-to-testrail-steps-design)
- Publish without preview + explicit confirmation
- Create test runs (separate workflow)
