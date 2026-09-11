# Setup Guide for Web Testing Skill

This skill executes QA and FAIL test cases in real browser.
Testing logic, classifications and navigation memory — universal.
Only need to configure login configuration.

## What you need to know before setup

### 1. Which browser tool are you using?

Skill is built for **Claude in Chrome extension**.
All tool names (`navigate`, `find`, `computer`, `form_input`
etc.) are names of tools of this extension.

If you use Playwright MCP or other tool —
you need to adapt all tool names in SKILL.md
and references/browser-rules.md to your system.

### 2. What does login look like in your product?

- URL of login page
- How to find email/username and password fields (label, placeholder)
- Text of submit button
- Which credentials to use and where to get them
- What appears after successful login

### 3. Do you need to register new users?

If test cases require creating new accounts —
prepare email template and default data for registration.

## Setup Order

### Step 1: references/login-config.md — login (MANDATORY)

This is the only file that needs configuration.
Replace all `<placeholders>` with real values:

- Login URL
- Descriptions of login form fields
- Credentials for each role
- Success indicator after login
- Actions after login (if any)

If registration is not needed — delete the Registration
and Default data sections.

### Step 2: navigation_paths.json — navigation memory

File is already present as empty structure `{"navigation_paths": {}}`.
Nothing needs to be changed — skill will fill it itself
during first run when it learns paths to pages.

### Step 3 (optional): SKILL.md — name of previous skill

If your chain of skills has different names than
`06-qa-code-review` and `04-qa-test-cases` — update the references
to these skills in the "Input Data" section of SKILL.md.

## Verification After Setup

- [ ] references/login-config.md does not contain `<placeholders>`
- [ ] Login URL is specified
- [ ] Credentials for all roles are specified
- [ ] Success indicator is specified
- [ ] Source of credentials is specified (hardcoded / .env / other)

## Skill Files

```
07-web-testing/
  SKILL.md                         — skill instruction
  navigation_paths.json            — memory of navigation paths
  references/
    login-config.md                — login configuration (configure!)
    browser-rules.md               — browser interaction rules
    output-template.md             — output file template
  setup-guide.md                   — this instruction
```
