"""Unit tests for optional bearer-token auth on the DORA ingestion API.

dora/collectors/*/ scripts already document DORA_API_KEY as an optional
env var sent as `Authorization: Bearer $DORA_API_KEY` "if auth is enabled"
(see dora/collectors/generic/curl-examples.sh, manual-incident/*.sh,
woodpecker/pipeline-snippet.yml) — but dora/ingestion/api/main.py never
enforced it. These tests pin the enforcement behavior: open when
DORA_API_KEY is unset (local/dev default), required when it is set.
"""

import sys
from pathlib import Path

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dora"))

from ingestion.api.auth import require_api_key  # noqa: E402


class TestRequireApiKey:
    @pytest.mark.asyncio
    async def test_open_when_key_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("DORA_API_KEY", raising=False)
        await require_api_key(authorization=None)

    @pytest.mark.asyncio
    async def test_open_when_key_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DORA_API_KEY", "")
        await require_api_key(authorization=None)

    @pytest.mark.asyncio
    async def test_accepts_matching_bearer_token(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DORA_API_KEY", "secret123")
        await require_api_key(authorization="Bearer secret123")

    @pytest.mark.asyncio
    async def test_rejects_missing_header_when_key_set(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DORA_API_KEY", "secret123")
        with pytest.raises(HTTPException) as exc_info:
            await require_api_key(authorization=None)
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rejects_wrong_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DORA_API_KEY", "secret123")
        with pytest.raises(HTTPException) as exc_info:
            await require_api_key(authorization="Bearer wrong")
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rejects_malformed_header(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DORA_API_KEY", "secret123")
        with pytest.raises(HTTPException) as exc_info:
            await require_api_key(authorization="secret123")
        assert exc_info.value.status_code == 401
