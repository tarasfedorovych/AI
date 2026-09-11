---
name: 06-qa-code-review
description: Stage 6 of the QA pipeline. Takes the test cases created by the 04-qa-test-cases skill and the PR summary created by the 05-pr-summary skill, verifies each test case against the PR code, and produces a compact results file with PASS/FAIL/QA/N-A statuses and findings. Use when the user says "verify test cases against the PR", "QA code review", "check implementation against test cases", or after 05-pr-summary completes. This is the QA-pipeline verification stage — not a general-purpose code quality review.
---

# QA Code Review

Verifies each test case against the PR code. Output is a
compact results table with findings for FAIL points.

## Input Data

Inputs, all read from the story folder:
1. Test cases in `test-cases/` created by 04-qa-test-cases —
   `index.md` plus one `TC-*.md` file per test case.
2. PR summary file `<ISSUEKEY>-pr-summary.md` created by
   05-pr-summary.
3. PR URL or branch name — from the user.

Read `test-cases/index.md` first for the REQ grouping and the full
case list, then read the `TC-*.md` files. Verify every case listed in
the index against the code — the index is the authoritative list, so
a case missing its file is a gap to report, not a case to skip.

## Story Folder

All file inputs and outputs live in the story folder built by
01-task-context:

```
stories/**/{ISSUEKEY}/
```

Locate it by globbing `stories/**/{ISSUEKEY}/` — one glob matches both
`stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

If the folder does not exist, or `test-cases/` holds no case files, or
`{ISSUEKEY}-pr-summary.md` is absent — stop and tell the user which
earlier stage to run. Do not create the structure here, and do not
fall back to the working directory.

> ⚠️ **CONFIGURE:** specify PR URL format in your system.
> Examples: `https://github.com/owner/repo/pull/123` for GitHub,
> `https://gitlab.com/owner/repo/-/merge_requests/123` for GitLab.

If any file is not provided — ask before starting.
If neither PR URL nor branch name is provided — ask.

If user provides branch name instead of PR — work
with the branch directly via CLI or API. Don't search for PR by branch.

Data sources for this skill:
- test-cases file — source of checks
- pr-summary file — navigation map for PR
- PR code via CLI or API — source of evidence

All files — read-only.
Don't modify, rewrite, or clear their content.

If test-cases file is missing — stop and inform
user that 04-qa-test-cases skill must be executed first.

If pr-summary file is missing — work without it.
Search for test case implementation in PR directly via CLI or API.

Don't access tracker, use external tools,
search the internet, or use browser.

## Rules

- All communication and output file content — in English.
- Chat messages — concise.
- Read-only: don't modify code, create commits, push,
  don't create PR comments, reviews, labels, or statuses.
- Work only within PR branch or specified branch.
  Don't take code from main, base branch, other branches,
  or general repository context.
- Verify only test cases from file. Don't invent,
  don't interpret requirements on your own.
- Don't evaluate code quality, style, architecture, naming,
  tests, CI, or refactoring — unless described
  in test case.
- Don't search for bugs unrelated to test cases.
- Don't analyze pre-existing code unchanged in PR.
- If test case cannot be verified by code —
  mark as QA, don't guess result.

## Code Access

> ⚠️ **CONFIGURE:** describe how skill accesses PR and code.
> Specify concrete tools and commands for your system.
>
> Examples:
> - **GitHub → gh CLI:** `gh pr view`, `gh pr diff`, `gh api`
> - **GitLab → glab CLI:** `glab mr view`, `glab mr diff`
> - **Bitbucket → bb CLI or REST API**
> - **Azure DevOps → az devops CLI or REST API**
>
> Always add rule: if CLI unavailable —
> stop and inform user. Don't use
> workarounds (browser, curl) as substitutes.

### Recommended Flow

> ⚠️ **CONFIGURE:** describe step-by-step flow for reading PR code.
> Below — example for GitHub + gh CLI.

**PR mode (PR URL provided):**

1. Parse PR URL → owner, repo, number.
2. Get PR metadata:
   ```
   gh pr view <URL> --json title,state,headRefName,headRefOid,baseRefName,files
   ```
3. For each test case, use PR summary
   to determine where to search. Read diff or full file
   only for relevant files:
   ```
   gh pr diff <URL> -- <filepath>
   ```
