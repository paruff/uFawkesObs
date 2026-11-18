"""GitHub DORA collectors send auth, lead-time fields and a real deploy time (DC-03)."""

from pathlib import Path

import pytest
import yaml

DIR = Path(__file__).resolve().parents[2] / "dora" / "collectors" / "github"
DEPLOY = (DIR / "dora-deployment-event.yml").read_text()
PR = (DIR / "dora-pr-event.yml").read_text()


@pytest.mark.parametrize("text", [DEPLOY, PR], ids=["deployment", "pr"])
def test_sends_bearer_token_when_secret_set(text):
    assert "Authorization: Bearer" in text
    assert "secrets.DORA_API_KEY" in text
    on = yaml.safe_load(text)[True]["workflow_call"]
    assert on["secrets"]["DORA_API_KEY"]["required"] is False


@pytest.mark.parametrize("text", [DEPLOY, PR], ids=["deployment", "pr"])
def test_fails_the_step_on_a_4xx(text):
    arm = text.split("4??)")[1].split(";;")[0]
    assert "exit 1" in arm and "::warning::" not in arm


def test_deployment_sends_lead_time_fields():
    assert "first_commit_at" in DEPLOY and "pr_merged_at" in DEPLOY
    assert "pull-requests: read" in DEPLOY


def test_deployed_at_is_not_the_commit_time():
    assert "head_commit.timestamp" not in DEPLOY.split("steps:")[1]
