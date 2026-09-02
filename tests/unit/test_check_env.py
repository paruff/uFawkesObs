"""Unit tests for scripts/check-env.sh — the Grafana credential guard.

This guard is the only thing standing between `make up` and a Grafana
instance published on 0.0.0.0:3000 with a password an attacker can guess,
so its rejection list is security-relevant logic and gets real coverage.

Regression under test: the guard rejected the sentinel
`REPLACE_ME_set_a_real_password_here`, but `.env.example` ships
`REPLACE_ME`. Following the guard's own remediation text
(`cp .env.example .env`) therefore passed the guard.
"""

import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_ENV = REPO_ROOT / "scripts" / "check-env.sh"
ENV_EXAMPLE = REPO_ROOT / ".env.example"


def run_guard(password: str, tmp_path: Path) -> subprocess.CompletedProcess:
    """Invoke check-env.sh against an isolated repo root with no .env file.

    The script derives ROOT_DIR from its own location and falls back to
    parsing ROOT_DIR/.env whenever the environment variable is empty, so
    running the checked-in copy would read the developer's real .env and
    make results machine-dependent. Copying it into tmp_path/scripts/
    gives every case the same known-empty starting state.
    """
    isolated_scripts = tmp_path / "scripts"
    isolated_scripts.mkdir(exist_ok=True)
    isolated_guard = isolated_scripts / "check-env.sh"
    isolated_guard.write_text(CHECK_ENV.read_text())

    return subprocess.run(
        ["bash", str(isolated_guard)],
        env={"PATH": "/usr/bin:/bin", "GRAFANA_ADMIN_PASSWORD": password},
        capture_output=True,
        text=True,
    )


@pytest.mark.unit
@pytest.mark.parametrize(
    "password",
    [
        "admin",
        "changeme",
        "REPLACE_ME",
        "REPLACE_ME_set_a_real_password_here",
    ],
)
def test_rejects_placeholder_and_default_passwords(
    password: str, tmp_path: Path
) -> None:
    result = run_guard(password, tmp_path)
    assert result.returncode != 0, (
        f"Guard accepted insecure password {password!r} — stdout: {result.stdout}"
    )
    assert "Refusing to start" in result.stdout


@pytest.mark.unit
def test_rejects_empty_password(tmp_path: Path) -> None:
    # An empty value makes the script fall through to .env parsing; with no
    # readable value anywhere it must still refuse rather than default.
    result = run_guard("", tmp_path)
    assert result.returncode != 0
    assert "Refusing to start" in result.stdout


@pytest.mark.unit
def test_accepts_a_real_password(tmp_path: Path) -> None:
    result = run_guard("s3cret-not-a-placeholder", tmp_path)
    assert result.returncode == 0, f"Guard rejected a valid password: {result.stdout}"
    assert "Environment check passed" in result.stdout


@pytest.mark.unit
def test_env_example_placeholder_is_rejected_by_the_guard(tmp_path: Path) -> None:
    """The documented onboarding path must not produce a working password.

    README and check-env.sh both tell the user to `cp .env.example .env`.
    Whatever placeholder that file ships must therefore be one the guard
    refuses — otherwise copying the file verbatim yields a live Grafana
    admin login with a password published in the repo.
    """
    placeholder = None
    for line in ENV_EXAMPLE.read_text().splitlines():
        line = line.strip()
        if line.startswith("GRAFANA_ADMIN_PASSWORD="):
            placeholder = line.split("=", 1)[1].strip().strip("\"'")
            break

    assert placeholder is not None, "GRAFANA_ADMIN_PASSWORD missing from .env.example"

    result = run_guard(placeholder, tmp_path)
    assert result.returncode != 0, (
        f".env.example ships GRAFANA_ADMIN_PASSWORD={placeholder!r}, which "
        f"check-env.sh accepts. Copying .env.example verbatim — the exact "
        f"step both README and the guard's own remediation text tell users "
        f"to take — produces a Grafana admin account with a password that is "
        f"public in this repository."
    )
