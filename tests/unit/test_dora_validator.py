"""Unit tests for ingestion/api/validator.py.

Covers edge cases missed by the schema validation tests:
- _check_date_time with non-string input (line 21)
- _check_date_time with invalid datetime string (lines 25-26)
- ValidationDetail.to_dict() (line 72)
- validate_payload()'s dispatch logic (#278): test_dora_event_schemas.py
  calls jsonschema.validate() directly against the schema files, which
  bypasses validate_payload() entirely -- the actual function main.py's
  POST /event handler calls had zero direct coverage before this.
"""

from dora.ingestion.api.validator import (
    ValidationDetail,
    _check_date_time,
    validate_payload,
    validate_payloads,
)


class TestCheckDateTime:
    """Cover the uncovered branches in _check_date_time."""

    def test_non_string_input_returns_true(self):
        """Line 21: non-string input should return True (skip validation)."""
        assert _check_date_time(42) is True
        assert _check_date_time(None) is True
        assert _check_date_time([]) is True

    def test_invalid_datetime_string_returns_false(self):
        """Lines 25-26: invalid datetime strings should return False."""
        assert _check_date_time("not-a-date") is False
        assert _check_date_time("2024-13-01T00:00:00") is False  # month 13
        assert _check_date_time("") is False

    def test_valid_datetime_string_returns_true(self):
        """Valid ISO 8601 strings should return True."""
        assert _check_date_time("2024-01-15T10:30:00Z") is True
        assert _check_date_time("2024-01-15T10:30:00+00:00") is True


class TestValidationDetail:
    """Cover ValidationDetail.to_dict()."""

    def test_to_dict_with_field(self):
        """Line 72-75: to_dict with a field path."""
        detail = ValidationDetail(field=["body", "event_type"], message="Missing field")
        result = detail.to_dict()
        assert result == {
            "field": "body.event_type",
            "message": "Missing field",
        }

    def test_to_dict_without_field(self):
        """Line 72-75: to_dict with empty field list uses 'body'."""
        detail = ValidationDetail(field=[], message="General error")
        result = detail.to_dict()
        assert result == {
            "field": "body",
            "message": "General error",
        }


class TestValidatePayloadDispatch:
    """Cover validate_payload()'s own dispatch logic -- missing/unknown
    event_type and the pass/fail routing to the right schema -- not just
    the schemas themselves.
    """

    def test_missing_event_type_fails(self):
        result = validate_payload({"repo": "org/repo"})
        assert result.valid is False
        assert result.errors[0].field == ["event_type"]
        assert "required" in result.errors[0].message

    def test_event_type_none_fails(self):
        result = validate_payload({"event_type": None})
        assert result.valid is False
        assert result.errors[0].field == ["event_type"]

    def test_event_type_non_string_fails(self):
        result = validate_payload({"event_type": 123})
        assert result.valid is False
        assert result.errors[0].field == ["event_type"]
        assert "must be a string" in result.errors[0].message

    def test_unknown_event_type_fails(self):
        result = validate_payload({"event_type": "not-a-real-type"})
        assert result.valid is False
        assert result.errors[0].field == ["event_type"]
        assert "unknown event_type" in result.errors[0].message
        assert "deployment" in result.errors[0].message

    def test_valid_deployment_payload_dispatches_to_deployment_schema(self):
        payload = {
            "schema_version": "1.0",
            "event_type": "deployment",
            "repo": "org/repo",
            "service": "svc",
            "environment": "production",
            "commit_sha": "a" * 40,
            "deployed_at": "2024-01-15T10:30:00Z",
            "status": "success",
            "pipeline_url": "https://example.com/run/1",
        }
        result = validate_payload(payload)
        assert result.valid is True
        assert result.errors == []

    def test_invalid_deployment_payload_dispatches_to_deployment_schema(self):
        payload = {
            "schema_version": "1.0",
            "event_type": "deployment",
            "repo": "org/repo",
            "status": "not-a-valid-status",
        }
        result = validate_payload(payload)
        assert result.valid is False
        assert result.errors  # missing required fields + bad enum value

    def test_valid_incident_payload_dispatches_to_incident_schema(self):
        payload = {
            "schema_version": "1.0",
            "event_type": "incident",
            "repo": "org/repo",
            "service": "svc",
            "incident_id": "INC-1",
            "status": "opened",
            "occurred_at": "2024-01-15T10:30:00Z",
            "severity": "critical",
        }
        result = validate_payload(payload)
        assert result.valid is True

    def test_to_error_response_shape(self):
        result = validate_payload({"repo": "org/repo"})
        response = result.to_error_response()
        assert response == {
            "detail": [
                {
                    "loc": ["body", "event_type"],
                    "msg": "field is required and must be a string",
                    "type": "value_error",
                }
            ]
        }

    def test_to_error_response_on_valid_result_is_empty(self):
        payload = {
            "schema_version": "1.0",
            "event_type": "deployment",
            "repo": "org/repo",
            "service": "svc",
            "environment": "production",
            "commit_sha": "a" * 40,
            "deployed_at": "2024-01-15T10:30:00Z",
            "status": "success",
            "pipeline_url": "https://example.com/run/1",
        }
        result = validate_payload(payload)
        assert result.to_error_response() == {"detail": []}


class TestValidatePayloads:
    """Cover validate_payloads() -- one ValidationResult per payload,
    independent of the others' pass/fail state.
    """

    def test_mixed_valid_and_invalid_payloads(self):
        results = validate_payloads(
            [
                {"event_type": "deployment"},  # missing required fields
                {
                    "schema_version": "1.0",
                    "event_type": "incident",
                    "repo": "org/repo",
                    "service": "svc",
                    "incident_id": "INC-1",
                    "status": "resolved",
                    "occurred_at": "2024-01-15T10:30:00Z",
                    "severity": "minor",
                },
                {"event_type": "unknown-type"},
            ]
        )
        assert len(results) == 3
        assert results[0].valid is False
        assert results[1].valid is True
        assert results[2].valid is False
        assert "unknown event_type" in results[2].errors[0].message

    def test_empty_list_returns_empty_list(self):
        assert validate_payloads([]) == []
