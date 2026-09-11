# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Not an application. It is a **Claude Code skill pipeline** — eight sequential QA skills
under `.claude/skills/`, each one a Markdown instruction document that Claude itself
executes. "Editing this codebase" almost always means editing prompt instructions, not code.

There is no build, no lint, and no test suite. The only executable artifact is one Python
script (below). `stories/` is generated output and is gitignored.

## Commands

The only runnable code is the BrowserStack payload converter used by stage 8:

```powershell
# validate test-case markdown, emit nothing (exit 1 on any warning) — always run this first
python .claude/skills/08-browserstack-publish/scripts/tc_to_browserstack.py `
  stories/AISD-5/AISD-6/test-cases --project PR-3 --validate-only

# emit createTestCase payloads (write to the scratchpad, never into the repo)
python .claude/skills/08-browserstack-publish/scripts/tc_to_browserstack.py `
  stories/AISD-5/AISD-6/test-cases --project PR-3 --folder <folder_id> `
  --no-issues --pretty --out <scratchpad>/bs-payload.json

# subset
... --only TC-REQ-1.1 TC-REQ-7a.1
```

`python` is 3.12; `gh` CLI is installed and authorized. `--no-issues` is required for
project PR-3 (Jira is not connected there as an issue tracker).

## Pipeline architecture

The stages communicate **only through files in the story folder** — never through chat
state. Each stage reads exactly one upstream artifact and writes exactly one, so a stage
can be run in a fresh chat as long as its input file exists.

| Stage | Skill | Reads | Writes |
|---|---|---|---|
| 1 | `01-task-context` | Jira issue (MCP) | `{KEY}-context.md`, `story.md`, `epic.md`, folder tree |
| 2 | `02-requirements-grooming` | `{KEY}-context.md` | `{KEY}-requirements.md` (assigns REQ-N) |
| 3 | `03-qa-checklist` | `{KEY}-requirements.md` | `{KEY}-checklist.md` (REQ-N.M) |
| 4 | `04-qa-test-cases` | `{KEY}-checklist.md` | `test-cases/index.md` + one `TC-REQ-N.M.md` per case |
| 5 | `05-pr-summary` | PR/branch via CLI | `{KEY}-pr-summary.md` |
| 6 | `06-qa-code-review` | `test-cases/`, `{KEY}-pr-summary.md`, PR code | `{KEY}-code-review.md` (PASS/FAIL/QA/N-A) |
| 7 | `07-web-testing` | `{KEY}-code-review.md` (QA+FAIL only), `test-cases/` | `{KEY}-web-testing.md` |
| 8 | `08-browserstack-publish` | `test-cases/` | BrowserStack Test Management (external write) |

Stages 5 and 8 branch off stage 4: 8 publishes the cases, 5→6→7 verifies them.

### Story folder

Stage 1 **owns** the folder structure. Every other stage locates it by globbing
`stories/**/{ISSUEKEY}/` (one glob covers both the two-level and the optional
Feature three-level layout) and must stop with "run stage N first" rather than create
anything or fall back to the working directory.

```
stories/{EPIC-KEY}/                     # epic.md — created only if absent, never overwritten
  {ISSUEKEY}/
    {ISSUEKEY}-context.md               # source of truth for stages 2+
    story.md                            # human-readable, derived strictly from context
    {ISSUEKEY}-requirements.md          # + checklist / pr-summary / code-review / web-testing
    test-cases/ tasks/                  # .gitkeep until real files land
