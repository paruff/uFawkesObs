"""Synthetic workload generators for acceptance tests."""

from tests.acceptance.workloads.synthetic_trace import SyntheticTraceWorkload
from tests.acceptance.workloads.synthetic_metric import SyntheticMetricWorkload
from tests.acceptance.workloads.synthetic_log import SyntheticLogWorkload

__all__ = [
    "SyntheticTraceWorkload",
    "SyntheticMetricWorkload",
    "SyntheticLogWorkload",
]
