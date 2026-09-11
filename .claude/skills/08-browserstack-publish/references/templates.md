# Publish Templates

Preview, report and error templates for BrowserStack publishing.

---

## Publish Preview

Show this before any write, then stop and wait.

```markdown
## BrowserStack Publish Preview

**Target:** PR-3 (AISD — Practice Knowledge Hub) → AISD-5 — Practice Page / AISD-7 — Viewer - Restricted Access to Non-Published Content
**Mode:** create
**Source:** stories/AISD-5/AISD-7/test-cases (13 case files, index.md order)
**Defaults:** priority Medium · case_type Functional · automation_status not_automated · test data folded into steps

| # | TC | REQ | Name | Steps | Operation |
|---|----|-----|------|-------|-----------|
| 1 | TC-REQ-1.1 | REQ-1 | Archived practice hidden from browse and search — Viewer | 3 | Create |
| 2 | TC-REQ-1.2 | REQ-1 | Archived practice hidden from browse and search — role other than Viewer | 3 | Create |
| 3 | TC-REQ-3.1 | REQ-3 | SSO authentication with Viewer role opens the application | 3 | Update (TC-812) |

**Folders to create:** AISD-7 — Viewer - Restricted Access to Non-Published Content (under AISD-5, id 51009923)

**Warnings:**
- TC-REQ-4.1: step 2 has no expected result

**Stays local (not published):**
- index.md groupings, applied-technique lines and statistics
- REQ-2 clarification note (restore-to-Draft transition, no case generated)

**Summary:** 12 to create · 1 to update · 1 folder to create · 1 warning

---

Reply **confirm publish** to execute.
```

Rules for the preview:

- One row per payload element, in payload order.
- Name column shows the exact `name` that will be sent.
- Folder creation is a write — list it, never fold it into "target".
- Every `--validate-only` warning appears here.
- Always include "Stays local" so the user knows the local files remain
  the fuller record.

---

## Publication Report

### Success

```markdown
## BrowserStack Publication Result

**Status:** Success
**Project:** PR-3 (AISD — Practice Knowledge Hub)
**Folder:** AISD-7 — Viewer - Restricted Access to Non-Published Content
[Open folder](https://test-management.browserstack.com/projects/3083195/folder/51009925/test-cases)

### Created (13)

| # | TC | REQ | BrowserStack id | Name |
|---|----|-----|-----------------|------|
| 1 | TC-REQ-1.1 | REQ-1 | TC-821 | Archived practice hidden from browse and search — Viewer |
| 2 | TC-REQ-1.2 | REQ-1 | TC-822 | Archived practice hidden from browse and search — role other than Viewer |

**Total:** 13 cases created

**Stayed local:** index.md structure; the REQ-2 clarification note.
```

Keep the local `TC-REQ-*` id beside the assigned BrowserStack id — that
pairing is the only place the two id spaces are written down together.

### Partial

```markdown
## BrowserStack Publication Result

**Status:** Partial — stopped at case 4 of 13

**Project:** PR-3 · **Folder:** AISD-7 — Viewer - Restricted Access to Non-Published Content

### Created (3)

| # | TC | BrowserStack id | Name |
|---|----|-----------------|------|
| 1 | TC-REQ-1.1 | TC-821 | Archived practice hidden from browse and search — Viewer |

### Failed (1)

| TC | Error |
|----|-------|
| TC-REQ-1.4 | API error: invalid folder_id |

### Not attempted (9)

TC-REQ-2.1, TC-REQ-3.1, TC-REQ-3.2, TC-REQ-4.1, TC-REQ-5.1, TC-REQ-6.1, TC-REQ-6.2, TC-REQ-7.1, TC-REQ-7.2

**Next step:** re-resolve the folder id with `listFolders`, then publish
the remaining 10 with `--only`.
```

Never report a partial run as success, and always name what was not
attempted — otherwise a re-run silently duplicates the cases that did
get through.

### Failure

```markdown
## BrowserStack Publication Result

**Status:** Failed — no cases were published
**Error:** <error text as returned>

**Checks:**
1. `browserstack` MCP server connected (`claude mcp get browserstack`)
2. `project_identifier` is the `PR-N` form, not the numeric URL id
3. `folder_id` came from `listFolders`, not from a browser URL
4. Account has write access to the project
```

---

## Upsert Match Preview

When the target folder already holds cases, show the match analysis
before the publish preview.

```markdown
## Upsert Match Analysis

**Folder:** AISD-6 — Viewer - Consume a Published Practice (id 51009924) · 32 existing cases

| # | Local TC | Local name | Match | Action |
|---|----------|------------|-------|--------|
| 1 | TC-REQ-6.1 | Copy button copies the code block and shows "Copied!" | TC-707 (exact title) | Update |
| 2 | TC-REQ-6.2 | Copy button copies only its own code block | TC-708: "Verify button label changes..." (partial) | Create — no exact match |
| 3 | TC-REQ-16.1 | TOC lists every heading level as a flat, non-indented list | — | Create |

**Unmatched existing cases (25)** will be left untouched, not deleted.

Confirm the matches before proceeding.
```

Match on exact title only. A partial match is reported and then treated
as "create" — never as the same case. Existing cases with no local
counterpart are never deleted by this skill.

---

## Validation Errors

When the payload cannot be published as-is.

```markdown
## Validation Errors

Publishing is blocked until these are resolved:

| TC | Issue |
|----|-------|
| TC-REQ-4.1 | No step rows parsed — createTestCase requires at least one step |
| TC-REQ-5.2 | Step 2 has no expected result |
| — | index.md lists TC-REQ-9.3 but no file was found |

Test case files are read-only for this skill — fix them by re-running
04-qa-test-cases, or publish the rest with `--only`.
```

---

## Target Selection

When the project or folder is not yet known.

```markdown
## Select BrowserStack Target

### Projects

The API needs the `PR-N` identifier, not the numeric id in the URL.

| Identifier | Numeric id | Folders |
|------------|-----------|---------|
| PR-1 | 2223127 | 9 |
| PR-2 | 2224653 | 7 |
| PR-3 | 3083195 | 1 (AISD-5 — Practice Knowledge Hub) |

### Folders under AISD-5 — Practice Knowledge Hub (PR-3, id 51009923)

| Folder id | Name | Cases |
|-----------|------|-------|
| 51009924 | AISD-6 — Viewer - Consume a Published Practice | 32 |
| 51327437 | AISD-9 — Viewer - Scan Practices via Content Card | 14 |
| 51764824 | AISD-8 — Viewer - Consume Practice on Mobile Device | 0 |
| 52786320 | AISD-10 — Viewer - Use Type-Specific Actions on Practice | 16 |

No folder matches AISD-7. Reply **create folder** to add
`AISD-7 — {Story Title}` under AISD-5, or name an existing folder id.
```