```

Path resolution comes from the Jira parent chain: parent is an Epic →
`stories/{EPIC}/{KEY}/`; parent is a Feature-level container →
`stories/{EPIC}/{FEATURE}/{KEY}/`; no parent → `stories/no-epic/{KEY}/`; the issue *is*
an Epic → `stories/{KEY}/` with only `epic.md`.

## Invariants that hold across every skill

Editing one skill without honouring these breaks the handoff downstream:

- **REQ IDs are permanent.** Stage 2 assigns `REQ-1..N` (splitting into `REQ-5a`/`REQ-5b`
  where a requirement holds several things). Stages 3, 4, 6, 8 inherit them unchanged —
  `REQ-5` means the same thing everywhere, and order must match the upstream file.
- **Full overwrite, never merge.** Every output file is deleted and rewritten on each run;
  stage 4 regenerates its whole `test-cases/` folder so no orphan `TC-*.md` survives.
  The two exceptions are `epic.md`/`feature.md` (create-if-absent, a human may have
  expanded them) and `07-web-testing/navigation_paths.json` (append-only memory).
- **Upstream files are read-only.** A stage never edits what an earlier stage produced.
- **No fabrication.** Each stage's declared source is its *only* source: no tracker access
  after stage 1, no internet, no code reading in stages 2–4, no code in stage 7. Exact
  values, labels, thresholds, validation messages and if/else branches are carried
  verbatim; ambiguity is reported, never resolved into fact.
- **Stop after saving.** A skill does not chain into the next stage on its own.
- English for all chat output and all file content; chat messages stay brief and never
  paste raw MCP/CLI payloads.

## External integrations

- **Jira** (stage 1) — `jira` MCP server, local `uvx mcp-atlassian` over stdio, against
  `https://hannakhivrenko.atlassian.net`, project `AISD`. One `jira_get_issue` call with an
  explicit `fields=` list retrieves everything; never `fields=*all`. Do **not** fall back to
  the `MCP_DOCKER` Atlassian server — it was deliberately retired because it authenticated
  but returned zero project visibility, which looked like an empty ticket. Report
  "server not connected" and "connected but unreadable" as distinct failures.
- **BrowserStack** (stage 8) — `browserstack` MCP, local `npx @browserstack/mcp-server`.
  The API takes the `PR-N` identifier, not the numeric project id in the UI URL
  (`PR-3` = AISD / Practice Knowledge Hub, numeric `3083195`). Never write without a
  preview and an explicit *confirm publish*.
- **Chrome** (stage 7) — Claude in Chrome extension; invoke the `claude-in-chrome` skill
  first. Playwright MCP is explicitly forbidden as a substitute.
- **Git host** (stages 5–6) — via CLI (`gh`); if the CLI is unavailable the stage stops
  rather than falling back to clone/curl/browser.

When an integration is unavailable, every skill stops and tells the user. Workarounds are
prohibited by design, because a silent workaround produces plausible-looking empty output.

## Configuration state

Stages 1–4 and 8 are configured for the AISD project. Still in template form:

- `05-pr-summary/SKILL.md` and `06-qa-code-review/SKILL.md` carry `⚠️ CONFIGURE` blocks —
  the GitHub/`gh` commands in them are worked examples, not this project's settled setup.
- `07-web-testing/references/login-config.md` is unfilled placeholders, so stage 7 asks the
  user for login details at runtime; `navigation_paths.json` is still empty.

Each skill ships a `setup-guide.md` describing what to fill in and in what order —
read it before rewriting a `⚠️ CONFIGURE` section.

Project field knowledge lives in `01-task-context/references/field-maps.md`: AISD is
team-managed with **no custom content fields**, so all requirement content (Business Rules,
Acceptance Criteria, Design Checklist, Open Questions) is parsed out of `##` subsections of
`description`. That file also lists the management fields that must never reach output.

## Skill layout convention

```
.claude/skills/NN-name/
  SKILL.md            # frontmatter (name, description) + the instruction itself
  references/         # loaded on demand: output-template.md, design rules, examples
  setup-guide.md      # how to adapt the skill to another tracker/product
  scripts/            # only where deterministic work beats spending tokens (stage 8)
```

`SKILL.md` stays the decision logic; bulk detail (templates, design rules, worked examples)
belongs in `references/` so it is read only when needed.

## Loose ends

- `browserstack-publish/` at the repo root is an earlier standalone draft of the stage-8
  skill (different content, `ApprovedCaseSet` YAML input). The live skill is
  `.claude/skills/08-browserstack-publish/`; do not edit the root copy expecting effect.
- A stray `NUL` file sits at the repo root (Windows shell artifact).
