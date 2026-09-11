---
name: 05-pr-summary
description: Stage 5 of the QA pipeline. Reads a pull request via CLI or API and creates a structured summary of the changes — a navigation map of the PR for the 06-qa-code-review skill. Use when the user says "read PR", "check PR", "PR summary", "what's in PR", or after 04-qa-test-cases completes.
---

# PR Summary

Reads PR via CLI or API and creates a structured summary
of changes: which files changed, which components are affected,
what was added, deleted, and changed.

Summary — this is a navigation map for the 06-qa-code-review skill.
Code review uses it to know where in the PR to look for
implementation of each test case.

## Input Data

User needs to provide:
- PR URL or branch name.

> ⚠️ **CONFIGURE:** specify the PR URL format in your system.
> For example: `https://github.com/owner/repo/pull/123` for GitHub,
> `https://gitlab.com/owner/repo/-/merge_requests/123` for GitLab.

If neither PR URL nor branch name is provided — ask
before starting work.

If the user provides a branch name instead of PR — work
with the branch directly via CLI or API. Do not search for PR by branch.

Data sources for this skill:
- PR via CLI or API — only source.

Do not go to the tracker, do not use external tools,
do not search the internet, do not use the browser.
Do not read requirements, checklist, or test-cases files —
this skill works only with code.

## Rules

- All communication and all output file content — in English.
- Chat messages — brief.
- Read-only: do not change code, do not create commits, do not push,
  do not create PR comments, reviews, labels, or statuses.
- Work only within the PR branch or specified branch.
  Do not take code from main, base branch, or other branches.
- Describe what changed, do not evaluate how changed. Do not comment
  on code quality, style, architecture, or naming.
- Do not compare changes with task requirements. The skill does not know
  the requirements — it sees only the code.
- After saving the file — stop. Do not continue
  to code review or analysis.

## Code Access

> ⚠️ **CONFIGURE:** describe how the skill accesses the PR.
> Specify the specific tool and commands for your system.
>
> Examples:
> - **GitHub → gh CLI:** `gh pr view`, `gh pr diff`, `gh api`
> - **GitLab → glab CLI:** `glab mr view`, `glab mr diff`
> - **Bitbucket → bb CLI or REST API**
> - **Azure DevOps → az devops CLI or REST API**
>
> IMPORTANT: add a rule: if CLI is unavailable —
> stop and inform the user. Do not use workarounds (browser, curl)
> as a replacement.

### Workflow Order

> ⚠️ **CONFIGURE:** describe the step-by-step flow for retrieving data
> from PR. Below is an example for GitHub + gh CLI.

**PR Mode (PR URL provided):**

1. Parse PR URL → owner, repo, number.
2. Get PR metadata:
   ```
   gh pr view <URL> --json title,state,headRefName,headRefOid,baseRefName,files
   ```
3. Get list of changed files:
   ```
   gh pr diff <URL> --name-only
   ```
4. For each file, get the diff:
   ```
   gh pr diff <URL> -- <filepath>
   ```
   Read files one by one, not the entire diff at once.
5. If the diff is insufficient to understand the changes — read
   the full file from the PR branch:
   ```
   gh api -H "Accept: application/vnd.github.raw" "repos/{owner}/{repo}/contents/{path}?ref={head_branch}"
   ```

**Branch Mode (branch name without PR):**

1. Ask the user for owner/repo if unclear
   from context. Base branch is `main`, unless the user
   specified another.
2. Get list of changed files:
   ```
   gh api "repos/{owner}/{repo}/compare/main...{branch}" --jq '.files[].filename'
   ```
3. Get diff for a specific file:
   ```
   gh api "repos/{owner}/{repo}/compare/main...{branch}" --jq '.files[] | select(.filename=="{path}") | .patch'
   ```
4. Full file content from the branch:
   ```
   gh api -H "Accept: application/vnd.github.raw" "repos/{owner}/{repo}/contents/{path}?ref={branch}"
   ```

Read files only from the PR's head branch.
Do not read files from base branch, main, or other branches.
Do not take code from the repository's general context.

### Large PR

If more than 20 files changed — do not read the diff for each one.
Read the diff only for key files (components, logic,
API). Configs, styles, tests — describe by file name
without the diff.

### If CLI Unavailable

Stop. Do not use git clone, curl, browser,
or other tools as a replacement. Inform the user to
install and authorize the CLI.

> ⚠️ **CONFIGURE:** specify the exact authorization command
> for your CLI. For example: `gh auth login` for GitHub.

## What to Describe for Each File

For each changed file, determine:

- **Category:** component, API/endpoint, model/type,
  utility, style, config, test, migration, or other.
- **What Changed:** briefly — what was added, deleted, or
  modified. Do not rewrite code, describe the essence of changes.
  Specify specific names of functions, components, hooks,
  endpoints that are changed or added.

If multiple files change one entity (component +
its styles + its test) — group them under that entity.

## Verification Before Saving

Before saving, verify:

- Each changed file from PR is present in the summary.
  Compare the number of files in the change list with the number
  of files in the summary.
- Category is defined for each file.
- Change descriptions are concise and specific — not "file changed",
  but "added region parameter to filterLeads function".

## Story Folder

Output goes to the story folder built by 01-task-context:

```
stories/**/{ISSUEKEY}/
```

Locate it by globbing `stories/**/{ISSUEKEY}/` — one glob matches both
`stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

This skill takes a PR, not a story file, so the issue key does not
come from its input. Take it from the story under work in this chat.
If it is not established, or the glob finds no folder — ask the user
for the issue key rather than guessing from the PR title or branch
name. Do not create the structure here, and do not fall back to the
working directory.

## Output File

Create file `<ISSUEKEY>-pr-summary.md` in the story folder:

```
stories/**/{ISSUEKEY}/{ISSUEKEY}-pr-summary.md
```

The next skill reads it from the same folder.

If the file already exists — delete it completely and create a new one.

File structure template is in references/output-template.md.

## Final Response

After saving the file, inform:
- Path to the saved file
- Number of changed files
