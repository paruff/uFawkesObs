#!/usr/bin/env python3
"""OTLP round-trip: send one trace, log and metric to the Collector, then poll
Tempo, Loki and Prometheus until each shows it. Stdlib only; needs `make up`.

Exit 0 when all three signals arrive; otherwise exit 1 naming the missing ones
and printing the Collector log tail.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

OTLP = os.environ.get("SMOKE_OTLP_URL", "http://localhost:4318")
TEMPO = os.environ.get("SMOKE_TEMPO_URL", "http://localhost:3200")
LOKI = os.environ.get("SMOKE_LOKI_URL", "http://localhost:3100")
PROM = os.environ.get("SMOKE_PROM_URL", "http://localhost:9090")
TIMEOUT = int(os.environ.get("SMOKE_TIMEOUT", "60"))
COLLECTOR = os.environ.get("SMOKE_COLLECTOR_CONTAINER", "otel-collector")
SERVICE = "smoke-telemetry"


def _resource(run_id):
    return {
        "attributes": [
            {"key": "service.name", "value": {"stringValue": SERVICE}},
            {"key": "smoke.run_id", "value": {"stringValue": run_id}},
        ]
    }


def _attr(run_id):
    return [{"key": "run_id", "value": {"stringValue": run_id}}]


def payloads(run_id, now_ns):
    ts = str(now_ns)
    return {
        "traces": {
            "resourceSpans": [
                {
                    "resource": _resource(run_id),
                    "scopeSpans": [
                        {
                            "spans": [
                                {
                                    "traceId": uuid.uuid4().hex,
                                    "spanId": uuid.uuid4().hex[:16],
                                    "name": "smoke-span",
                                    "kind": 1,
                                    "startTimeUnixNano": ts,
                                    "endTimeUnixNano": str(now_ns + 1_000_000),
                                    "attributes": _attr(run_id),
                                }
                            ]
                        }
                    ],
                }
            ]
        },
        "logs": {
            "resourceLogs": [
                {
                    "resource": _resource(run_id),
                    "scopeLogs": [
                        {
                            "logRecords": [
                                {
                                    "timeUnixNano": ts,
                                    "severityText": "INFO",
                                    "body": {
                                        "stringValue": f"smoke-telemetry {run_id}"
                                    },
                                    "attributes": _attr(run_id),
                                }
                            ]
                        }
                    ],
                }
            ]
        },
        "metrics": {
            "resourceMetrics": [
                {
                    "resource": _resource(run_id),
                    "scopeMetrics": [
                        {
                            "metrics": [
                                {
                                    "name": "smoke_probe",
                                    "gauge": {
                                        "dataPoints": [
                                            {
                                                "timeUnixNano": ts,
                                                "asDouble": 1.0,
                                                "attributes": _attr(run_id),
                                            }
                                        ]
                                    },
                                }
                            ]
                        }
                    ],
                }
            ]
        },
    }


def get_json(url):
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def send(signal, body):
    req = urllib.request.Request(
        f"{OTLP}/v1/{signal}",
        json.dumps(body).encode(),
        {"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=10).read()


def tempo_has(run_id, _now_ns):
    q = urllib.parse.urlencode({"q": f'{{ span.run_id = "{run_id}" }}'})
    return bool(get_json(f"{TEMPO}/api/search?{q}").get("traces"))


def loki_has(run_id, now_ns):
    q = urllib.parse.urlencode(
        {
            "query": f'{{service_name="{SERVICE}"}} |= "{run_id}"',
            "start": now_ns - 300 * 10**9,
            "end": now_ns + 300 * 10**9,
        }
    )
    return bool(get_json(f"{LOKI}/loki/api/v1/query_range?{q}")["data"]["result"])


def prom_has(run_id, _now_ns):
    q = urllib.parse.urlencode(
        {"query": f'{{__name__=~".*smoke_probe.*",run_id="{run_id}"}}'}
    )
    return bool(get_json(f"{PROM}/api/v1/query?{q}")["data"]["result"])


CHECKS = {"traces": tempo_has, "logs": loki_has, "metrics": prom_has}


def collector_tail():
    try:
        out = subprocess.run(
            ["docker", "logs", "--tail", "40", COLLECTOR],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return out.stdout + out.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return f"(could not read collector logs: {exc})"


def main():
    run_id = uuid.uuid4().hex[:12]
    now_ns = time.time_ns()
    for signal, body in payloads(run_id, now_ns).items():
        try:
            send(signal, body)
        except (OSError, urllib.error.URLError) as exc:
            print(f"FAIL: could not send {signal} to {OTLP}: {exc} (is the stack up?)")
            return 1
    pending = dict(CHECKS)
    errors = {}
    deadline = time.monotonic() + TIMEOUT
    while pending and time.monotonic() < deadline:
        for name, check in list(pending.items()):
            try:
                if check(run_id, now_ns):
                    print(f"ok: {name} arrived (run {run_id})")
                    del pending[name]
            except (OSError, urllib.error.URLError, KeyError, ValueError) as exc:
                errors[name] = repr(exc)  # retry until the deadline, but report it
        if pending:
            time.sleep(2)
    if pending:
        print(
            f"FAIL: signal(s) never arrived within {TIMEOUT}s: {', '.join(pending)} (run {run_id})"
        )
        for name in pending:
            if name in errors:
                print(f"last {name} query error: {errors[name]}")
        print("--- collector log tail ---")
        print(collector_tail())
        return 1
    print("PASS: traces, logs and metrics all traversed Collector -> backend")
    return 0


if __name__ == "__main__":
    sys.exit(main())
