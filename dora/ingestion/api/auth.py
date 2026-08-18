"""Optional bearer-token auth for the DORA ingestion API.

DORA_API_KEY is optional (local/dev default: unset, ingestion stays open —
see collector scripts under dora/collectors/*/ which already document it
as "if auth is enabled"). When set, every request must present a matching
`Authorization: Bearer <DORA_API_KEY>` header.
"""

import os
import secrets

from fastapi import Header, HTTPException


async def require_api_key(authorization: str | None = Header(default=None)) -> None:
    api_key = os.environ.get("DORA_API_KEY", "")
    if not api_key:
        return
    expected = f"Bearer {api_key}"
    if not authorization or not secrets.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