4. When diff is insufficient and full file content needed
   from PR branch:
   ```
   gh api -H "Accept: application/vnd.github.raw" "repos/{owner}/{repo}/contents/{path}?ref={head_branch}"
   ```

**Branch mode (branch name without PR):**

1. Ask user for owner/repo if unclear
   from context. Base branch — `main`, unless user
   specified otherwise.
2. Get specific file diff:
   ```
   gh api "repos/{owner}/{repo}/compare/main...{branch}" --jq '.files[] | select(.filename=="{path}") | .patch'
   ```
3. Full file content from branch:
   ```
   gh api -H "Accept: application/vnd.github.raw" "repos/{owner}/{repo}/contents/{path}?ref={branch}"
   ```

Read files only from PR head branch.
Don't read files from base branch, main, or other branches.

### PR Summary as Navigation

PR summary shows which files changed and what's in them.
Use it to quickly find where in PR specific test case
is implemented.

If test case implementation not found
in files listed in PR summary — search PR directly
via CLI or API. PR summary may be incomplete — that's
not reason to set FAIL.

### If CLI Unavailable

Stop. Don't use git clone, curl, browser,
or other tools as substitute. Inform user
to install and authorize CLI.

> ⚠️ **CONFIGURE:** specify exact authorization command
> for your CLI. Example: `gh auth login` for GitHub.

### Large PRs

If more than 20 files changed:
- Use PR summary as navigation map —
  don't read files blindly.
- Group test cases by files: read file once
  and verify all test cases affecting it.
  Don't reread file for each test case.
- Configs, styles, tests — read only if there's
  direct test case for them.

## Review Process

For each test case (TC-REQ-X.Y):

1. **Understand** — what scenario describes test case:
   precondition, steps, expected result.
2. **Find** — use PR summary to determine which files
   are relevant. Read diff or full file.
3. **Assess** — whether code implements behavior described
   in test case. Compare expected result
   of each step with what code does.
4. **Classify** — set status.

### What to Look for in Code

- Presence of elements: components, fields, buttons, labels,
  texts, messages, tooltips.
- Condition logic: if/else, switch, guard clauses, permissions,
  feature flags.
- States: default, active, disabled, error, loading, empty.
- Validations: rules, messages, triggers, boundary values.
- Data: fields, formats, mappings, API contracts, models.
- Removals: whether what should be removed is actually removed.
- UI binding: whether element is connected to correct
  template, route, component, screen.

### FAIL vs Missing in Diff

Missing code in diff ≠ automatic FAIL.
Code may already exist in branch without changes.
Before setting FAIL — check full file
from PR branch via CLI or API.

FAIL only when there's specific evidence:
- code does something different than test case expects
- code deletes or breaks what should work

## Classification

Each test case gets one status:

- `PASS` — code confirms behavior described
  in test case is implemented.
- `FAIL` — code shows behavior not implemented,
  implemented incorrectly, or contradicts expectations.
- `QA` — cannot verify by code alone. Requires
  manual verification: runtime behavior, visual
  layout, real data, integrations, permissions.
- `N/A` — point not applicable to this PR.
  Code related to this requirement missing from PR.

Rules:
- Don't set PASS if you have doubts — use QA instead.
- Don't set FAIL without specific evidence from code.
- Don't set N/A without specific evidence from code.
- QA is normal status. Many UI/UX and runtime
  checks cannot be confirmed by code alone.

## Output File

Create file `<ISSUEKEY>-code-review.md` in the story folder:

```
stories/**/{ISSUEKEY}/{ISSUEKEY}-code-review.md
```

The next skill reads it from the same folder.

If file already exists — delete completely and create new.

Output template structure — in references/output-template.md.

## Verification Before Saving

Before saving, verify:

- Number of test cases in results table equals
  number of TC-REQ in test cases file. If mismatch —
  find missing and add to save.
- Order of test cases in table matches
  order in test cases file.
- Each FAIL has corresponding entry in Findings
  with specific file and line.
- Each N/A has corresponding entry in Findings with reason.
- No FAIL without evidence from code.
- No N/A without evidence from code.

## Final Response

After saving file, inform:
- Path to saved file
- PASS / FAIL / QA / N/A counters
