"""Schema validator for canonical uFawkesDORA event schemas.

Validates incoming event payloads against the JSON Schema files in events/.
Returns structured 422 errors with field-level detail — not just "invalid".
"""

import datetime
import json
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft7Validator, FormatChecker

# ── Format checker for date-time ───────────────────────────────────────────────
# jsonschema does not ship with date-time format validation by default.


def _check_date_time(instance: str) -> bool:
    """Validate RFC 3339 date-time strings: a time and a UTC offset are required."""
    if not isinstance(instance, str):
        return True
    try:
        return (
            datetime.datetime.fromisoformat(instance).tzinfo is not None
            and "T" in instance
        )
    except (ValueError, TypeError):
        return False


_format_checker = FormatChecker()
_format_checker.checks("date-time")(_check_date_time)


@_format_checker.checks("uri")
def _check_uri(instance: str) -> bool:
    """An absolute URI: a scheme, a host, no whitespace."""
    if not isinstance(instance, str):
        return True
    parsed = urlparse(instance)
    return bool(parsed.scheme and parsed.netloc) and not any(
        c.isspace() for c in instance
    )


# A clock this far ahead of the server is skew, not a future deployment.
_MAX_CLOCK_SKEW = datetime.timedelta(minutes=5)


def _parse_iso(value: object) -> datetime.datetime | None:
    try:
        return datetime.datetime.fromisoformat(value)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def _check_deployment_times(payload: dict) -> list["ValidationDetail"]:
    """Cross-field rules a JSON Schema cannot state (AF-06)."""
    if payload.get("event_type") != "deployment":
        return []
    deployed = _parse_iso(payload.get("deployed_at"))
    first = _parse_iso(payload.get("first_commit_at"))
    if deployed is None or deployed.tzinfo is None:
        return []
    errors = []
    now = datetime.datetime.now(datetime.UTC)
    if deployed > now + _MAX_CLOCK_SKEW:
        errors.append(ValidationDetail(["deployed_at"], "deployed_at is in the future"))
    if first is not None and first.tzinfo is not None and first > deployed:
        errors.append(
            ValidationDetail(
                ["first_commit_at"], "first_commit_at is after deployed_at"
            )
        )
    return errors


# ── Schema registry ────────────────────────────────────────────────────────────

# Map event_type constant → schema filename
EVENT_TYPE_SCHEMA_MAP: dict[str, str] = {
    "deployment": "deployment-event.schema.json",
    "incident": "incident-event.schema.json",
    "pr": "pr-event.schema.json",
    "rework": "rework-event.schema.json",
}

# Cache loaded schemas
_schema_cache: dict[str, dict] = {}


def _get_schema_dir() -> Path:
    """Return the path to the events/ directory relative to this file."""
    return Path(__file__).resolve().parent.parent.parent / "events"


def _load_schema(filename: str) -> dict:
    """Load a JSON Schema file, caching it for subsequent calls."""
    if filename not in _schema_cache:
        schema_path = _get_schema_dir() / filename
        with open(schema_path) as f:
            _schema_cache[filename] = json.load(f)
    return _schema_cache[filename]


# ── Public API ─────────────────────────────────────────────────────────────────


class ValidationDetail:
    """Holds a single field-level validation error."""

    def __init__(self, field: list[str], message: str):
        self.field = field
        self.message = message

    def to_dict(self) -> dict:
        return {
            "field": ".".join(str(p) for p in self.field) if self.field else "body",
            "message": self.message,
        }


class ValidationResult:
    """Result of validating an event payload against its schema."""

    def __init__(
        self, valid: bool = False, errors: list[ValidationDetail] | None = None
    ):
        self.valid = valid
        self.errors = errors or []

    def to_error_response(self) -> dict:
        return {
            "detail": [
                {
                    "loc": ["body", e.field[0]] if e.field else ["body"],
                    "msg": e.message,
                    "type": "value_error",
                }
                for e in self.errors
            ]
        }


def _missing_field_details(error) -> list["ValidationDetail"]:
    """One detail per missing field, so `loc` names it (AF-09); `path` is only the parent."""
    missing = [f for f in error.validator_value if f not in error.instance]
    return [
        ValidationDetail(field=[*error.path, f], message=error.message) for f in missing
    ]


def validate_payload(payload: dict) -> ValidationResult:
    """Validate an event payload against its canonical schema.

    Steps:
    1. Check that ``event_type`` is present and known.
    2. Load the corresponding schema.
    3. Validate the payload, collecting field-level errors.

    Returns a ``ValidationResult`` — check ``.valid`` before using.
    """
    # Step 1: event_type must be present
    event_type = payload.get("event_type")
    if not event_type or not isinstance(event_type, str):
        return ValidationResult(
            errors=[
                ValidationDetail(
                    field=["event_type"],
                    message="field is required and must be a string",
                )
            ]
        )

    # Step 2: event_type must be known
    schema_file = EVENT_TYPE_SCHEMA_MAP.get(event_type)
    if schema_file is None:
        return ValidationResult(
            errors=[
                ValidationDetail(
                    field=["event_type"],
                    message=f"unknown event_type '{event_type}'. "
                    f"Supported: {', '.join(EVENT_TYPE_SCHEMA_MAP.keys())}",
                )
            ]
        )

    # Step 3: load schema and validate
    schema = _load_schema(schema_file)

    # Build a validator with format checking
    validator = Draft7Validator(schema, format_checker=_format_checker)

    errors: list[ValidationDetail] = []
    for error in sorted(validator.iter_errors(payload), key=lambda e: list(e.path)):
        if error.validator == "required":
            errors.extend(_missing_field_details(error))
            continue
        errors.append(
            ValidationDetail(
                field=list(error.path),
                message=error.message,
            )
        )
    if not errors:
        errors = _check_deployment_times(payload)

    if errors:
        return ValidationResult(errors=errors)

    return ValidationResult(valid=True)


def validate_payloads(payloads: list[dict]) -> list[ValidationResult]:
    """Validate multiple event payloads, returning one result per payload."""
    return [validate_payload(p) for p in payloads]
