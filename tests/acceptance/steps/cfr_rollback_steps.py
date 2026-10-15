"""Step definitions for the CFR-triggered rollback feature (#502).

Runs the real scripts: cfr-alert-firing.sh against a stub Prometheus, then
rollback-latest-good.sh against a throwaway git repo with docker stubbed.
"""

from __future__ import annotations

import http.server
import json
import os
import subprocess
import threading
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, then, when

ROOT = Path(__file__).resolve().parents[3]


class _Host:
    def __init__(self, tmp: Path) -> None:
        self.repo = tmp / "repo"
        self.bin = tmp / "bin"
        self.firing = False
        self.server: http.server.HTTPServer | None = None
        self.good = self.candidate = ""

    def git(self, *args: str) -> str:
        return subprocess.run(
            [
                "git",
                "-C",
                str(self.repo),
                "-c",
                "user.email=t@t",
                "-c",
                "user.name=t",
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()


@pytest.fixture
def cfr_host(tmp_path: Path):
    host = _Host(tmp_path)
    yield host
    if host.server:
        host.server.shutdown()


@given("a deploy host running a candidate ahead of deploy-latest-good")
def deploy_host(cfr_host: _Host) -> None:
    (cfr_host.repo / "scripts").mkdir(parents=True)
    cfr_host.bin.mkdir()
    cfr_host.git("init", "-q")
    cfr_host.git("remote", "add", "origin", str(cfr_host.repo))
    for name in ("check-env.sh", "wait-healthy.sh", "send-dora-deployment-event.sh"):
        stub = cfr_host.repo / "scripts" / name
        stub.write_text('#!/usr/bin/env bash\necho ran >> ".calls-$(basename "$0")"\n')
        stub.chmod(0o755)
    docker = cfr_host.bin / "docker"
    docker.write_text('#!/usr/bin/env bash\necho "$@" >> .calls-docker\n')
    docker.chmod(0o755)
    (cfr_host.repo / "f").write_text("good")
    cfr_host.git("add", "-A")
    cfr_host.git("commit", "-qm", "good")
    cfr_host.git("tag", "deploy-latest-good")
    cfr_host.good = cfr_host.git("rev-parse", "HEAD")
    (cfr_host.repo / "f").write_text("bad")
    cfr_host.git("commit", "-qam", "candidate")
    cfr_host.candidate = cfr_host.git("rev-parse", "HEAD")


def _serve(host: _Host, firing: bool) -> None:
    result = [{"metric": {"alertname": "DORACFRRegressionRollback"}}] if firing else []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "success", "data": {"result": result}}).encode()
            )

        def log_message(self, *args: object) -> None:
            pass

    host.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=host.server.serve_forever, daemon=True).start()


@given("Prometheus reports DORACFRRegressionRollback as firing")
def prom_firing(cfr_host: _Host) -> None:
    _serve(cfr_host, True)


@given("Prometheus reports DORACFRRegressionRollback as not firing")
def prom_not_firing(cfr_host: _Host) -> None:
    _serve(cfr_host, False)


@when("the CFR rollback check runs")
def run_check(cfr_host: _Host) -> None:
    assert cfr_host.server is not None
    url = f"http://127.0.0.1:{cfr_host.server.server_port}"
    out = subprocess.run(
        [str(ROOT / "scripts/cfr-alert-firing.sh"), url],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    # Clear call markers so each run's redeploy is observable on its own.
    (cfr_host.repo / ".calls-docker").unlink(missing_ok=True)
    if out != "0":
        env = {
            **os.environ,
            "PATH": f"{cfr_host.bin}:{os.environ['PATH']}",
            "REPO_DIR": str(cfr_host.repo),
        }
        subprocess.run(
            ["bash", str(ROOT / "scripts/rollback-latest-good.sh")],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )


@then("the host should be on deploy-latest-good")
def on_good(cfr_host: _Host) -> None:
    assert cfr_host.git("rev-parse", "HEAD") == cfr_host.good


@then("the host should still be on the candidate")
def on_candidate(cfr_host: _Host) -> None:
    assert cfr_host.git("rev-parse", "HEAD") == cfr_host.candidate


@then("the host should have been redeployed and a recovery event sent")
def redeployed(cfr_host: _Host) -> None:
    assert (cfr_host.repo / ".calls-docker").exists()
    assert (cfr_host.repo / ".calls-send-dora-deployment-event.sh").exists()


@then(parsers.parse("the host should not be redeployed a second time"))
def not_redeployed(cfr_host: _Host) -> None:
    assert not (cfr_host.repo / ".calls-docker").exists()
