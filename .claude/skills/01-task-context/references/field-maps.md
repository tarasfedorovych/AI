# Field Maps

Fixed field maps for project **AISD** (`AI-SDLC Sandbox`) on
`https://hannakhivrenko.atlassian.net`. Do not reopen these maps
every time — use as is.

Verified against the live project create schema and against
AISD-7 and AISD-6.

## Key Fact About This Project

This is a team-managed Jira project with **no custom content fields**.
All five issue types (Epic, Subtask, Task, Story, Bug) share an
identical field schema.

There is **no** dedicated `Acceptance Criteria`, `User Story`,
`Steps to Reproduce`, or `Notes for QA` custom field. All QA-relevant
content lives inside `description` as a structured markdown document.
Read the description in full and parse its subsections — see
"Description Subsections" below.

## Story / Task / Bug

Same table applies to all three — the schema is identical.

| Value | Field Key | Mandatory |
|---|---|---|
| Name | `summary` | — |
| Description (all requirement content) | `description` | yes |
| Comments | `comment` | no |
| Attachments | `attachment` | no |
| Linked issues (related context only) | `issuelinks` | no |
| Parent epic (related context only) | `parent` | no |

## Epic / Subtask

Same field keys as above. Mandatory field remains `description`.

Epics in this project are containers (AISD-5 `Practice Page` is the
parent of AISD-7). When the requested issue is an Epic, its own
`description` is the mandatory field; child issues are not pulled in.

## Description Subsections

`description` is markdown with `##` section headings. Not every
heading appears on every ticket — collect the ones present, skip the
rest. Observed headings, with the identifier convention each uses:

| Heading | Identifiers | Maps to output section |
|---|---|---|
| `## User Goal` | As a / I want to / So that | Goal |
| `## Business Rules` | `BR-NNN` | Requirements |
| `## Preconditions` | — | Requirements |
| `## Acceptance Criteria` | `AC-N` | Requirements |
| `## Design Checklist` | `DG-NNN` | Requirements |
| `## Story Dependencies` | issue keys + reason | Related Context |
| `## Open Questions` | `SQ-<AREA>-NNN` | Requirements |

`## Acceptance Criteria` is further split by `###` subheadings.
Observed: `Happy Path`, `Edge Cases`, `Access Restriction`,
`Error Handling`. Keep each `AC-N` as its own bullet and preserve
which subheading it came from.

`## Story Dependencies` may be a table (`|Depends on|Reason|`) or the
literal text `None (foundation story, can start immediately).` — in
the latter case there is no dependency to record.

Note on markup: descriptions come back with escaped asterisks
(`\*\*BR-026:\*`) and unbalanced emphasis markers
(`**BR-028:*`). These are source-formatting artifacts. Strip the
markup, keep the identifier and text verbatim.

## Fields Not Read

Excluded as project-management data, per the "Before finishing" rule
in SKILL.md — these must not reach the output file:

| Field | Field Key |
|---|---|
| Assignee | `assignee` |
| Story point estimate | `customfield_10016` |
| Sprint | `customfield_10020` |
| Start date | `customfield_10015` |
| Due date | `duedate` |
| Rank | `customfield_10019` |
| Team | `customfield_10001` |
| Flagged | `customfield_10021` |
| Development | `customfield_10000` |
| Restrict to | `issuerestriction` |
| Status, Priority, Reporter, Created, Updated | system fields |
| Labels | `labels` |

`issuetype` is read only to select the map above, never carried into
the output.

These three appear on issue views but are absent from the project
create schema and were empty on AISD-7. Not read. Revisit if they
start being populated:

| Field | Field Key |
|---|---|
| Vulnerability | `customfield_10033` |
| Design | `customfield_10035` |
| Agent Sessions | `customfield_10236` |

## Effective Read

One call retrieves everything in the map:

```
jira_get_issue
  issue_key    = <ISSUEKEY>
  fields       = summary,description,attachment,issuelinks,parent,issuetype
  include      = comments
  comment_limit = 100
```

Do not use `fields=*all` — it returns the excluded management fields
listed above and inflates the payload.

Caveat: `attachment` is omitted from the response entirely when the
issue has no attachments. An absent key means none exist; it is not a
read error.
