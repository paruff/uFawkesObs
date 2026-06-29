"""
Log emitter workload for acceptance tests.

This module provides a thin facade over the SyntheticLogWorkload's
structured JSON log generation capabilities to match the Phase 4 workload
specification.

Usage::

    from tests.acceptance.workloads.log_emitter import LogEmitterWorkload

    workload = LogEmitterWorkload()
    test_id = workload.emit_log(body={"event": "test_event"})
"""

from tests.acceptance.workloads.synthetic_log import (
    SyntheticLogWorkload,
)


class LogEmitterWorkload(SyntheticLogWorkload):
    """Log emitter workload.

    Generates structured JSON log entries via the OTLP logs signal
    with configurable rate and content.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
