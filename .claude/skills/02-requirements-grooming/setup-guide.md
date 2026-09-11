# Requirements Grooming Skill Setup Guide

This skill analyzes requirements from the context file and creates
a numbered list of requirements for the next skills in the chain.
The grooming logic is universal — minimal setup is needed.

## What needs to be configured

### 1. Name of the context collection skill

This skill expects a context file from the previous skill
in the chain. By default it is called "01-task-context".

If the context collection skill in your chain has a different name —
replace "01-task-context" with the correct one in two places:
- `description` in frontmatter (line with "Takes context file
  created by 01-task-context skill")
- section "Input Data" in SKILL.md body

### 2. Communication language (optional)

By default the skill communicates in English.
If you need a different language — find the "Rules" section in SKILL.md
and replace the line:
```
- All communication and all output file content — in English.
```
with your language.

## What does NOT need to be configured

Grooming method (4 questions), REQ-N numbering rules,
chat output format, rules for what not to generate —
this is universal logic, do not touch.

## Setup Order

1. In `SKILL.md` frontmatter: replace "01-task-context" with the name of
   your context collection skill.
2. In `SKILL.md` "Input Data" section: replace "01-task-context"
   with the same name.
3. Optionally: replace communication language.

## Verification After Setup

- [ ] Context collection skill name is correct
      in both places
- [ ] `⚠️ CONFIGURE` blocks in SKILL.md are addressed

## Skill Files

```
02-requirements-grooming/
  SKILL.md                         — skill instruction
  references/
    output-template.md             — output file template
  setup-guide.md                   — this instruction
```
