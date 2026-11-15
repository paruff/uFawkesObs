# Plan: Medium and Low audit findings (AF-02 06 09 10 14)

The suite integration harness in uFawkes.dev (`tests/suite-integration`) found
these bugs. Each finding and its stated fix is in
`AUDIT_FINDINGS.md` there. This repository's share:

- AF-02: deployments dedupe on identity, not the whole payload.
- AF-06: future-dated deployments and negative lead times are rejected.
- AF-09: a missing required field is named in the error location.
- AF-10: `pipeline_url` is checked as a URI.
- AF-14: `deploy-marker` exits non-zero without a commit SHA or pipeline URL.
- Unit tests for the new rules are in `tests/unit/test_dora_validator.py`.

## Verification Strategy

- Each finding has a harness test that asserts the correct behaviour. The test
  failed before this change and passes after it.
- `make suite-integration-test` in uFawkes.dev, run with this branch checked
  out beside the other five repositories: all tests pass, no finding
  reproduction is left.
- Pre-commit passes on this branch.
