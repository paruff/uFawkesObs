"""Current-state docs/config must not teach the retired DORA service topology.

`dora-compute`, `pushgateway` and `otel-collector-dora` do not exist on the
stack (ADR-007 fold; issues #266/#275): the `dora` profile adds only
`dora-api`, which computes the DORA metrics in-process and exposes them on
`:8088/metrics` for Prometheus pull (job_name ``dora-api`` — see the
replacement rationale in ``config/prometheus/prometheus.yaml``).

Deliberately allowlisted as historical records, not current-state claims:
CHANGELOG, ADRs, the migrated pre-consolidation design/spec docs (each
carries a status banner), and prometheus.yaml itself (which documents the
replacement). Every finding is printed in the assertion message — a silent
pass here would be indistinguishable from a check that never ran.
"""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RETIRED = ("dora-compute", "pushgateway", "otel-collector-dora")

ALLOWLIST = (
    "CHANGELOG.md",
    "config/prometheus/prometheus.yaml",  # replacement rationale comment
    "docs/adr/",  # ADRs are point-in-time records (incl. ADR-006/007)
    "docs/dora/design/",  # pre-consolidation design record, bannered
    "docs/dora/spec/",  # pre-implementation spec, bannered
    "docs/CONTRACTS.md",  # keeps a "not deployed" section for the inert collector
    "docs/product/design.md",  # supersession banner: "parts below no longer run"
    "docs/notes/",  # dated point-in-time plans (cite incidents by name)
    "config/otel/collector-dora.yaml",  # inert config retained deliberately (#534)
)

# (path, name) pairs: a file may discuss one retired name as removal history
# while still being held to the ban on the others. Every entry says why.
ALLOWED_NAMES = {
    (
        "config/prometheus/rules/ufawkesobs-dora-metrics.yml",
        "otel-collector-dora",
    ): "comments document the container's removal (issue #266), not a live path",
    (
        "docs/ai-sdlc/dora-current-state/plan.md",
        "dora-compute",
    ): "the plan records what this change removed; it is the change record, not the stack",
    (
        "docs/ai-sdlc/dora-current-state/plan.md",
        "pushgateway",
    ): "the plan records what this change removed; it is the change record, not the stack",
    (
        "docs/ai-sdlc/dora-current-state/plan.md",
        "otel-collector-dora",
    ): "the plan records what this change removed; it is the change record, not the stack",
}


def _current_state_files():
    files = []
    for base in ("docs", "config"):
        files += [p for p in (REPO / base).rglob("*") if p.is_file()]
    for extra in ("compose.yaml", "README.md"):
        p = REPO / extra
        if p.is_file():
            files.append(p)
    return files


def test_no_retired_dora_service_references():
    offenders = []
    for path in _current_state_files():
        rel = path.relative_to(REPO).as_posix()
        if any(rel == a or rel.startswith(a) for a in ALLOWLIST):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            # Not swallowed: an unreadable file is reported, never skipped
            # silently — unreadable current-state docs are findings too.
            offenders.append(f"{rel}: unreadable ({exc})")
            continue
        low = text.lower()
        for name in RETIRED:
            if name.lower() in low and (rel, name) not in ALLOWED_NAMES:
                offenders.append(f"{rel}: contains `{name}`")
    assert not offenders, (
        "retired DORA service references in current-state docs/config:\n"
        + "\n".join(offenders)
        + "\n(dora profile = dora-api only; pull model, job_name=dora-api. "
        "If this is a deliberate historical record, extend ALLOWLIST with a "
        "comment saying why.)"
    )


if __name__ == "__main__":
    try:
        test_no_retired_dora_service_references()
    except AssertionError as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1) from None
    print("test_docs_dora_freshness: OK — no retired DORA service references")
