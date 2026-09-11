#!/usr/bin/env python3
"""Convert QA-pipeline test cases into BrowserStack createTestCase payloads.

Reads a story's `test-cases/` folder as produced by the 04-qa-test-cases
skill and emits a JSON array. Each element maps 1:1 onto the arguments of
the BrowserStack MCP `createTestCase` tool.

The conversion is deterministic — no model tokens are spent on parsing,
HTML wrapping, ordering or tag generation.

Usage
-----
    python tc_to_browserstack.py <test-cases-dir> --project PR-3 \
        --folder 51009925 --pretty --out payload.json

    # dry run, warnings only
    python tc_to_browserstack.py <test-cases-dir> --project PR-3 --validate-only

Source format expected per file (04-qa-test-cases output)
---------------------------------------------------------
    # TC-REQ-6.1: <scenario name>

    Requirement: REQ-6 — <requirement text>
    Applied technique: EP, Use Case

    **Precondition:** <prose, may contain fenced code blocks>

    | # | Step | Test Data | Expected Result |
    |---|------|-----------|------------------|
    | 1 | <action> | <data or —> | <result> |

    **Postcondition:** <optional>
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# Patterns
# --------------------------------------------------------------------------

H1_RE = re.compile(r"^#\s+(?P<tc_id>TC-[A-Za-z0-9.\-]+)\s*:\s*(?P<name>.+?)\s*$")
REQUIREMENT_RE = re.compile(
    r"^Requirement:\s*(?P<req_id>REQ-[A-Za-z0-9.]+)\s*(?:—|-|–)\s*(?P<req_text>.+?)\s*$"
)
TECHNIQUE_RE = re.compile(r"^Applied technique:\s*(?P<techniques>.+?)\s*$")
PRECONDITION_RE = re.compile(r"^\*\*Precondition:\*\*\s*(?P<rest>.*)$")
POSTCONDITION_RE = re.compile(r"^\*\*Postcondition:\*\*\s*(?P<rest>.*)$")
TABLE_HEADER_RE = re.compile(r"^\|\s*#\s*\|")
TABLE_SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
FENCE_RE = re.compile(r"^(?P<ticks>`{3,})")
INDEX_LINK_RE = re.compile(r"\[(?P<tc_id>TC-[A-Za-z0-9.\-]+)\]\((?P<file>[^)]+)\)")

# Cells holding no data in the pipeline's own output.
EMPTY_CELLS = {"", "—", "-", "–", "n/a", "N/A", "none"}

# Guards against splitting a precondition mid-abbreviation.
ABBREVIATIONS = {
    "e.g", "i.e", "etc", "vs", "cf", "approx", "no", "mr", "mrs",
    "ms", "dr", "prof", "fig", "sec", "min", "max",
}

PRIORITY_DISPLAY = {
    "critical": "Critical",
    "high": "High",
    "medium": "Medium",
    "low": "Low",
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def read_text(path: Path) -> str:
    """Read UTF-8, tolerating the BOM that Windows editors prepend.

    Without this a leading \\ufeff breaks the `^#` heading match and the
    file looks like it has no title at all.
    """
    return path.read_text(encoding="utf-8-sig")


def natural_key(text: str):
    """Sort key that orders TC-REQ-2.1 before TC-REQ-10.1 and keeps 7a < 7b."""
    parts = re.split(r"(\d+)", text)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def strip_fences(lines: list[str]) -> tuple[list[str], list[str]]:
    """Pull fenced code blocks out of a block of lines.

    Returns (lines_with_placeholders, fence_bodies). A placeholder line
    reads ``\x00FENCE:<n>\x00`` so prose handling never sees code.
    Handles nested fences (a 4-backtick block wrapping a 3-backtick one).
    """
    out: list[str] = []
    fences: list[str] = []
    fence_ticks: str | None = None
    buffer: list[str] = []

    for line in lines:
        stripped = line.strip()
        match = FENCE_RE.match(stripped)

        if fence_ticks is None:
            if match and set(stripped) == {"`"}:
                fence_ticks = match.group("ticks")
                buffer = []
                continue
            out.append(line)
        else:
            # Closing fence must be backticks only, at least as long as opener.
            if match and set(stripped) == {"`"} and len(match.group("ticks")) >= len(fence_ticks):
                fences.append("\n".join(buffer))
                out.append(f"\x00FENCE:{len(fences) - 1}\x00")
                fence_ticks = None
                continue
            buffer.append(line)

    if fence_ticks is not None:  # unterminated fence — keep what we have
        fences.append("\n".join(buffer))
        out.append(f"\x00FENCE:{len(fences) - 1}\x00")

    return out, fences


def split_sentences(text: str) -> list[str]:
    """Split prose into sentences without breaking abbreviations.

    Wording is preserved verbatim; only the split points are inferred.
    """
    pieces: list[str] = []
    current = ""
    tokens = re.split(r"(?<=\.)\s+", text)
    for token in tokens:
        candidate = f"{current} {token}".strip() if current else token
        last_word = re.split(r"[\s(]", candidate.rstrip("."))[-1].lower().rstrip(".")
        ends_sentence = candidate.endswith(".") and last_word not in ABBREVIATIONS
        # A following token starting lowercase means we split too early.
        if ends_sentence:
            pieces.append(candidate)
            current = ""
        else:
            current = candidate
    if current:
        pieces.append(current)
    return [p for p in (piece.strip() for piece in pieces) if p]


def html_list(items: list[str], ordered: bool = True) -> str:
    tag = "ol" if ordered else "ul"
    body = "\n".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f"<{tag}>\n{body}\n</{tag}>"


def html_fence(code: str) -> str:
    return f"<pre><code>{html.escape(code)}</code></pre>"


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------


@dataclass
class Step:
    index: str
    action: str
    test_data: str
    expected: str


@dataclass
class TestCase:
    path: Path
    tc_id: str = ""
    name: str = ""
    req_id: str = ""
    req_text: str = ""
    techniques: str = ""
    precondition_lines: list[str] = field(default_factory=list)
    postcondition_lines: list[str] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_case_file(path: Path) -> TestCase:
    case = TestCase(path=path)
    lines = read_text(path).splitlines()

    section: str | None = None
    in_table = False

    for line in lines:
        stripped = line.strip()

        if not case.tc_id:
            m = H1_RE.match(stripped)
            if m:
                case.tc_id = m.group("tc_id")
                case.name = m.group("name")
                continue

        m = REQUIREMENT_RE.match(stripped)
        if m and not case.req_id:
            case.req_id = m.group("req_id")
            case.req_text = m.group("req_text")
            section = None
            continue

        m = TECHNIQUE_RE.match(stripped)
        if m and not case.techniques:
            case.techniques = m.group("techniques")
            section = None
            continue

        m = PRECONDITION_RE.match(stripped)
        if m:
            section = "precondition"
            in_table = False
            if m.group("rest"):
                case.precondition_lines.append(m.group("rest"))
            continue

        m = POSTCONDITION_RE.match(stripped)
        if m:
            section = "postcondition"
            in_table = False
            if m.group("rest"):
                case.postcondition_lines.append(m.group("rest"))
            continue

        if TABLE_HEADER_RE.match(stripped):
            section = None
            in_table = True
            continue

        if in_table:
            if TABLE_SEPARATOR_RE.match(stripped):
                continue
            if stripped.startswith("|"):
                cells = [c.strip() for c in stripped.strip("|").split("|")]
                if len(cells) == 4:
                    case.steps.append(Step(*cells))
                elif len(cells) == 3:  # tolerate a table without a Test Data column
                    case.steps.append(Step(cells[0], cells[1], "—", cells[2]))
                else:
                    case.warnings.append(
                        f"skipped table row with {len(cells)} columns: {stripped[:60]}"
                    )
                continue
            if stripped:
                in_table = False

        if section == "precondition":
            case.precondition_lines.append(line)
        elif section == "postcondition":
            case.postcondition_lines.append(line)

    if not case.tc_id:
        case.warnings.append("no `# TC-...: name` heading found")
    if not case.name:
        case.warnings.append("no scenario name in heading")
    if not case.req_id:
        case.warnings.append("no `Requirement: REQ-N — ...` line found")
    if not case.steps:
        case.warnings.append("no step rows parsed — createTestCase requires at least one")
    for step in case.steps:
        if step.expected.strip() in EMPTY_CELLS:
            case.warnings.append(f"step {step.index} has no expected result")

    return case


# --------------------------------------------------------------------------
# Story context
# --------------------------------------------------------------------------


@dataclass
class StoryContext:
    story_key: str = ""
    story_title: str = ""
    epic_key: str = ""
    epic_title: str = ""
    jira_host: str = ""


def _h1_title(path: Path) -> str:
    if not path.is_file():
        return ""
    for line in read_text(path).splitlines():
        if line.startswith("# "):
            text = line[2:].strip()
            # "AISD-5 — Practice Page" -> "Practice Page"
            return re.sub(r"^[A-Z]+-\d+\s*(?:—|-|–)\s*", "", text).strip()
    return ""


def _jira_host(paths: list[Path]) -> str:
    for path in paths:
        if not path.is_file():
            continue
        m = re.search(r"https?://([^/\s)]+)/browse/", read_text(path))
        if m:
            return f"https://{m.group(1)}"
    return ""


def resolve_context(test_cases_dir: Path) -> StoryContext:
    """Derive keys and titles from the `stories/{EPIC}/{STORY}/test-cases` path."""
    story_dir = test_cases_dir.parent
    epic_dir = story_dir.parent

    ctx = StoryContext()
    ctx.story_key = story_dir.name
    ctx.story_title = _h1_title(story_dir / "story.md")

    if re.fullmatch(r"[A-Z]+-\d+", epic_dir.name):
        ctx.epic_key = epic_dir.name
        ctx.epic_title = _h1_title(epic_dir / "epic.md")

    ctx.jira_host = _jira_host(
        [story_dir / "story.md", epic_dir / "epic.md", story_dir / f"{ctx.story_key}-context.md"]
    )
    return ctx


def index_order(test_cases_dir: Path) -> list[str]:
    """Test case ids in the order `index.md` lists them (checklist order)."""
    index = test_cases_dir / "index.md"
    if not index.is_file():
        return []
    seen: list[str] = []
    for m in INDEX_LINK_RE.finditer(read_text(index)):
        tc_id = m.group("tc_id")
        if tc_id not in seen:
            seen.append(tc_id)
    return seen


# --------------------------------------------------------------------------
# Payload building
# --------------------------------------------------------------------------


def build_preconditions(case: TestCase, test_data_mode: str) -> str:
    blocks: list[str] = []

    pre_lines, fences = strip_fences(case.precondition_lines)
    prose = " ".join(line.strip() for line in pre_lines if line.strip())
    placeholders = re.findall(r"\x00FENCE:(\d+)\x00", prose)
    prose = re.sub(r"\s*\x00FENCE:\d+\x00\s*", " ", prose).strip()

    if prose:
        blocks.append(html_list(split_sentences(prose)))
    for idx in placeholders:
        blocks.append(html_fence(fences[int(idx)]))

    if test_data_mode in ("preconditions", "both"):
        data_items = [
            f"Step {s.index}: {s.test_data}"
            for s in case.steps
            if s.test_data.strip() not in EMPTY_CELLS
        ]
        if data_items:
            blocks.append("<p><strong>Test Data:</strong></p>")
            blocks.append(html_list(data_items, ordered=False))

    post_lines, post_fences = strip_fences(case.postcondition_lines)
    post = " ".join(line.strip() for line in post_lines if line.strip())
    post = re.sub(r"\s*\x00FENCE:\d+\x00\s*", " ", post).strip()
    if post:
        blocks.append("<p><strong>Postconditions:</strong></p>")
        blocks.append(html_list(split_sentences(post)))

    return "\n".join(blocks)


def build_steps(case: TestCase, test_data_mode: str) -> list[dict]:
    steps = []
    for step in case.steps:
        action = step.action
        has_data = step.test_data.strip() not in EMPTY_CELLS
        if has_data and test_data_mode in ("step", "both"):
            action = f"{action} (Test data: {step.test_data})"
        steps.append({"step": action, "result": step.expected})
    return steps


def build_payload(
    case: TestCase,
    ctx: StoryContext,
    project: str,
    folder: str | None,
    priority: str,
    case_type: str,
    automation_status: str,
    owner: str | None,
    test_data_mode: str,
    link_issues: bool,
) -> dict:
    description_parts = []
    if case.req_id:
        description_parts.append(f"{case.req_id}: {case.req_text}")
    if case.techniques:
        description_parts.append(f"Technique: {case.techniques}")
    description_parts.append(f"Source: {case.tc_id} ({case.path.name})")

    priority_display = PRIORITY_DISPLAY.get(priority.lower(), priority)

    tags = [f"priority:{priority_display.lower()}"]
    if ctx.epic_key:
        tags.append(f"epic:{ctx.epic_key}")
    if ctx.story_key:
        tags.append(f"story:{ctx.story_key}")
    if case.req_id:
        tags.append(f"req:{case.req_id}")
    if case.tc_id:
        tags.append(f"tc:{case.tc_id}")
    tags.append("MCP Generated")

    payload: dict = {
        "project_identifier": project,
        "name": case.name,
        "description": " | ".join(description_parts),
        "priority": priority_display,
        "case_type": case_type,
        "template": "test_case_steps",
        "automation_status": automation_status,
        "preconditions": build_preconditions(case, test_data_mode),
        "test_case_steps": build_steps(case, test_data_mode),
        "tags": tags,
    }

    if folder:
        payload["folder_id"] = str(folder)
    if owner:
        payload["owner"] = owner

    if link_issues:
        issues = [k for k in (ctx.story_key, ctx.epic_key) if k]
        if issues:
            payload["issues"] = issues
            if ctx.jira_host:
                payload["issue_tracker"] = {"name": "jira", "host": ctx.jira_host}

    return payload


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert QA-pipeline test cases to BrowserStack createTestCase payloads."
    )
    parser.add_argument("test_cases_dir", help="Path to a story's test-cases/ folder")
    parser.add_argument("--project", required=True, help="BrowserStack project identifier (PR-N)")
    parser.add_argument("--folder", help="Target folder id; omit to fill in later")
    parser.add_argument("--priority", default="Medium", help="Priority for all cases (default: Medium)")
    parser.add_argument("--case-type", default="Functional", help="case_type (default: Functional)")
    parser.add_argument("--automation-status", default="not_automated")
    parser.add_argument("--owner", help="Owner email")
    parser.add_argument(
        "--test-data",
        choices=("step", "preconditions", "both"),
        default="step",
        help="Where the Test Data column goes (default: step)",
    )
    parser.add_argument(
        "--no-issues", action="store_true", help="Do not link Jira story/epic keys"
    )
    parser.add_argument("--only", nargs="*", help="Publish only these TC ids")
    parser.add_argument("--out", help="Write JSON here instead of stdout")
    parser.add_argument("--pretty", action="store_true", help="Indent the JSON")
    parser.add_argument(
        "--validate-only", action="store_true", help="Report warnings, emit no payload"
    )
    args = parser.parse_args()

    tc_dir = Path(args.test_cases_dir)
    if not tc_dir.is_dir():
        print(f"error: not a directory: {tc_dir}", file=sys.stderr)
        return 2

    files = [p for p in tc_dir.glob("TC-*.md") if p.is_file()]
    if not files:
        print(f"error: no TC-*.md files in {tc_dir}", file=sys.stderr)
        return 2

    cases = [parse_case_file(p) for p in files]

    # Order by index.md, then by natural id order for anything it misses.
    order = index_order(tc_dir)
    rank = {tc_id: i for i, tc_id in enumerate(order)}
    cases.sort(key=lambda c: (rank.get(c.tc_id, len(rank)), natural_key(c.tc_id or c.path.name)))

    listed = set(order)
    found = {c.tc_id for c in cases}
    for missing in sorted(listed - found, key=natural_key):
        print(f"warning: index.md lists {missing} but no file was found", file=sys.stderr)
    for extra in sorted(found - listed, key=natural_key):
        if order:
            print(f"warning: {extra} is not listed in index.md", file=sys.stderr)

    if args.only:
        wanted = set(args.only)
        cases = [c for c in cases if c.tc_id in wanted]
        if not cases:
            print(f"error: --only matched nothing: {sorted(wanted)}", file=sys.stderr)
            return 2

    ctx = resolve_context(tc_dir)

    warn_count = 0
    for case in cases:
        for warning in case.warnings:
            print(f"warning: {case.path.name}: {warning}", file=sys.stderr)
            warn_count += 1

    print(
        f"parsed {len(cases)} case(s) from {tc_dir} "
        f"[story={ctx.story_key or '?'} epic={ctx.epic_key or '-'} warnings={warn_count}]",
        file=sys.stderr,
    )

    if args.validate_only:
        return 1 if warn_count else 0

    payloads = [
        build_payload(
            case,
            ctx,
            project=args.project,
            folder=args.folder,
            priority=args.priority,
            case_type=args.case_type,
            automation_status=args.automation_status,
            owner=args.owner,
            test_data_mode=args.test_data,
            link_issues=not args.no_issues,
        )
        for case in cases
    ]

    text = json.dumps(payloads, indent=2 if args.pretty else None, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {len(payloads)} payload(s) to {args.out}", file=sys.stderr)
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())
