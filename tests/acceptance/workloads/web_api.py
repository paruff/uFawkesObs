"""
Web API simulation workload for acceptance tests.

This module provides a thin facade over the SyntheticTraceWorkload's
web request simulation capabilities to match the Phase 4 workload
specification.

Usage::

    from tests.acceptance.workloads.web_api import WebApiWorkload

    workload = WebApiWorkload()
    trace_id = workload.simulate_request(path="/api/orders")
"""

from tests.acceptance.workloads.synthetic_trace import (
    SyntheticTraceWorkload,
)


class WebApiWorkload(SyntheticTraceWorkload):
    """Web API workload simulation.

    Implements web request patterns including handler, database query,
    and external API call spans.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
