# Setup Guide for QA Checklist Skill

This skill is almost completely universal — it works with any
tracker and product without changes. Checklist building method,
numbering rules, check types and anti-patterns are based
on ISTQB and do not depend on environment.

## What needs to be configured

### 1. Communication language (optional)

By default the skill communicates in Ukrainian.
If you need another language — in the "Rules" section of SKILL.md
replace the line:
```
- All communication and all output file content — in Ukrainian.
```
with your language.

### 2. Reference to previous skill (optional)

If in your chain the requirements grooming skill has a different
name than "02-requirements-grooming" — replace this reference
in SKILL.md "Input Data" section.

## What does NOT need to be configured

- `references/checklist-design-rules.md` — ISTQB rules,
  completely universal, do not touch
- `references/checklist-example.md` — decomposition example,
  do not touch
- `references/output-template.md` — file structure template,
  do not touch
- REQ-N.M numbering method, verification, filtering rules —
  do not touch

## Verification After Setup

- [ ] If language changed — check that it changed everywhere
- [ ] If previous skill name changed —
      check that it changed in "Input Data" section

## Skill Files

```
03-qa-checklist/
  SKILL.md                              — skill instruction
  references/
    checklist-design-rules.md          — building rules (ISTQB)
    checklist-example.md               — decomposition example
    output-template.md                 — output file template
  setup-guide.md                       — this instruction
```
