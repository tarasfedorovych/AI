#!/usr/bin/env python3
"""PreToolUse guard for the 01-task-context skill.

Stage 1 is the only stage with tracker access, and every later stage reads what
it writes. A stage 1 run that starts without a working `jira` MCP server either
dies halfway or — worse — produces a plausible-looking empty context file. This
hook refuses the skill up front instead.

Two things are checked, and reported as the two distinct failures the skill
itself distinguishes:

  configured  — a `jira` server entry exists in .mcp.json or ~/.claude.json,
                its command is on PATH, and every ${VAR} in its env resolves.
  connected   — the server actually starts and answers an MCP initialize +
                tools/list handshake with the Jira tools the skill calls.

Reads the PreToolUse payload on stdin, writes a PreToolUse decision on stdout.
Silent (exit 0, no output) for every tool call that is not the stage 1 skill,
and for a passing check. An internal error asks rather than denies, so a bug
here never hard-blocks the pipeline.
"""

import hashlib
import json
import os
import queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

SKILL_NAME = "01-task-context"
SERVER_NAME = "jira"
REQUIRED_TOOLS = ("jira_get_issue",)
HANDSHAKE_TIMEOUT = 40.0
CACHE_TTL = 600.0
CACHE_FILE = Path(tempfile.gettempdir()) / "qa-pipeline-jira-mcp-check.json"

NO_WORKAROUND = (
    "Stop and tell the user; stage 1 has no fallback — do not use MCP_DOCKER, "
    "WebFetch, the browse URL or a browser as a substitute."
)


def decide(decision, reason):
    """Emit a PreToolUse decision and exit."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def deny(reason):
    decide("deny", reason)


def targets_stage_1(payload):
    if payload.get("tool_name") != "Skill":
        return False
    skill = (payload.get("tool_input") or {}).get("skill") or ""
    skill = skill.strip().lstrip("/")
    return skill == SKILL_NAME or skill.endswith(":" + SKILL_NAME)


def same_project(config_key, cwd):
    normalized = os.path.normcase(os.path.normpath(config_key.replace("/", os.sep)))
    return normalized == os.path.normcase(os.path.normpath(str(cwd)))


def find_server(cwd):
    """Locate the `jira` MCP entry the way Claude Code resolves it.

    Project .mcp.json first, then the project-scoped and global blocks of
    ~/.claude.json. Returns (entry, source label) or (None, None).
    """
    project_mcp = cwd / ".mcp.json"
    if project_mcp.is_file():
        servers = read_json(project_mcp).get("mcpServers") or {}
        if SERVER_NAME in servers:
            return servers[SERVER_NAME], str(project_mcp)

    user_config = Path.home() / ".claude.json"
    if user_config.is_file():
        data = read_json(user_config)
        for key, value in (data.get("projects") or {}).items():
            servers = (value or {}).get("mcpServers") or {}
            if SERVER_NAME in servers and same_project(key, cwd):
                return servers[SERVER_NAME], f"{user_config} (project {key})"
        servers = data.get("mcpServers") or {}
        if SERVER_NAME in servers:
            return servers[SERVER_NAME], str(user_config)

    return None, None


def read_json(path):
    # utf-8-sig: config files written by Windows editors carry a BOM.
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def resolve_env(entry):
    """Expand ${VAR} references in the server's env. Returns (env, unresolved)."""
    resolved = {}
    unresolved = []
    for key, raw in (entry.get("env") or {}).items():
        value = str(raw)

        def substitute(match):
            name = match.group(1) or match.group(2)
            replacement = os.environ.get(name, "")
            if not replacement:
                unresolved.append(name)
            return replacement

        expanded = PLACEHOLDER.sub(substitute, value)
        if not expanded.strip():
            unresolved.append(key)
        resolved[key] = expanded
    # Preserve order, drop repeats.
    return resolved, list(dict.fromkeys(unresolved))


def check_credentials(env):
    """mcp-atlassian only registers Jira tools when these are present."""
    missing = []
    if not env.get("JIRA_URL", "").strip():
        missing.append("JIRA_URL")
    basic = env.get("JIRA_USERNAME", "").strip() and env.get("JIRA_API_TOKEN", "").strip()
    personal = env.get("JIRA_PERSONAL_TOKEN", "").strip()
    if not basic and not personal:
        missing.append("JIRA_USERNAME + JIRA_API_TOKEN (or JIRA_PERSONAL_TOKEN)")
    return missing


def cache_key(executable, args, env):
    digest = hashlib.sha256()
    digest.update(json.dumps([executable, args], sort_keys=True).encode())
    for key in sorted(env):
        digest.update(key.encode())
        digest.update(hashlib.sha256(env[key].encode()).digest())
    return digest.hexdigest()


def cache_is_fresh(key):
    try:
        cached = read_json(CACHE_FILE)
    except (OSError, ValueError):
        return False
    return cached.get("key") == key and (time.time() - float(cached.get("ts", 0))) < CACHE_TTL


def cache_store(key):
    try:
        CACHE_FILE.write_text(json.dumps({"key": key, "ts": time.time()}), encoding="utf-8")
    except OSError:
        pass  # A cache miss next run is harmless; a crash here is not.


def pump(stream, sink):
    for line in stream:
        sink(line)
    try:
        stream.close()
    except OSError:
        pass


