---
name: 01-task-context
description: Stage 1 of the QA pipeline. Collects task data from Jira, matches information from all fields (description, comments, attachments), and forms a unified enriched Markdown context — the source of truth for the later pipeline skills. Use when the user gives a Jira issue URL or key (e.g. AISD-7, https://hannakhivrenko.atlassian.net/browse/AISD-7), or says "extract context from Jira", "prepare task context", "process ticket", "task context".
---

# Task Context

Collects task data from tracker, matches information
from all fields, and forms a unified enriched Markdown context — source of truth
for subsequent skills in the chain.

## Input Data

From the user, need:
1. URL or task key in the tracker

Accepted forms:
- Issue key: `AISD-7` — pattern `<PROJECT>-<number>`, project key
  uppercase.
- Browse URL: `https://hannakhivrenko.atlassian.net/browse/AISD-7` —
  take the key from the last path segment.

Both resolve to the same issue key. Everything downstream uses the key.

## Rules

- All communication with user and all handoff content — in English.
- Chat messages — brief. Do not paste raw tracker responses.
- Do not clarify or groom requirements. This skill only collects
  and structures tracker data as is. Output file — source of truth
  for all subsequent skills in the chain.
- Ask user only about operational blockers: unavailable
  attachments, read errors.
- Concise bullets, no filler.

## Tracker Access

Tracker: **Jira Cloud** at `https://hannakhivrenko.atlassian.net`.

Access via the `jira` MCP server (local `uvx mcp-atlassian`, stdio).
Tools used by this skill:

| Purpose | Tool |
|---|---|
| Read the issue | `mcp__jira__jira_get_issue` |
| Attachment images | `mcp__jira__jira_get_issue_images` |
| Other attachments | `mcp__jira__jira_download_attachments` |

Mandatory rule: if the integration is unavailable — stop and inform
the user. Do not use workarounds (browser, internet search,
`WebFetch` on the browse URL) as a replacement.

Two failure modes to report distinctly, because the fixes differ:
- **Server not connected** — the `mcp__jira__*` tools are absent.
  Infrastructure problem; the user restarts or reconnects the server.
- **Connected but the issue is unreadable** — an "issue not found"
  error, or reads that return zero projects and zero issues. This is
  an access problem, not a wrong key. Report it as such so the user
  checks account permissions rather than re-checking the key.

Do not fall back to the `MCP_DOCKER` gateway. Its Atlassian server
was retired from this pipeline: it authenticated successfully but the
account had no project visibility, which produced empty results that
read like an empty ticket.

### Effective Usage

One call retrieves every field in the map:

```
mcp__jira__jira_get_issue
  issue_key     = <ISSUEKEY>
  fields        = summary,description,attachment,issuelinks,parent,issuetype
  include       = comments
  comment_limit = 100
```

Do not use `fields=*all`. It returns the management fields that
references/field-maps.md excludes and inflates the payload.

### Recommended Flow

1. Parse the input → extract the issue key.
2. Read the issue with the call above.
3. Determine the issue type from `issue_type.name` in the response.
4. Load the field map for that type from references/field-maps.md.
5. Parse `description` into its subsections — the section table in
   references/field-maps.md maps each heading to an output section.
   All requirement content lives here; this project has no custom
   Acceptance Criteria field.
6. Attachments — see the Attachments section below.
7. Related issues (`issuelinks`, `parent`, and the keys named under
   `## Story Dependencies`) — record what they are and why they
   matter for the current task. Their own requirements do not belong
   in this file. Read a related issue only if the current ticket is
   unintelligible without it, and even then only for context.
8. Collect and match, then verify.
9. Resolve the output path and build the folder structure — see
   "Output Location". This may need one extra Jira read for the
   parent Epic (and Feature, where that level exists) when its
   description file is absent.
10. Write `{ISSUEKEY}-context.md` and `story.md`.

## Task Types and Fields

Types in project AISD: **Epic**, **Story**, **Task**, **Bug**,
**Subtask**. Identify the type from `issue_type.name` in the
`jira_get_issue` response.

All five share an identical field schema, so the field map differs
only in how the type is treated, not in which fields exist.

1. Determine task type from tracker response.
2. Load field map for this type from references/field-maps.md.
3. Read only fields listed in the map. Ignore other fields.
4. Do not reopen field maps every time —
   they are fixed for your project.

## Empty Fields

Mandatory field to process — task description
(according to references/field-maps.md).

For every type in this project — Epic, Story, Task, Bug, Subtask —
the mandatory field is `description`. There is no separate
steps-to-reproduce or bug-description field; a Bug states its
reproduction inside `description` like any other type.

If mandatory field is empty or missing — stop
and inform user that there is nothing to process, need
to add description to the ticket.

All other fields — optional. Collect everything that is filled,
skip empty fields. Complete field list for each task type
is in references/field-maps.md.

## Attachments

This MCP gives **direct access to attachment content** — no upload
request needed in the normal case:
- `mcp__jira__jira_get_issue_images` returns image attachments as
  inline images, ready to read.
- `mcp__jira__jira_download_attachments` returns all attachments as
  base64 embedded resources.

Note: the `attachment` field is omitted from the `jira_get_issue`
response entirely when the issue has no attachments. An absent key
means none exist — it is not a read error, and needs no mention to
the user.

Flow:
1. Collect list of attachments from task metadata.
2. Determine supported for processing:
   - images: png, jpg, jpeg, gif, webp
   - markdown: md, markdown
   - PDF: pdf
3. Fetch supported attachments directly with the tools above —
   images via `jira_get_issue_images`, the rest via
   `jira_download_attachments`. Do not ask the user to upload files
   that the MCP can already retrieve.
4. Extract information and add to appropriate context sections.
5. Video (mp4, mov, webm, avi, mkv) — Claude cannot
   view. Record in context as available
   but not processed.
6. Only if a fetch fails — ask the user to upload that specific file
   to chat. If they skip it, record the attachment in context as
   available but not processed.

## Data Collection and Matching

This step is performed after receiving all data:
fields, comments, and attachments from the user.

Match data between each other and form a unified enriched context.

Principle:
- Go through all filled task fields.
- Compare data across fields: comments may supplement
  description, attachments may detail steps, acceptance
  criteria may clarify requirements from description.
- If one field has detail missing from another —
  add it to the appropriate context section.
- If attachments (screenshots, mockups, md-files) provide
  specifics that expand description — integrate this information.
- Result: one file where everything is collected, deduplicated,
  and organized by sections. Not separate data from fields,
  but a coherent picture of the task.

Processing comments:
- Comments — same data source as description
  or acceptance criteria.
- If comment supplements or clarifies existing requirement —
  integrate into Requirements section.
- If comment describes issue not in requirements —
  add as additional requirement in section
  "Additional Requirements (from comments)" under main requirements.
- Everything else (bugs in existing requirements, test status,
  process discussion) — ignore.

Prohibitions — violation of any of these makes handoff unusable:
- Do not change essence, wording, or meaning of requirements.
- Do not change validation rules, validation messages,
  validation trigger conditions.
- Do not simplify or generalize specific values: numbers,
  limits, ranges, sizes, thresholds, units.
- Do not replace exact names, labels, copy, statuses, states,
  roles, permissions with generic wording.
- Do not skip before/after values when changing — keep
  both sides.
- Do not assume, make logical conclusions, do not add
  information not in any task field.
- Do not combine different requirements into one if in tracker
  they are described separately.
- Do not change conditional logic: keep all condition branches
  (if/then/else) as in tracker.
- Do not break links between requirements: if one
  requirement depends on another (field on state, action on condition,
  rule on role) — keep this link in one place.

## Verification Before Saving

Before saving, go through each filled field
from references/field-maps.md list and verify:

- Does each fact, requirement, and detail from this field
  end up in the appropriate context section?
- Did nothing get skipped because it seemed
  familiar, repeated, or unimportant?

If missing information is found — add it
to the appropriate section before saving.

## Output Location

This skill owns the folder structure. Later pipeline skills only
locate it — they never create it.

### Resolve the Path

From the issue's parent chain:

1. Read `parent` from the `jira_get_issue` response.
2. Parent is an **Epic** → `stories/{EPIC-KEY}/{ISSUEKEY}/`
3. Parent is **not** an Epic (a Feature-level container) → that key is
   `{FEATURE-KEY}`. Read that issue to get its own parent Epic →
   `stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`
4. Issue has **no parent** → `stories/no-epic/{ISSUEKEY}/`
5. The requested issue **is itself an Epic** → `stories/{ISSUEKEY}/`,
   and write only `epic.md`. There is no story folder to build.

Project AISD has no Feature issue type, so branch 3 does not occur
there. Keep it for projects that add an intermediate level.

### Build the Structure

Create folders and files that do not yet exist:

```
stories/
  {EPIC-KEY}/
    epic.md                   ← Epic description
    [{FEATURE-KEY}/
      feature.md              ← Feature description
    ]
    {ISSUEKEY}/
      {ISSUEKEY}-context.md   ← Source of truth
      story.md                ← Formatted story
      test-cases/             ← filled by 04-qa-test-cases
      tasks/                  ← placeholder
```

Write rules — these differ per file, do not apply one blanket rule:

| File | On every run |
|---|---|
| `{ISSUEKEY}-context.md` | Create or overwrite |
| `story.md` | Create or overwrite |
| `epic.md` | Create only if absent — never overwrite |
| `feature.md` | Create only if absent — never overwrite |
| `test-cases/`, `tasks/` | Create if absent, leave empty |

`epic.md` and `feature.md` are never overwritten because a human may
have expanded them. If absent, read that issue from Jira
(`fields=summary,description`) and write key, summary, browse URL and
description.

Place a `.gitkeep` in `test-cases/` and `tasks/` when creating them —
git does not track empty directories, so the placeholders would
otherwise vanish on commit.

## Output File — {ISSUEKEY}-context.md

Source of truth for all subsequent skills.

If the file already exists — delete it completely and create a new one.
Always output one file with results from the latest run.
Do not merge with the previous version, do not append, do not preserve
data from the previous record.

Before finishing, verify:
- One top-level heading
- One coherent handoff without duplicate sections
- All prohibitions from "Data Collection and Matching" are followed
- Do not create sections that are not in references/output-template.md
- Do not include estimation, story points, sprint, assignee,
  work dates or other project management data

File structure template is in references/output-template.md.

## Output File — story.md

A human-readable rendering of the same ticket. Derived **strictly**
from `{ISSUEKEY}-context.md` — it adds no information that the
context file does not already carry, and every prohibition from
"Data Collection and Matching" applies unchanged.

Include only the sections the ticket actually has:

```markdown
# {ISSUEKEY} — {Summary}

[Open in Jira]({browse_url})

## User Story
As a <role>, I want <goal>, so that <benefit>.

## Business Rules
- BR-NNN: <text>

## Preconditions
- <text>

## Acceptance Criteria
### <subheading, e.g. Happy Path>
- AC-N: <text>

## Design Checklist
- <text>

## Open Questions
- SQ-<AREA>-NNN: <text>
```

Story dependencies and linked issues stay in the context file's
Related Context section — do not repeat them here.

## Final Response

After saving, inform:
- The story folder path, and which files were created versus
  overwritten versus left untouched
- If anything was skipped (attachment fetch failed, field was
  unavailable) — briefly remind what exactly did not make it
  into context.
