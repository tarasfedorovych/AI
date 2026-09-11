# Field Mapping Reference

How a `TC-REQ-N.M.md` file from 04-qa-test-cases becomes
`createTestCase` arguments. The converter script
(`scripts/tc_to_browserstack.py`) implements every rule here — this file
documents them so the output can be reviewed and the script can be
changed with intent.

---

## Source Format

04-qa-test-cases writes one file per case, with no frontmatter:

```markdown
# TC-REQ-6.1: Viewer opens a Draft practice by direct URL — 404 page

Requirement: REQ-6 — AC-2 (Access Restriction): If a Viewer accesses a Draft or Archived practice via direct URL, the system returns a 404 page.
Applied technique: EP, Use Case

**Precondition:** User is authenticated via SSO with the Viewer role. A practice with status Draft exists: "RAG Pipeline Setup" [test data], and its direct URL is known.

| # | Step | Test Data | Expected Result |
|---|------|-----------|------------------|
| 1 | Open the direct URL of the Draft practice | Direct URL of "RAG Pipeline Setup" [test data] | A 404 page is displayed |
| 2 | Check the page for content of the Draft practice | — | None of the Draft practice's content is displayed |

**Postcondition:** <present only when the case changes state>
```

---

## Field Map

| Source | BrowserStack field | Transformation |
|---|---|---|
| `# TC-REQ-6.1: <scenario name>` | `name` | Scenario name only. The `TC-REQ-6.1` part goes to tags and description, never to `name`. |
| `Requirement:` line | `description` | `REQ-6: <requirement text>` |
| `Applied technique:` line | `description` | Appended as `Technique: EP, Use Case` |
| filename + local id | `description` | Appended as `Source: TC-REQ-6.1 (TC-REQ-6.1.md)` |
| `**Precondition:**` block | `preconditions` | Sentence-split into `<ol><li>` — see below |
| Table `Step` column | `test_case_steps[].step` | Verbatim |
| Table `Test Data` column | `test_case_steps[].step` | Appended as ` (Test data: …)` — see below |
| Table `Expected Result` column | `test_case_steps[].result` | Verbatim |
| `**Postcondition:**` block | `preconditions` | Appended under a `Postconditions:` heading |
| story / epic folder names | `tags`, `issues` | `story:AISD-7`, `epic:AISD-5`; `issues: ["AISD-7", "AISD-5"]` |
| `Requirement:` id | `tags` | `req:REQ-6` |
| local case id | `tags` | `tc:TC-REQ-6.1` |
| — | `template` | Always `test_case_steps` |
| — | `case_type` | `Functional` (override with `--case-type`) |
| — | `priority` | `Medium` (override with `--priority`) |
| — | `automation_status` | `not_automated` |

`#` (the step number column) is dropped — BrowserStack numbers steps by
array position.

---

## Fields the Source Does Not Carry

04-qa-test-cases emits no priority, type or automation metadata, by
design: those are publication concerns, not test-design concerns. They
are therefore **defaults applied at publish time**, not data recovered
from the file.

| Field | Default | Why |
|---|---|---|
| `priority` | `Medium` | BrowserStack's own project default. Set `--priority` when the whole story warrants a different level. |
| `case_type` | `Functional` | Every case the pipeline generates is behavioural. |
| `automation_status` | `not_automated` | Nothing in this pipeline generates automation. |
| `owner` | unset | Set `--owner` to attribute cases; otherwise BrowserStack uses the API account. |

Per-case priority is not supported. If a story needs mixed priorities,
publish in two passes with `--only` and different `--priority` values.

---

## Preconditions Formatting

The source precondition is one prose paragraph, not a list. It is split
into sentences and wrapped in `<ol><li>`, matching the shape of cases
already in this BrowserStack project.

Splitting happens on `. ` followed by a new sentence, and is suppressed
after known abbreviations (`e.g`, `i.e`, `etc`, `vs`, …) so a wording
like "e.g. Slow 3G" is not torn in half. Wording is never altered — only
the split points are inferred.

### Input

```markdown
**Precondition:** User is authenticated via SSO with the Viewer role. A practice with status Draft exists: "RAG Pipeline Setup" [test data], and its direct URL is known.
```

### Output

```html
<ol>
<li>User is authenticated via SSO with the Viewer role.</li>
<li>A practice with status Draft exists: &quot;RAG Pipeline Setup&quot; [test data], and its direct URL is known.</li>
</ol>
```

