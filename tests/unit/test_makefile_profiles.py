"""Regression test for #617: every compose service is in a profile, so
`docker compose down` / `logs` with no profile select zero services and
silently do nothing. The targets must opt into all profiles."""

import re
from pathlib import Path

MAKEFILE = (Path(__file__).resolve().parents[2] / "Makefile").read_text()


def _recipe(target: str) -> str:
    match = re.search(rf"^{target}:.*\n((?:\t.*\n)+)", MAKEFILE, re.MULTILINE)
    assert match, f"Makefile has no `{target}:` recipe"
    return match.group(1)


def test_down_selects_all_profiles():
    assert "--profile '*'" in _recipe("down"), (
        "`make down` must pass --profile '*' or it removes nothing (#617)"
    )


def test_logs_selects_all_profiles():
    assert "--profile '*'" in _recipe("logs"), (
        "`make logs` must pass --profile '*' or it prints nothing (#617)"
    )
