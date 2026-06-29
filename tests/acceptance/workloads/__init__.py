"""Synthetic workload generators for acceptance tests.

Provides a registry of available workload generators for use in acceptance tests:
- `get_workload(workload_type, **kwargs)` — factory function to create workload instances
- Individual workload classes for different test scenarios:
  - Web API simulation (web_api module)
  - Batch job simulation (batch_job module)
  - Log emitter (log_emitter module)
  - DORA events (dora_events module)
- Directly exported:
  - SyntheticTraceWorkload (web api + batch job simulation)
  - SyntheticMetricWorkload (health check metrics)
  - SyntheticLogWorkload (log emission)
  - DORAWorkload (deployment, incident, lead-time traces)

Usage::

    from tests.acceptance.workloads import get_workload

    # Create workload via registry
    workload = get_workload("web_api", otlp_endpoint="http://localhost:4318")

    # Or use directly
    from tests.acceptance.workloads import SyntheticMetricWorkload
    metric_workload = SyntheticMetricWorkload()
"""

# Direct exports of all workload implementations
from tests.acceptance.workloads.synthetic_trace import SyntheticTraceWorkload
from tests.acceptance.workloads.synthetic_metric import SyntheticMetricWorkload
from tests.acceptance.workloads.synthetic_log import SyntheticLogWorkload
from tests.acceptance.workloads.dora_events import DORAWorkload


# Workload registry for discovery and factory patterns
def get_workload(workload_type: str, **kwargs):
    """Factory function to create workload instances by type.

    Args:
        workload_type: One of "web_api", "batch_job", "log_emitter", "dora".
        **kwargs: Arguments passed to workload constructors.

    Returns:
        Workload instance.

    Raises:
        ValueError: If workload_type is not recognized.
    """
    # Map workload types to constructor functions
    workload_registry = {
        "web_api": SyntheticTraceWorkload,
        "web": SyntheticTraceWorkload,  # Alias
        "batch_job": SyntheticTraceWorkload,  # Combined with web in existing implementation
        "batch": SyntheticTraceWorkload,  # Alias
        "log_emitter": SyntheticLogWorkload,
        "log": SyntheticLogWorkload,  # Alias
        "dora": DORAWorkload,
        "dora_events": DORAWorkload,
    }

    if workload_type not in workload_registry:
        available = ", ".join(sorted(workload_registry.keys()))
        raise ValueError(
            f"Unknown workload type '{workload_type}'. Available: {available}"
        )

    return workload_registry[workload_type](**kwargs)


# Export all exported workload classes
__all__ = [
    # Direct exports (maintain backward compatibility)
    "SyntheticTraceWorkload",
    "SyntheticMetricWorkload",
    "SyntheticLogWorkload",
    "DORAWorkload",
    # Registry function
    "get_workload",
]

# Legacy aliases for backward compatibility
# These allow tests to use either the new registry or direct imports
WebApiWorkload = SyntheticTraceWorkload
BatchJobWorkload = SyntheticTraceWorkload
LogEmitterWorkload = SyntheticLogWorkload
DORAEventWorkload = DORAWorkload

__all__.extend(
    [
        "WebApiWorkload",
        "BatchJobWorkload",
        "LogEmitterWorkload",
        "DORAEventWorkload",
    ]
)
