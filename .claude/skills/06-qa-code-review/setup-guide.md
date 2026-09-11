# QA Code Review Skill Setup Guide

This skill checks test cases against PR code. Review logic
(classification, what to search for, process) — universal. Only need to configure
the way to access the PR and code.

## What you need to know before setup

### 1. What is your version control system?

GitHub, GitLab, Bitbucket, Azure DevOps or other.

### 2. How will AI get access to PR code?

Options:
- **CLI** (recommended) — `gh` for GitHub, `glab` for GitLab.
  Check that CLI is installed and authorized.
- **REST API** — direct call to platform API.
  Need access token.

### 3. What is the PR URL format in your system?

Examples:
- GitHub: `https://github.com/owner/repo/pull/123`
- GitLab: `https://gitlab.com/owner/repo/-/merge_requests/123`
- Bitbucket: `https://bitbucket.org/owner/repo/pull-requests/123`

## Setup Order

### Step 1: SKILL.md — section "Input Data"

Replace block `⚠️ CONFIGURE` with PR URL format of your system.

### Step 2: SKILL.md — section "Code Access"

Replace block `⚠️ CONFIGURE` with specific tools
and commands for your system. Specify:
- Which CLI or API to use
- What to do if CLI is unavailable

### Step 3: SKILL.md — section "Recommended Workflow"

Replace block `⚠️ CONFIGURE` and GitHub example commands
with real commands for your system.

### Step 4: SKILL.md — section "If CLI Unavailable"

Replace block `⚠️ CONFIGURE` with specific authorization
command for your CLI.

## Verification After Setup

- [ ] All `⚠️ CONFIGURE` blocks replaced
- [ ] Specific CLI commands or API requests specified
- [ ] Authorization command specified
- [ ] Described what to do if CLI is unavailable

## Skill Files

```
06-qa-code-review/
  SKILL.md                         — skill instruction
  references/
    output-template.md             — output file template
  setup-guide.md                   — this instruction
```
