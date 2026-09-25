#!/usr/bin/env python3
"""PreToolUse hook (Edit|Write|MultiEdit|Bash): blocks deleting tests.

Enforces AGENTS.md / .claude/rules/tests.md "never delete failing tests to
make a build pass" mechanically rather than by instruction only:

- Edit / MultiEdit / Write to a .py file under a tests/ directory that
  leaves fewer `def test_*` functions than the file has now. Renames and
  additions are allowed -- only a net loss of test functions is blocked.
- Bash rm / unlink / git rm / mv / git mv / find -delete of test files or
  test directories. Build artifacts (__pycache__, .pytest_cache, reports/,
  *.pyc, *.xml) are still deletable.

Exit 2 blocks the tool call and shows stderr to Claude. Anything this hook
can't parse is allowed (exit 0) -- it guards one rule, it isn't a sandbox.
If a test genuinely must go, a human removes it.
"""

import json
import re
import shlex
import sys
from collections import Counter
from pathlib import PurePath

TEST_DEF = re.compile(r"^[ \t]*(?:async[ \t]+)?def[ \t]+(test\w*)[ \t]*\(", re.M)
TEST_FILE = re.compile(r"^(test_.*|.*_test|conftest)\.py$")
ARTIFACT_DIRS = {"__pycache__", ".pytest_cache", "reports", "htmlcov"}
ARTIFACT_SUFFIXES = {".pyc", ".xml", ".html", ".log"}
SEGMENT_SPLIT = re.compile(r"&&|\|\||[;|\n]")


def block(message: str) -> None:
    print(f"BLOCKED: {message}", file=sys.stderr)
    print(
        "\nAGENTS.md: never delete tests to make a build pass. If the test is "
        "wrong, fix it; if it truly must be removed, ask the human to do it.",
        file=sys.stderr,
    )
    sys.exit(2)


def in_tests_dir(path: str) -> bool:
    return "tests" in PurePath(path).parts


def is_protected_path(path: str) -> bool:
    p = PurePath(path)
    if TEST_FILE.match(p.name):
        return True
    if not in_tests_dir(path):
        return False
    if ARTIFACT_DIRS.intersection(p.parts) or p.suffix in ARTIFACT_SUFFIXES:
        return False
    return True


def test_names(source: str) -> Counter:
    return Counter(TEST_DEF.findall(source))


def check_file_edit(tool: str, tool_input: dict) -> None:
    path = tool_input.get("file_path", "")
    if not (path.endswith(".py") and in_tests_dir(path)):
        return
    try:
        with open(path, encoding="utf-8") as f:
            before = f.read()
    except OSError:
        return  # new file -- nothing to lose

    if tool == "Write":
        after = tool_input.get("content", "")
    else:
        edits = tool_input.get("edits") if tool == "MultiEdit" else [tool_input]
        after = before
        for e in edits or []:
            old, new = e.get("old_string", ""), e.get("new_string", "")
            if not old or old not in after:
                return  # the tool itself will reject this edit
            count = -1 if e.get("replace_all") else 1
            after = after.replace(old, new, count)

    lost = test_names(before) - test_names(after)
    if sum(test_names(after).values()) < sum(test_names(before).values()):
        names = ", ".join(sorted(lost)) or "test functions"
        block(f"this {tool} removes {names} from {path}.")


def check_bash(command: str) -> None:
    for segment in SEGMENT_SPLIT.split(command):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        if not tokens:
            continue
        if tokens[0] == "sudo":
            tokens = tokens[1:]
        if not tokens:
            continue

        cmd, args = tokens[0], tokens[1:]
        if cmd == "git" and args[:1] in (["rm"], ["mv"]):
            cmd, args = f"git {args[0]}", args[1:]

        paths = [a for a in args if not a.startswith("-")]
        if cmd in ("mv", "git mv"):
            paths = paths[:-1]  # sources only
        elif cmd == "find":
            if ("-delete" in args or "-exec" in args) and any(
                in_tests_dir(a) or a == "tests" for a in paths
            ):
                block(f"`{segment.strip()}` deletes files under tests/.")
            continue
        elif cmd not in ("rm", "unlink", "git rm"):
            continue

        for path in paths:
            if is_protected_path(path) or path.rstrip("/") == "tests":
                block(f"`{segment.strip()}` deletes or moves test code ({path}).")


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)
    tool = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    if tool in ("Edit", "Write", "MultiEdit"):
        check_file_edit(tool, tool_input)
    elif tool == "Bash":
        check_bash(tool_input.get("command", ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
