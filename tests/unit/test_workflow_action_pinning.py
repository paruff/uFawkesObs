"""Unit tests asserting third-party GitHub Actions are pinned to commit SHAs.

A tag is a mutable pointer: whoever owns the action can move it to arbitrary
code, which then runs inside this repo's workflows with whatever permissions
and secrets that job holds. That is not hypothetical here --
`webfactory/ssh-agent` receives the production DEPLOY_KEY private key at four
points in deploy.yml.

GitHub's own hardening guidance is to pin third-party actions to a full commit
SHA. This test enforces that so the pinning cannot silently regress the next
time an action is added or bumped.
"""

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# Owners exempt from the SHA-pin requirement, each for a stated reason.
#   actions/*  - published by GitHub itself, the same trust boundary that
#                already runs the workflow; pinning them adds churn without
#                moving the trust boundary.
#   paruff/*   - this repo's own org; the reusable workflows are maintained
#                alongside it and move under the same review process.
EXEMPT_OWNERS = frozenset({"actions", "paruff"})

SHA_RE = re.compile(r"^[0-9a-f]{40}$")


# `uses:` can appear on a step (steps[].uses) or on a job (jobs.<id>.uses for
# a reusable workflow), so collect them by walking the parsed YAML rather than
# assuming one shape.
def collect_uses(node) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uses" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(collect_uses(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(collect_uses(item))
    return found


def workflow_files() -> list[Path]:
    return sorted(list(WORKFLOW_DIR.glob("*.yml")) + list(WORKFLOW_DIR.glob("*.yaml")))


@pytest.mark.unit
def test_workflow_directory_is_not_empty() -> None:
    # Guards against the walk silently finding nothing and every assertion
    # below passing vacuously.
    assert workflow_files(), f"No workflow files found under {WORKFLOW_DIR}"


@pytest.mark.unit
@pytest.mark.parametrize("workflow", workflow_files(), ids=lambda p: p.name)
def test_third_party_actions_are_sha_pinned(workflow: Path) -> None:
    parsed = yaml.safe_load(workflow.read_text())
    unpinned: list[str] = []

    for uses in collect_uses(parsed):
        if uses.startswith("./"):
            continue  # local workflow in this repo, not a third-party fetch
        if "@" not in uses:
            unpinned.append(f"{uses} (no ref at all)")
            continue

        target, ref = uses.rsplit("@", 1)
        owner = target.split("/", 1)[0]
        if owner in EXEMPT_OWNERS:
            continue
        if not SHA_RE.match(ref):
            unpinned.append(f"{uses} (ref {ref!r} is a mutable tag or branch)")

    assert not unpinned, (
        f"{workflow.name} references third-party actions that are not pinned to "
        f"a commit SHA:\n  " + "\n  ".join(unpinned) + "\n\n"
        "A tag can be repointed by its owner at any time, and these run with "
        "this repo's permissions and secrets. Resolve the tag to its commit "
        "SHA and keep the tag in a trailing comment, e.g.\n"
        "  uses: owner/action@<40-char-sha> # v1.2.3"
    )
