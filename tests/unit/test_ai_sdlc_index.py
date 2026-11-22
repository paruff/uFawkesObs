"""docs/ai-sdlc/README.md lists every feature folder and every link resolves."""

import re
from pathlib import Path

SDLC = Path(__file__).resolve().parents[2] / "docs" / "ai-sdlc"
README = (SDLC / "README.md").read_text()


def test_every_feature_folder_has_a_row():
    for folder in sorted(p.name for p in SDLC.iterdir() if p.is_dir()):
        assert f"| `{folder}` |" in README, f"docs/ai-sdlc/README.md lacks {folder}"


def test_row_links_resolve():
    for target in re.findall(r"\]\(([a-z0-9._-]+/[a-z]+\.md)[^)]*\)", README):
        assert (SDLC / target).is_file(), f"broken link: {target}"


def test_each_row_links_every_file_the_folder_has():
    for folder in (p for p in SDLC.iterdir() if p.is_dir()):
        for f in folder.glob("*.md"):
            assert f"]({folder.name}/{f.name})" in README, (
                f"{folder.name}/{f.name} not linked"
            )
