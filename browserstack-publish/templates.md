# BrowserStack Publish Templates

Preview and report templates for publishing test cases to BrowserStack Test Management.

---

## Publish Preview Template

Show this before any write operations:

```markdown
## BrowserStack Publish Preview

**Target:** Project [PR-XXX] | Folder [folder_name]
**Mode:** create | update | upsert
**Source:** test-case.md files | ApprovedCaseSet

| # | Name | Type | Priority | Steps | Issues | Operation | Notes |
|---|------|------|----------|-------|--------|-----------|-------|
| 1 | Verify user can submit form with valid data | Functional | High | 5 | PROJ-123 | Create | — |
| 2 | Verify error message for invalid email | Functional | Medium | 3 | PROJ-123 | Create | — |
| 3 | Verify form validation at boundary | Functional | Medium | 4 | PROJ-123 | Update (TC-456) | Existing case found |

**Warnings:**
- Case #2: Missing preconditions
- Duplicate title found: "Verify user can submit form" (existing TC-123)

**Summary:**
- To create: 2 cases
- To update: 1 case
- Warnings: 2

---

Reply **confirm publish** to execute.
```

---

## Publication Report Template

Show after successful/partial publication:

### Success

```markdown
## BrowserStack Publication Result

**Status:** Success
**Project:** PR-XXX (Project Name)
**Folder:** Feature Tests

### Created (2 cases)

| # | Name | Case ID | Link |
|---|------|---------|------|
| 1 | Verify user can submit form with valid data | TC-789 | [View](https://test-management.browserstack.com/...) |
| 2 | Verify error message for invalid email | TC-790 | [View](https://test-management.browserstack.com/...) |

### Updated (1 case)

| # | Name | Case ID | Link |
|---|------|---------|------|
| 1 | Verify form validation at boundary | TC-456 | [View](https://test-management.browserstack.com/...) |

**Total:** 3 cases published successfully
```

### Partial Success

```markdown
## BrowserStack Publication Result

**Status:** Partial
**Project:** PR-XXX (Project Name)

### Created (1 case)

| # | Name | Case ID | Link |
|---|------|---------|------|
| 1 | Verify user can submit form | TC-789 | [View](...) |

### Failed (1 case)

| # | Name | Error |
|---|------|-------|
| 1 | Verify error message | API Error: Invalid folder_id |

**Retry suggestion:** Verify folder_id exists using `listFolders` tool.
```

### Failure

```markdown
## BrowserStack Publication Result

**Status:** Failed
**Error:** Authentication failed - invalid credentials

**Troubleshooting:**
1. Verify BrowserStack MCP is properly configured
2. Check API credentials are valid
3. Confirm project access permissions

No cases were published.
```

---

## Upsert Match Preview

When using upsert mode, show matches:

```markdown
## Upsert Match Analysis

**Folder:** Feature Tests (ID: 123)
**Existing cases in folder:** 15

| # | Input Title | Match | Action |
|---|-------------|-------|--------|
| 1 | Verify user can submit form | TC-456: "Verify user can submit form" (exact) | Update |
| 2 | Verify error handling | TC-789: "Verify error handling for forms" (partial) | Create (no exact match) |
| 3 | Verify new feature | — | Create |

**Confirm matches are correct before proceeding.**
```

---

## Validation Error Template

When input validation fails:

```markdown
## Validation Errors

The following issues must be resolved before publishing:

| # | Case | Issue |
|---|------|-------|
| 1 | Verify user login | Missing: test_case_steps (required) |
| 2 | Verify form submit | Invalid priority: "Urgent" (use Critical/High/Medium/Low) |
| 3 | — | Missing: project_identifier (required) |

**Fix these issues and retry.**
```

---

## Target Resolution Template

When project/folder needs selection:

```markdown
## Select BrowserStack Target

### Available Projects

| # | Project ID | Name |
|---|------------|------|
| 1 | PR-123 | Mobile App Tests |
| 2 | PR-456 | Web App Tests |
| 3 | PR-789 | API Tests |

**Specify project:** Reply with project ID (e.g., "PR-123")

---

### Folders in PR-123 (Mobile App Tests)

| # | Folder ID | Name | Cases |
|---|-----------|------|-------|
| 1 | 100 | Authentication | 25 |
| 2 | 101 | User Profile | 18 |
| 3 | 102 | Settings | 12 |

**Specify folder:** Reply with folder ID (e.g., "100")

Or reply **create folder [name]** to create a new folder.
```

---

## Quick Reference: MCP Tool Calls

### List Folders
```
Tool: listFolders
Arguments:
  project_identifier: "PR-XXX"
  parent_id: (optional, for sub-folders)
```

### List Test Cases
```
Tool: listTestCases
Arguments:
  project_identifier: "PR-XXX"
  folder_id: "123" (optional)
```

### Create Test Case
```
Tool: createTestCase
Arguments:
  project_identifier: "PR-XXX"
  folder_id: "123"
  name: "Test case title"
  test_case_steps: [{step: "...", result: "..."}]
  (optional: description, preconditions, priority, case_type, issues, tags, automation_status)
```

### Update Test Case
```
Tool: updateTestCase
Arguments:
  project_identifier: "PR-XXX"
  test_case_identifier: "TC-XXX"
  (any fields to update)
```