def handshake(executable, args, env, cwd):
    """Start the server and run initialize + tools/list. Returns (tools, error)."""
    popen_kwargs = {}
    if os.name == "nt":
        popen_kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        proc = subprocess.Popen(
            [executable] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=str(cwd),
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            **popen_kwargs,
        )
    except OSError as exc:
        return None, f"could not be started ({exc})"

    lines = queue.Queue()
    errors = []
    threading.Thread(target=pump, args=(proc.stdout, lines.put), daemon=True).start()
    threading.Thread(
        target=pump,
        args=(proc.stderr, lambda line: errors.append(line.rstrip()) if len(errors) < 40 else None),
        daemon=True,
    ).start()

    deadline = time.monotonic() + HANDSHAKE_TIMEOUT

    def send(message):
        proc.stdin.write(json.dumps(message) + "\n")
        proc.stdin.flush()

    def await_response(request_id):
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError
            if proc.poll() is not None and lines.empty():
                raise RuntimeError("exited")
            try:
                line = lines.get(timeout=min(remaining, 1.0))
            except queue.Empty:
                continue
            try:
                message = json.loads(line)
            except ValueError:
                continue  # Servers occasionally print banners on stdout.
            if isinstance(message, dict) and message.get("id") == request_id:
                return message

    try:
        send(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "qa-pipeline-stage1-hook", "version": "1.0"},
                },
            }
        )
        response = await_response(1)
        if "error" in response:
            return None, f"rejected the MCP handshake ({response['error']})"
        send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        response = await_response(2)
        if "error" in response:
            return None, f"refused tools/list ({response['error']})"
        tools = [tool.get("name", "") for tool in (response.get("result") or {}).get("tools", [])]
        return tools, None
    except TimeoutError:
        return None, f"did not answer within {HANDSHAKE_TIMEOUT:.0f}s"
    except (RuntimeError, BrokenPipeError, OSError):
        tail = " / ".join(line for line in errors[-3:] if line.strip())
        return None, f"exited during startup{': ' + tail if tail else ''}"
    finally:
        try:
            proc.stdin.close()
        except OSError:
            pass
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


def main():
    # PowerShell prepends a UTF-8 BOM when it pipes into a native command.
    raw = sys.stdin.read().lstrip("﻿").strip()
    try:
        payload = json.loads(raw or "{}")
    except ValueError:
        sys.exit(0)  # Not a payload we understand — stay out of the way.

    if not targets_stage_1(payload):
        sys.exit(0)

    cwd = Path(payload.get("cwd") or os.getcwd())

    entry, source = find_server(cwd)
    if entry is None:
        deny(
            f"Jira MCP is NOT CONFIGURED: no `{SERVER_NAME}` server in .mcp.json or "
            f"~/.claude.json. Stage 1 ({SKILL_NAME}) reads the ticket only through it. "
            f"{NO_WORKAROUND} Fix: add the server (see "
            ".claude/skills/01-task-context/setup-guide.md), then restart the session."
        )

    command = entry.get("command")
    if not command:
        deny(
            f"Jira MCP is MISCONFIGURED: the `{SERVER_NAME}` entry in {source} has no "
            f"`command`. {NO_WORKAROUND}"
        )

    env_overrides, unresolved = resolve_env(entry)
    if unresolved:
        deny(
            f"Jira MCP is MISCONFIGURED: the `{SERVER_NAME}` entry in {source} references "
            f"environment variables that are unset or empty in this session: "
            f"{', '.join(unresolved)}. The server would start unauthenticated and return "
            f"zero projects, which reads like an empty ticket. {NO_WORKAROUND} Fix: set "
            "them, then restart the session so Claude Code picks them up."
        )

    env = os.environ.copy()
    env.update(env_overrides)
    missing = check_credentials(env)
    if missing:
        deny(
            f"Jira MCP is MISCONFIGURED: the `{SERVER_NAME}` entry in {source} is missing "
            f"{', '.join(missing)}. mcp-atlassian registers no Jira tools without them. "
            f"{NO_WORKAROUND}"
        )

    executable = shutil.which(command)
    if executable is None:
        deny(
            f"Jira MCP is NOT CONNECTABLE: `{command}` (the launcher for the "
            f"`{SERVER_NAME}` server in {source}) is not on PATH. {NO_WORKAROUND}"
        )

    args = [str(arg) for arg in (entry.get("args") or [])]
    key = cache_key(executable, args, env_overrides)
    if cache_is_fresh(key):
        sys.exit(0)

    tools, error = handshake(executable, args, env, cwd)
    if error is not None:
        deny(
            f"Jira MCP is NOT CONNECTED: the `{SERVER_NAME}` server ({command} "
            f"{' '.join(args)}) {error}. This is an infrastructure failure, not a bad "
            f"issue key. {NO_WORKAROUND} Fix: restart or reconnect the server, then rerun "
            "stage 1."
        )

    absent = [tool for tool in REQUIRED_TOOLS if tool not in tools]
    if absent:
        deny(
            f"Jira MCP is CONNECTED BUT UNUSABLE: the `{SERVER_NAME}` server started and "
            f"exposed {len(tools)} tools, but not {', '.join(absent)}. mcp-atlassian drops "
            "its Jira tools when JIRA_URL or the credentials are wrong, so treat this as an "
            f"access/config problem rather than a wrong issue key. {NO_WORKAROUND}"
        )

    cache_store(key)
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — a broken guard must not block the pipeline
        decide(
            "ask",
            f"The Jira MCP pre-flight check for {SKILL_NAME} failed to run "
            f"({type(exc).__name__}: {exc}). It could not confirm the server is connected. "
            "Confirm only if you know the jira MCP is up.",
        )
