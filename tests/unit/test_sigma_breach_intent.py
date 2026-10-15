"""Stage 6 σ-band breach -> intent issue wiring (#602)."""

import json
import pathlib
import subprocess

import yaml


def _run(project_root, tmp_path, series, *extra):
    f = tmp_path / "alerts.json"
    f.write_text(json.dumps({"status": "success", "data": {"result": series}}))
    return subprocess.run(
        [
            f"{project_root}/scripts/sigma-breach-intent.sh",
            "--alerts-file",
            str(f),
            "--dry-run",
            *extra,
        ],
        capture_output=True,
        text=True,
    )


def test_breach_maps_to_intent_title_in_affected_repo(project_root, tmp_path):
    r = _run(
        project_root,
        tmp_path,
        [{"metric": {"team_id": "paruff/uFawkesPipe", "metric": "dora_cfr_pct"}}],
    )
    assert r.returncode == 0
    repo, title = r.stdout.strip().split("\t")
    assert repo == "paruff/uFawkesPipe"
    assert title.startswith("intent: dora_cfr_pct breached")


def test_bare_team_id_gets_default_owner(project_root, tmp_path):
    r = _run(
        project_root,
        tmp_path,
        [{"metric": {"team_id": "demo", "metric": "dora_cfr_pct"}}],
        "--default-owner",
        "acme",
    )
    assert r.stdout.startswith("acme/demo\t")


def test_unsafe_team_id_is_skipped(project_root, tmp_path):
    r = _run(
        project_root,
        tmp_path,
        [{"metric": {"team_id": "x/y; rm -rf /", "metric": "dora_cfr_pct"}}],
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "no sigma-band breaches firing"
    assert "unsafe" in r.stderr


def test_unreachable_prometheus_fails(project_root):
    r = subprocess.run(
        [
            f"{project_root}/scripts/sigma-breach-intent.sh",
            "--prometheus-url",
            "http://127.0.0.1:1",
        ],
        capture_output=True,
        text=True,
    )
    assert r.returncode != 0


def test_rule_and_workflow_are_wired(project_root):
    root = pathlib.Path(project_root)
    rules = yaml.safe_load(
        (root / "config/prometheus/rules/ufawkesobs-sigma-band.yml").read_text()
    )
    names = [r.get("alert") or r.get("record") for r in rules["groups"][0]["rules"]]
    assert names == ["dora:badness_zscore_30d", "DORASigmaBandBreach"]
    assert (
        "ufawkesobs-sigma-band.yml"
        in (root / "config/prometheus/prometheus.yaml").read_text()
    )
    wf = yaml.safe_load(
        (root / ".github/workflows/sigma-breach-intent.yml").read_text()
    )
    job = wf["jobs"]["open-intents"]
    assert "SIGMA_INTENT_ENABLED" in job["if"]
    assert "sigma-breach-intent.sh" in json.dumps(job["steps"])
    assert (
        "DORASigmaBandBreach" in (root / "scripts/sigma-breach-intent.sh").read_text()
    )


def test_live_path_creates_issue_once_per_breach(project_root, tmp_path):
    # Stub gh: "issue list" reports nothing open; "issue create" is recorded.
    log = tmp_path / "gh.log"
    gh = tmp_path / "gh"
    gh.write_text(f'#!/bin/sh\necho "$@" >> {log}\n')
    gh.chmod(0o755)
    f = tmp_path / "alerts.json"
    f.write_text(
        json.dumps(
            {
                "status": "success",
                "data": {
                    "result": [
                        {"metric": {"team_id": "paruff/demo", "metric": "dora_cfr_pct"}}
                    ]
                },
            }
        )
    )
    r = subprocess.run(
        [f"{project_root}/scripts/sigma-breach-intent.sh", "--alerts-file", str(f)],
        capture_output=True,
        text=True,
        env={"PATH": f"{tmp_path}:/usr/bin:/bin"},
    )
    assert r.returncode == 0, r.stderr
    out = log.read_text()
    assert out.count("issue create") == 1
    assert "--repo paruff/demo" in out and "--label intent" in out
    assert "sigma-breach: paruff/demo dora_cfr_pct" in out
