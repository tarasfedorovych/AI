---
name: 08-browserstack-publish
description: Stage 8 of the QA pipeline. Publishes the test cases created by the 04-qa-test-cases skill to BrowserStack Test Management via the browserstack MCP, mirroring the local Epic/Story folder tree, with a preview and explicit confirmation before any write. Use when the user says "publish to BrowserStack", "sync test cases", "push test cases to BrowserStack", "upload test cases", or after 04-qa-test-cases completes.
---

# BrowserStack Publish

Takes a story's `test-cases/` folder and creates or updates the matching
test cases in BrowserStack Test Management.

This skill writes to an external system. Nothing is created or changed
without a preview and an explicit **confirm publish** from the user.

## Input Data

Input — the `test-cases/` folder of one story, as produced by
04-qa-test-cases:

```
stories/**/{ISSUEKEY}/test-cases/
  index.md
  TC-REQ-1.1.md
  TC-REQ-7a.1.md
  ...
```

Locate it by globbing `stories/**/{ISSUEKEY}/test-cases/` — one glob
matches both `stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

If the folder does not exist, holds no `TC-*.md` files, or holds only a
`.gitkeep` — stop and tell the user to run 04-qa-test-cases first. Do not
create the structure here, and do not fall back to the working directory.

Test case files and `index.md` are **read-only**. This skill never edits,
renumbers, or rewrites them.

## Rules

- All communication and all published content — in English.
- Chat messages — brief. Do not paste raw payload JSON into chat.
- Publish only what is in the test case files. Do not invent steps,
  expected results, test data, priorities, or preconditions.
- Preserve wording verbatim. The converter script is the only thing that
  reshapes text, and it only wraps and re-joins — it never rephrases.
- Never write to BrowserStack without an explicit **confirm publish**.
- After the publication report — stop. Do not create test runs, do not
  start executions, do not open browser sessions.

## Tracker Access

BrowserStack Test Management via the `browserstack` MCP server
(local `npx @browserstack/mcp-server`, stdio).

| Purpose | Tool |
|---|---|
| Find the target folder | `mcp__browserstack__listFolders` |
| Find existing cases (upsert / duplicate check) | `mcp__browserstack__listTestCases` |
| Create a folder | `mcp__browserstack__createProjectOrFolder` |
| Create a case | `mcp__browserstack__createTestCase` |
| Update a case | `mcp__browserstack__updateTestCase` |

Mandatory rule: if the integration is unavailable — stop and inform the
user. Do not use workarounds (browser automation on
`test-management.browserstack.com`, the REST API via curl, `WebFetch`)
as a replacement.

### Project Identifier

The API takes the **`PR-N` identifier**, never the numeric id in the
browser URL. A UI URL like
`https://test-management.browserstack.com/projects/3083195/folder/52786320/test-cases`
carries the numeric project id `3083195` and the folder id `52786320`.
Passing `3083195` as `project_identifier` fails with
"You have stumbled on an invalid endpoint".

There is no list-projects tool. To map a numeric id to `PR-N`, call
`listFolders` for `PR-1`, `PR-2`, … and read the numeric id back out of
each folder's `urls.self`. Known mapping for this account:

| Numeric id | Identifier | Project |
|---|---|---|
| 2223127 | `PR-1` | mixed / legacy suites |
| 2224653 | `PR-2` | EEFRAC |
| 3083195 | `PR-3` | AISD — Practice Knowledge Hub |

Verify before trusting this table — projects can be added.

## Recommended Flow

1. Resolve the story folder and read `index.md`.
2. Resolve the target project (`PR-N`) and folder id — see
   "Resolve the Target".
3. Convert with the script — see "Convert".
4. Decide the publish mode — see "Publish Mode".
5. Show the preview and **wait for confirmation**.
6. Execute the writes.
7. Report results.

## Resolve the Target

The BrowserStack folder tree mirrors the local story folder tree:

```
{project PR-N}
  └── {EPIC-KEY} — {Epic Title}          ← from stories/{EPIC-KEY}/epic.md
        └── {STORY-KEY} — {Story Title}  ← from stories/**/{STORY-KEY}/story.md
              └── test cases
```

Steps:

1. `listFolders` with the project identifier → find the epic folder.
2. `listFolders` with `parent_id` = the epic folder id → find the story
   folder.
3. Missing folders are created with `createProjectOrFolder`
   (`parent_id` = epic folder id for a story folder). Folder naming
   follows the existing convention in this project:
   `{KEY} — {Title}`, description `Story: {Title} ({KEY})`.
4. Creating a folder is a write. Include it in the preview and cover it
   with the same confirmation.

Never guess a folder id. If two candidate folders match a key, stop and
ask which one.

## Convert

Use the script — do **not** spend tokens transforming markdown by hand:

```bash
python .claude/skills/08-browserstack-publish/scripts/tc_to_browserstack.py \
  stories/{EPIC-KEY}/{STORY-KEY}/test-cases \
  --project PR-3 --folder {folder_id} --pretty --out {scratchpad}/bs-payload.json
```

It emits a JSON array where each element is a ready `createTestCase`
argument object. Write it to the scratchpad directory, not into the repo.

Useful options:

| Option | Effect |
|---|---|
| `--validate-only` | Parse and report warnings, emit no payload. Exit 1 if any warning. |
| `--priority Critical\|High\|Medium\|Low` | Priority for every case (default `Medium`) |
| `--case-type` | `case_type` (default `Functional`) |
| `--test-data step\|preconditions\|both` | Where the Test Data column lands (default `step`) |
| `--only TC-REQ-1.1 TC-REQ-1.2` | Publish a subset |
| `--no-issues` | Skip Jira issue linking |
| `--owner someone@example.com` | Set the case owner |

Run `--validate-only` first. Resolve every warning — or tell the user
about it in the preview — before publishing.

The script derives context from the path and files, so it needs no flags
for it: story key and epic key from the folder names, titles from the
`# ` heading of `story.md` / `epic.md`, and the Jira host from the first
`https://<host>/browse/` link it finds in `story.md`, `epic.md` or
`{ISSUEKEY}-context.md`.

Ordering follows `index.md`, which keeps the published order equal to
checklist order. Files missing from `index.md` are appended in natural
id order and reported as a warning.

Field-by-field rules — see [references/field-mapping.md](references/field-mapping.md).

## Publish Mode

| Mode | Behaviour |
|---|---|
| `create` | Always create. Warn on any title already present in the folder. |
| `update` | Update named cases only. Requires a `test_case_identifier` per case. |
| `upsert` | Match on exact title within the target folder — update if found, create if not. |

Default to `create` for a folder with no cases, and `upsert` for a folder
that already holds cases. State which mode is in effect in the preview;
never switch mode silently.

For `upsert` and for the `create` duplicate check, call `listTestCases`
with `folder_id` and match titles exactly. Report partial matches as
warnings — never treat a partial match as the same case.

`updateTestCase` takes `test_case_identifier` (the BrowserStack
`TC-NNN`), not the local `TC-REQ-N.M`. Get it from `listTestCases`.

## Issue Linking Is Not Available in PR-3

`createTestCase` rejects `issue_tracker` in project PR-3 with
`Invalid issue tracker` — Jira is not connected as an issue tracker
there, and every pre-existing case in the project has `issues: []`.

So for PR-3, convert with `--no-issues`. Traceability is unaffected:
the `story:`/`epic:`/`req:`/`tc:` tags and the `description` line carry
it. Do not retry the call with `issue_tracker` — the failure is a
project configuration gap, not a transient error.

Re-check this if Jira is later connected under the project's
integrations. Cases already published can be backfilled with
`updateTestCase` — they do not need recreating.

## Traceability

BrowserStack assigns its own identifiers (`TC-705`, `TC-706`, …), so the
local ids would otherwise be lost. Every published case carries them in
two places:

- `tags`: `req:REQ-6` and `tc:TC-REQ-6.1`, alongside
  `epic:{EPIC-KEY}`, `story:{STORY-KEY}`, `priority:{level}` and
  `MCP Generated`
- `description`: `REQ-6: <requirement text> | Technique: ... | Source: TC-REQ-6.1 (file)`

Do not drop these. 06-qa-code-review keys its results off `REQ-*`, and
without the tags a published case cannot be traced back to a
requirement.

## What Does Not Transfer

State these in the preview so the user knows what stays local:

- **`index.md` structure** — the per-requirement grouping, the
  "Applied techniques" lines and the statistics block have no
  BrowserStack equivalent.
- **Structural requirements** — requirements that 04-qa-test-cases
  covered by checklist only produce no case file and therefore nothing
  to publish. They remain visible only in the local checklist.
- **"Needs clarification" notes** — a requirement flagged in `index.md`
  with no generated case publishes nothing.
- **Per-step test data as a field** — BrowserStack steps have only
  `step` and `result`. Test data is folded into the step sentence
  (default) or listed in preconditions.
- **Postcondition as a field** — appended to `preconditions` under a
  `Postconditions:` heading.

## Verification Before Publishing

Before showing the preview, confirm:

- Every `TC-*.md` in the folder appears in the payload, or is explicitly
  excluded by `--only` and named in the preview.
- Every payload element has a non-empty `name` and at least one step
  with a non-empty `result` — `createTestCase` requires steps.
- `project_identifier` is a `PR-N` value, and `folder_id` came from
  `listFolders` or `createProjectOrFolder`, not from a URL.
- The payload case count matches the `index.md` statistics block, or the
  difference is explained.
- No warning from `--validate-only` is left unmentioned.

## Preview and Confirmation

Show the preview table from
[references/templates.md](references/templates.md) and stop.

Proceed only on an explicit **confirm publish**. Anything else — a
question, a partial answer, silence — is not confirmation. If the user
asks for changes, re-convert and show the preview again.

## Execute

- Create with `createTestCase`, one call per case, in payload order.
- Update with `updateTestCase`, passing only the fields that change.
- On a failure, do not roll back silently and do not retry the same call
  blindly. Stop after the failing case, keep what already succeeded, and
  report exactly which cases got through.

## Final Response

After publishing, report:

- Target project and folder, with the folder URL
- Cases created, with the BrowserStack ids assigned
- Cases updated, with their ids
- Cases failed, with the error text
- What stayed local, per "What Does Not Transfer"

Report templates — [references/templates.md](references/templates.md).

## What This Skill Does Not Do

- Draft or renumber test cases — that is 04-qa-test-cases.
- Read requirements from Jira — that is 01-task-context.
- Create test runs or executions.
- Publish without a preview and an explicit confirmation.
