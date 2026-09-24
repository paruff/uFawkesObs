"""Unit tests for the Claude Code guardrails in .claude/ (AI-Native SDLC).

- protect-tests.py (PreToolUse): blocks tool calls that delete test files or
  remove test functions -- AGENTS.md "never delete tests to make a build
  pass", enforced mechanically instead of by instruction only.
- verify-changed-files.sh (Stop): runs pre-commit on the session's changed
  files so the session checks its own work before a human sees it.
- .claude/skills resolves to .agents/skills, so Claude Code discovers the
  repo's skills (it does not read .agents/).
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS = REPO_ROOT / ".claude" / "hooks"
PROTECT_TESTS = HOOKS / "protect-tests.py"
VERIFY_CHANGED = HOOKS / "verify-changed-files.sh"
SETTINGS = REPO_ROOT / ".claude" / "settings.json"

TWO_TESTS = "def test_a():\n    assert 1\n\n\ndef test_b():\n    assert 2\n"
ONE_TEST = "def test_a():\n    assert 1\n"


def run_hook(hook: Path, payload: dict, cwd: Path = REPO_ROOT):
    # Hooks cd to $CLAUDE_PROJECT_DIR when set; drop it so a test run inside
    # a Claude Code session exercises `cwd`, not the real repo.
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
    return subprocess.run(
        [str(hook)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=cwd,
        env=env,
        timeout=120,
    )


def edit(file_path: str, old: str, new: str, replace_all: bool = False) -> dict:
    return {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": file_path,
            "old_string": old,
            "new_string": new,
            "replace_all": replace_all,
        },
    }


def bash(command: str) -> dict:
    return {"tool_name": "Bash", "tool_input": {"command": command}}


@pytest.fixture
def test_file(tmp_path: Path) -> Path:
    path = tmp_path / "tests" / "unit" / "test_example.py"
    path.parent.mkdir(parents=True)
    path.write_text(TWO_TESTS)
    return path


class TestProtectTestsHook:
    def test_hook_is_executable(self):
        assert PROTECT_TESTS.is_file()
        assert PROTECT_TESTS.stat().st_mode & 0o111

    def test_edit_removing_a_test_function_is_blocked(self, test_file):
        old = "\n\ndef test_b():\n    assert 2\n"
        result = run_hook(PROTECT_TESTS, edit(str(test_file), old, "\n"))
        assert result.returncode == 2
        assert "test_b" in result.stderr

    def test_edit_renaming_a_test_is_allowed(self, test_file):
        result = run_hook(
            PROTECT_TESTS, edit(str(test_file), "def test_b", "def test_b_renamed")
        )
        assert result.returncode == 0, result.stderr

    def test_edit_adding_a_test_is_allowed(self, test_file):
        new = "assert 2\n\n\ndef test_c():\n    assert 3\n"
        result = run_hook(PROTECT_TESTS, edit(str(test_file), "assert 2\n", new))
        assert result.returncode == 0, result.stderr

    def test_replace_all_removing_tests_is_blocked(self, test_file):
        result = run_hook(
            PROTECT_TESTS,
            edit(str(test_file), "def test_", "def helper_", replace_all=True),
        )
        assert result.returncode == 2

    def test_write_with_fewer_tests_is_blocked(self, test_file):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": str(test_file), "content": ONE_TEST},
        }
        assert run_hook(PROTECT_TESTS, payload).returncode == 2

    def test_multiedit_removing_a_test_is_blocked(self, test_file):
        payload = {
            "tool_name": "MultiEdit",
            "tool_input": {
                "file_path": str(test_file),
                "edits": [
                    {"old_string": "def test_b():\n    assert 2\n", "new_string": ""}
                ],
            },
        }
        assert run_hook(PROTECT_TESTS, payload).returncode == 2

    def test_edit_outside_tests_dir_is_allowed(self, tmp_path):
        path = tmp_path / "scripts" / "helper.py"
        path.parent.mkdir()
        path.write_text(TWO_TESTS)
        result = run_hook(PROTECT_TESTS, edit(str(path), TWO_TESTS, ""))
        assert result.returncode == 0, result.stderr

    @pytest.mark.parametrize(
        "command",
        [
            "rm tests/unit/test_compose_versions.py",
            "rm -rf tests/integration",
            "git rm tests/unit/test_check_env.py",
            "git mv tests/unit/test_check_env.py /tmp/x.py",
            "cd tests && rm unit/test_check_env.py",
            "find tests -name 'test_*.py' -delete",
        ],
    )
    def test_bash_deleting_tests_is_blocked(self, command):
        result = run_hook(PROTECT_TESTS, bash(command))
        assert result.returncode == 2, f"not blocked: {command}"

    @pytest.mark.parametrize(
        "command",
        [
            "pytest tests/unit -q",
            "ls tests/unit",
            "rm -rf tests/unit/__pycache__",
            "rm -f tests/unit/reports/junit.xml",
            "git diff tests/",
        ],
    )
    def test_bash_non_deleting_commands_are_allowed(self, command):
        result = run_hook(PROTECT_TESTS, bash(command))
        assert result.returncode == 0, f"wrongly blocked: {command}: {result.stderr}"

    def test_malformed_input_does_not_block(self):
        result = subprocess.run(
            [str(PROTECT_TESTS)], input="not json", capture_output=True, text=True
        )
        assert result.returncode == 0


class TestVerifyChangedFilesHook:
    def test_hook_is_executable(self):
        assert VERIFY_CHANGED.is_file()
        assert VERIFY_CHANGED.stat().st_mode & 0o111

    def test_second_stop_in_a_row_is_not_blocked(self):
        # stop_hook_active means Claude is already continuing because of this
        # hook -- blocking again would loop.
        result = run_hook(VERIFY_CHANGED, {"stop_hook_active": True})
        assert result.returncode == 0

    @pytest.fixture
    def git_repo(self, tmp_path: Path) -> Path:
        if not shutil.which("pre-commit"):
            pytest.skip("pre-commit not installed")

        def run(*args: str) -> None:
            subprocess.run(args, cwd=tmp_path, check=True, capture_output=True)

        run("git", "init", "-q")
        run("git", "config", "user.email", "t@example.com")
        run("git", "config", "user.name", "t")
        # `language: fail` needs no network, so this runs offline in CI.
        (tmp_path / ".pre-commit-config.yaml").write_text(
            "repos:\n- repo: local\n  hooks:\n  - id: no-bad\n    name: no-bad\n"
            "    language: fail\n    entry: bad file found\n    files: bad\\.txt$\n"
        )
        run("git", "add", ".")
        run("git", "commit", "-qm", "init")
        return tmp_path

    def test_clean_tree_is_not_blocked(self, git_repo):
        assert run_hook(VERIFY_CHANGED, {}, cwd=git_repo).returncode == 0

    def test_failing_changed_file_blocks_with_output(self, git_repo):
        (git_repo / "bad.txt").write_text("x\n")
        result = run_hook(VERIFY_CHANGED, {}, cwd=git_repo)
        assert result.returncode == 2
        assert "bad file found" in result.stderr

    def test_passing_changed_file_is_not_blocked(self, git_repo):
        (git_repo / "good.txt").write_text("x\n")
        assert run_hook(VERIFY_CHANGED, {}, cwd=git_repo).returncode == 0


class TestClaudeCodeWiring:
    def test_hooks_are_registered_in_settings(self):
        hooks = json.loads(SETTINGS.read_text())["hooks"]
        pre = [h["command"] for g in hooks["PreToolUse"] for h in g["hooks"]]
        stop = [h["command"] for g in hooks["Stop"] for h in g["hooks"]]
        assert any("protect-tests.py" in c for c in pre)
        assert any("verify-changed-files.sh" in c for c in stop)

    def test_protect_tests_matcher_covers_edit_write_and_bash(self):
        hooks = json.loads(SETTINGS.read_text())["hooks"]["PreToolUse"]
        matcher = next(
            g["matcher"]
            for g in hooks
            if any("protect-tests.py" in h["command"] for h in g["hooks"])
        )
        for tool in ("Edit", "Write", "MultiEdit", "Bash"):
            assert tool in matcher.split("|")

    def test_claude_skills_resolve_to_agents_skills(self):
        skills = REPO_ROOT / ".claude" / "skills"
        assert skills.is_symlink()
        assert skills.resolve() == (REPO_ROOT / ".agents" / "skills").resolve()
        assert (skills / "gitops-reconcile" / "SKILL.md").is_file()

    def test_review_md_points_at_review_contract(self):
        review = (REPO_ROOT / "REVIEW.md").read_text()
        assert ".agents/agents/review.md" in review
        assert "AI-Assisted Review Block" in review

    def test_settings_local_json_is_gitignored(self):
        result = subprocess.run(
            ["git", "check-ignore", "-q", ".claude/settings.local.json"],
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0
