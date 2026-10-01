from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_telemetry_generator_has_matching_lock_file() -> None:
    lock_path = REPO_ROOT / "apps" / "telemetry-generator" / "requirements.lock"
    assert lock_path.is_file(), (
        "apps/telemetry-generator requires a matching requirements.lock"
    )
    content = lock_path.read_text(encoding="utf-8")
    assert "Flask==" in content
    assert "opentelemetry-sdk==" in content
    assert "# Generated lock file" in content


def test_telemetry_generator_dockerfile_uses_lock_file() -> None:
    dockerfile = (REPO_ROOT / "apps" / "telemetry-generator" / "Dockerfile").read_text(
        encoding="utf-8"
    )
    assert "COPY requirements.lock requirements.txt" in dockerfile
    assert "pip install --no-cache-dir -r requirements.txt" in dockerfile


def test_makefile_relock_covers_telemetry_generator() -> None:
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "apps/telemetry-generator/requirements.txt" in makefile


def test_dependabot_tracks_telemetry_generator_pip_updates() -> None:
    dependabot = (REPO_ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    assert 'directory: "/apps/telemetry-generator"' in dependabot
