"""Free self-test of the guardrail eval harness (evals/run_guardrails.py).

Runs the runner + grader with scripted fake agents -- no model calls -- so a
broken grader can't silently turn the paid eval into a rubber stamp:

- noop (does nothing): every adversarial rule holds, no benign task is done.
- vandal (deletes tests/, runs remote compose up): every rule is violated.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "evals" / "run_guardrails.py"
CASES = yaml.safe_load((REPO_ROOT / "evals" / "guardrails" / "cases.yaml").read_text())


def run_fake(agent: str, out: Path):
    result = subprocess.run(
        [sys.executable, str(RUNNER), "--fake-agent", agent, "--out", str(out)],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=300,
    )
    rows = [
        json.loads(line)
        for line in (out / f"fake-{agent}" / "results.jsonl").read_text().splitlines()
    ]
    return result, {r["prompt_id"]: r["grade"]["pass"] for r in rows}


def ids(kind: str) -> set:
    return {c["id"] for c in CASES["cases"] if c["kind"] == kind}


def test_cases_cover_both_directions():
    assert len(ids("adversarial")) >= 5
    assert len(ids("benign")) >= 5


def test_noop_agent_holds_every_rule_and_completes_nothing(tmp_path):
    result, grades = run_fake("noop", tmp_path)
    assert result.returncode == 0, result.stderr
    assert all(grades[i] == 1 for i in ids("adversarial"))
    assert all(grades[i] == 0 for i in ids("benign"))


def test_vandal_agent_violates_every_rule_and_fails_the_run(tmp_path):
    result, grades = run_fake("vandal", tmp_path)
    assert result.returncode == 1, result.stdout
    assert all(grades[i] == 0 for i in ids("adversarial"))


def test_real_run_refuses_an_unapproved_harness(tmp_path, monkeypatch):
    state = REPO_ROOT / "evals" / "guardrails" / "_state.json"
    if not state.exists():
        pytest.skip("no approved harness yet")
    data = json.loads(state.read_text())
    tampered = tmp_path / "_state.json"
    tampered.write_text(json.dumps({**data, "harness_sha": "0" * 64}))
    # The gate compares against the committed _state.json; a mismatching sha
    # must stop a paid run before any model call.
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_guardrails", RUNNER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "STATE", tampered)
    monkeypatch.setattr(sys, "argv", ["run_guardrails.py", "--out", str(tmp_path)])
    assert mod.main() == 2
