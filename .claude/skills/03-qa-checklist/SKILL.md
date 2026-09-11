---
name: 03-qa-checklist
description: Stage 3 of the QA pipeline. Takes the requirements file created by the 02-requirements-grooming skill, decomposes each requirement into atomic checks and creates a reference QA checklist — input for test cases and for manual testing. Use when the user says "build checklist", "make checklist", "checklist of checks", or after 02-requirements-grooming completes.
---

# QA Checklist

Decomposes numbered requirements into atomic checks
and creates a reference QA checklist — input for test cases
and for manual testing.

## Input Data

Input — file `<ISSUEKEY>-requirements.md` created by the
02-requirements-grooming skill, read from the story folder.

## Story Folder

All inputs and outputs live in the story folder built by
01-task-context:

```
stories/**/{ISSUEKEY}/
```

Locate it by globbing `stories/**/{ISSUEKEY}/` — one glob matches both
`stories/{EPIC-KEY}/{ISSUEKEY}/` and
`stories/{EPIC-KEY}/{FEATURE-KEY}/{ISSUEKEY}/`.

If the folder does not exist, or it holds no
`{ISSUEKEY}-requirements.md` — stop and tell the user which earlier
stage to run. Do not create the structure here, and do not fall back
to the working directory.

Data sources for this skill:
- requirements file — single source of truth for requirements.
- user responses to questions before checklist generation.

First, read the requirements file completely. If something
in the requirements is unclear or ambiguous for building
checks — ask the user before starting generation.
Do not start generation while there are unresolved questions.

Do not go to the tracker, do not use external tools,
do not search the internet, do not inspect code.

Requirements file — read-only.
Do not change, do not rewrite, do not clear its contents.

If the requirements file is missing, empty, or corrupted —
stop and inform the user that the 02-requirements-grooming
skill needs to be executed first.

## Rules

- All communication and all output file content — in English.
- Chat messages — brief.
- Checklist is built only from what is in the requirements file.
  Do not assume, do not supplement, do not interpret requirements yourself.
  Do not invent routes, selectors, roles, states, data, or expected
  behavior not in requirements.
- Do not change sense and wording of requirements. Skill decomposes
  requirements into checks, but does not rewrite or improve
  the requirements themselves.
- If requirement was left unchanged after grooming
  (user skipped question in skill 2) — build checklist
  on what exists. Do not skip such requirement or mark
  it as incomplete. Requirements file — final.
- Do not add general QA advice not tied
  to specific requirement of the task.
- After saving file — stop. Do not continue
  to code review, test cases, or planning.

## Numbering

Checklist items inherit requirement IDs from the requirements file.

Order of requirements in the checklist must match the order of requirements
in the requirements file. Do not change, do not rearrange,
do not group requirements differently than they go in the file.

One requirement may produce several checks. Each check
gets a sub-number with period: REQ-3.1, REQ-3.2, REQ-3.3.

Main number REQ-* does not change — it is the same
as in the requirements file and further in code review.

Sub-numbering is sequential, without gaps,
in order as checks appear in the checklist.

If requirement already has sub-items (REQ-5a, REQ-5b) —
each sub-item is numbered separately: REQ-5a.1, REQ-5a.2,
REQ-5b.1, REQ-5b.2.

## Checklist Building Method

Quality rules, decomposition, wording, check types,
filtering unnecessary, basic sets for typical elements,
and anti-patterns — in references/checklist-design-rules.md.

Read this file before starting checklist generation.

## Verification Before Saving

After checklist generation and before saving the file:

1. Pass the checklist through filtering of unnecessary checks.
2. Go through the checklist and verify:

- Each requirement from the requirements file has at least one
  check in the checklist. If a requirement has no checks —
  add one or explain why it is not possible.
- No checklist items without REQ-ID.
- Order of requirements in the checklist matches the order
  in the requirements file.
- No duplication: the same check does not appear twice.
- Similar items have the same basic set of checks.
- Each item is atomic: one check, one pass/fail.
- Each item is self-contained: understandable without opening
  the requirements file.
- No checks for behavior not in the requirements.

If a problem is found — fix it before saving.

## Output File

Create file `<ISSUEKEY>-checklist.md` in the story folder,
beside `<ISSUEKEY>-requirements.md`:

```
stories/**/{ISSUEKEY}/{ISSUEKEY}-checklist.md
```

The next skill reads it from the same folder.

If the file already exists — delete it completely and create a new one.
On output always one file with the result of the last run.
Do not merge with the previous version, do not append, do not save
data from the previous run.

Before finishing, verify:
- One top-level heading
- One coherent checklist without duplicate sections

File structure template — in references/output-template.md.
Example of detail level — in references/checklist-example.md.

## Final Response

After saving the file, inform:
- Path to the saved file
- Number of checklist items
