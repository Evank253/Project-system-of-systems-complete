"""Connector base: every connector reports factual state or measured results. Fabrication is structurally impossible: there is no code path that returns PASS without a real configured runtime answering."""
import os
import time
from typing import Any, Dict, Optional

import requests


class ConnectorResult:
    __slots__ = ("state", "ok", "summary", "details", "measured", "evidence_level")

    def __init__(self, state: str, summary: str, details: str = "", measured: Optional[Dict[str, Any]] = None, ok: Optional[bool] = None, evidence_level: str = "NOT_MEASURED"):
        self.state = state
        self.ok = ok
        self.summary = summary
        self.details = details
        self.measured = measured or {}
        self.evidence_level = evidence_level


class Connector:
    id: str = "connector"
    name: str = "Connector"
    role: str = ""
    endpoint_env: str = ""
    description: str = ""
    capabilities: list = []
    suggested_tasks: list = ["ping", "status"]

    @classmethod
    def is_configured(cls) -> bool:
        return bool(os.environ.get(cls.endpoint_env))

    @classmethod
    def describe(cls) -> dict:
        return {
            "connector_id": cls.id,
            "name": cls.name,
            "role": cls.role,
            "description": cls.description,
            "endpoint_env": cls.endpoint_env,
            "capabilities": cls.capabilities,
            "lifecycle_status": "INTEGRATION_REQUIRED",
            "deployment_state": "CONFIGURED" if cls.is_configured() else "NOT_CONFIGURED",
        }

    @classmethod
    def execute(cls, task: str, params: Dict[str, Any]) -> ConnectorResult:
        endpoint = os.environ.get(cls.endpoint_env)
        if not endpoint:
            return ConnectorResult(
                state="NOT_CONFIGURED",
                ok=None,
                summary=f"{cls.name}: no runtime endpoint is configured.",
                details=f"Set environment variable {cls.endpoint_env} to the real [API_ENDPOINT] of the authoritative {cls.name} system. Until then this connector reports NOT_CONFIGURED and asserts nothing.",
                measured={"endpoint_env": cls.endpoint_env, "configured": False},
            )
        try:
            t0 = time.perf_counter()
            resp = requests.post(endpoint, json={"connector": cls.id, "task": task, "params": params}, timeout=8)
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        except requests.exceptions.Timeout:
            return ConnectorResult(state="UNAVAILABLE", ok=False, summary=f"{cls.name}: runtime endpoint timed out after 8s.", details=f"Real network timeout against {cls.endpoint_env}. No result is claimed.", measured={"endpoint_env": cls.endpoint_env, "error": "timeout"})
        except requests.exceptions.RequestException as e:
            return ConnectorResult(state="UNAVAILABLE", ok=False, summary=f"{cls.name}: runtime endpoint unreachable.", details=f"{type(e).__name__}: {e}", measured={"endpoint_env": cls.endpoint_env, "error": type(e).__name__})
        try:
            body = resp.json()
        except ValueError:
            body = {}
        if resp.status_code == 200 and body.get("ok") is True:
            return ConnectorResult(state="PASS", ok=True, summary=str(body.get("summary", f"{cls.name}: runtime returned ok.")), details=body.get("details", ""), measured={"latency_ms": latency_ms, "http_status": 200, "endpoint_env": cls.endpoint_env, "runtime": body.get("runtime", "[RUNTIME_IDENTIFIER]")}, evidence_level="NOT_MEASURED")
        if resp.status_code == 200:
            return ConnectorResult(state="FAIL", ok=False, summary=str(body.get("summary", f"{cls.name}: runtime answered with a failure.")), details=body.get("details", ""), measured={"latency_ms": latency_ms, "http_status": 200})
        return ConnectorResult(state="UNAVAILABLE", ok=False, summary=f"{cls.name}: runtime endpoint returned HTTP {resp.status_code}.", details=f"Real HTTP status from {cls.endpoint_env}. No result is claimed.", measured={"latency_ms": latency_ms, "http_status": resp.status_code})