Text is HTML-escaped; the wrapper tags are not.

### Fenced code blocks

A precondition may carry a fenced block — for example a markdown sample
the case is about. Fences are lifted out before sentence splitting and
re-emitted as `<pre><code>` after the list, so code never gets split on
a period. Nested fences (a ```` ```` ```` block wrapping a ``` ``` ```
one) are handled: the closing fence must be at least as long as the
opener.

```html
<ol>
<li>Published practice whose article body contains a fenced code block with a declared language [test data]:</li>
</ol>
<pre><code>```javascript
// build the client
const client = new Client(&quot;token&quot;);
```</code></pre>
```

---

## Test Data Placement

A BrowserStack step has exactly two fields, `step` and `result`. The
pipeline's `Test Data` column is per-step, so folding it into the step
sentence is the only placement that keeps the association.

`--test-data step` (default):

```json
{
  "step": "Authenticate via SSO with the Viewer account (Test data: viewer.user@example.com [test data])",
  "result": "Authentication succeeds and the application opens"
}
```

`--test-data preconditions` — collected instead into a block, for
reviewers who want all data visible before executing:

```html
<p><strong>Test Data:</strong></p>
<ul>
<li>Step 2: viewer.user@example.com [test data]</li>
</ul>
```

`--test-data both` writes it in both places.

Cells holding `—`, `-`, `n/a` or nothing are treated as empty and
produce no annotation.

---

## Postconditions

`**Postcondition:**` is present only on cases that change state.
BrowserStack has no postcondition field, so it is appended to
`preconditions`:

```html
<p><strong>Postconditions:</strong></p>
<ol>
<li>The Viewer account is authenticated in the application.</li>
</ol>
```

---

## Tags

Emitted in this order, matching the convention of cases already in the
project:

| Tag | Source |
|---|---|
| `priority:medium` | the `--priority` value, lowercased |
| `epic:AISD-5` | epic folder name |
| `story:AISD-7` | story folder name |
| `req:REQ-6` | `Requirement:` line |
| `tc:TC-REQ-6.1` | H1 heading |
| `MCP Generated` | fixed marker |

`req:` and `tc:` are the traceability contract. 06-qa-code-review keys
its results off `REQ-*`; without them a published case cannot be traced
back to a requirement or to its local file.

---

## Issue Linking

Story key first, then epic key, so BrowserStack links trace the full
hierarchy:

```json
{
  "issues": ["AISD-7", "AISD-5"],
  "issue_tracker": { "name": "jira", "host": "https://hannakhivrenko.atlassian.net" }
}
```

The host is read from the first `https://<host>/browse/` link found in
`story.md`, `epic.md` or `{ISSUEKEY}-context.md`. If no link is found,
`issue_tracker` is omitted and `issues` is still sent. `--no-issues`
skips both.

---

## Ordering

Publication order follows the `[TC-…](TC-….md)` links in `index.md`,
which is checklist order, which is requirements order. This keeps
`TC-REQ-7a.1` before `TC-REQ-7b.1` and `TC-REQ-9.2` before
`TC-REQ-10.1` — neither of which plain filename sorting gets right.

Files absent from `index.md` are appended in natural id order and
reported as a warning. Ids listed in `index.md` with no matching file are
also warned about.

---

## Warnings the Script Raises

Each is written to stderr and, with `--validate-only`, makes the exit
code 1:

| Warning | Meaning |
|---|---|
| `no `# TC-...: name` heading found` | File is not a case file, or the heading was edited |
| `no `Requirement: REQ-N — ...` line found` | Traceability tags cannot be built |
| `no step rows parsed` | `createTestCase` would reject the payload |
| `step N has no expected result` | Not a verification — fix the case first |
| `skipped table row with N columns` | Malformed step table |
| `index.md lists X but no file was found` | Stale index, or a deleted case file |
| `X is not listed in index.md` | Case file left over from an earlier run |

---

## Not Mapped

| Source | Why |
|---|---|
| `index.md` groupings and statistics | No BrowserStack equivalent |
| "Applied techniques" per requirement heading | Carried per case in `description` instead |
| Structural requirements (checklist-only) | No case file exists to publish |
| "Needs clarification" notes | No case file exists to publish |
| Step `#` column | BrowserStack numbers by array position |
