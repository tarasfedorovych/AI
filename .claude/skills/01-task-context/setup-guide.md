# Task Context Skill Setup Guide

This skill collects task data from tracker and forms
structured context file. Before using
need to configure for your tracker and project.

## What you need to know before setup

Find answers to these questions BEFORE asking
AI to configure the files:

### 1. What tracker do you have?

Jira Cloud, Jira Server, Linear, GitHub Issues,
Azure DevOps, YouTrack, Notion, ClickUp, or other.

### 2. How will AI access the tracker?

Options:
- **MCP Server** (recommended) — Atlassian MCP for Jira,
  Linear MCP for Linear, etc. Verify that MCP is connected
  and authenticated.
- **CLI** — for example `gh` for GitHub Issues.
  Verify that CLI is installed and authorized.
- **No integration** — you will copy the task description to the chat
  manually. Works with any tracker, but slower.

### 3. What task types are in your project?

Go to the tracker and see what types are used.
Typical examples:
- Jira: Story, Task, Bug, Epic, Sub-task
- Linear: Issue, Bug, Feature
- GitHub: Issue (one type, differentiated by labels)

### 4. What fields are in each task type?

This is the most important step. Open several real tasks
of each type and write down which fields are filled:

- Title (always present)
- Description (almost always present)
- Acceptance Criteria
- User Story
- Notes for QA / Notes for DEV
- Custom fields specific to your project
- Comments
- Attachments

**For Jira:** custom fields have technical keys
like `customfield_XXXXX`. To find the key:
1. Open the task in browser
2. Click `...` → Export XML
3. In XML find the needed field and its key

Or ask Jira admin to provide a list of custom fields.

### 5. Which field is mandatory?

Which field MUST be filled to have something to process?
Usually this is task description (description).
For bugs there may be a separate field (Bug Description,
Steps to Reproduce).

## Setup Order

When you have answers to the questions above — configure the files
in this order:

### Step 1: references/field-maps.md

This is first and most important. Fill the field map:
1. Create a section for each task type
2. For each type fill the table:
   - Value — human-readable field name
   - Field key — technical key in tracker
   - Mandatory — yes/no (minimum one "yes" per type)
3. Delete task types you don't use
4. Add types missing from the template

### Step 2: SKILL.md — section "Access to tracker"

Replace the `⚠️ CONFIGURE` block with specific instructions
for your tracker and access method. Specify:
- Which MCP tools or CLI commands to use
- How to parse task URL
- What to do if integration is unavailable
- Fallback scenario

### Step 3: SKILL.md — section "Task types and fields"

Replace the `⚠️ CONFIGURE` block with a list of your task types.

### Step 4: SKILL.md — section "Empty fields"

Replace the `⚠️ CONFIGURE` block with specific mandatory fields
for each task type from your field map.

### Step 5: SKILL.md — section "Attachments"

Replace the `⚠️ CONFIGURE` block with description of how your tracker/MCP
returns attachments. If unsure — leave as is,
default flow (ask user to upload) works with any tracker.

### Step 6: SKILL.md — section "Input Data"

Replace the `⚠️ CONFIGURE` block with format of task key
in your tracker.

## Verification After Setup

After setup check:
- [ ] All `⚠️ CONFIGURE` blocks in SKILL.md replaced
      with specific instructions
- [ ] field-maps.md contains real fields of your project
      with correct technical keys
- [ ] At least one mandatory field for each task type
- [ ] Access method specified (MCP, CLI,
      or manual copying)

## Test Run

After setup do a test run on one real task:
1. Give AI the key or URL of task
2. Check that all fields from the map are collected
3. Check that context file contains all information
   from ticket without loss
4. If something is missing — check the field map

## Skill Files

```
.claude/skills/01-task-context/
  SKILL.md                         — skill instruction
  references/
    field-maps.md                  — project field map
    output-template.md             — output file template
  setup-guide.md                   — this instruction
```
