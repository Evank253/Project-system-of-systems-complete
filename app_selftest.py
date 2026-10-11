import os
import time

from connectors.base import Connector, ConnectorResult


class AppSelftest(Connector):
    id = "app-selftest"
    name = "Public App Self-Test"
    role = "Real, reproducible execution performed by this deployment itself"
    endpoint_env = "APP_SELFTEST_TARGET"
    description = "The only connector with a real runtime in this package: the public application itself. It measures a real MongoDB round-trip on the running deployment. Its result is a measured fact about this infrastructure layer — about nothing else."
    capabilities = ["measure real datastore round-trip latency on this deployment", "record a hashed evidence record of the attempt"]
    suggested_tasks = ["datastore-ping", "health-probe"]

    @classmethod
    def is_configured(cls) -> bool:
        return True

    @classmethod
    def execute(cls, task: str, params=None) -> ConnectorResult:
        params = params or {}
        t0 = time.perf_counter()
        try:
            from pymongo import MongoClient

            client = MongoClient(os.environ["MONGO_URL"], serverSelectionTimeoutMS=3000)
            dbname = os.environ["DB_NAME"]
            client[dbname].command("ping")
            latency_ms = round((time.perf_counter() - t0) * 1000, 2)
            client.close()
            return ConnectorResult(
                state="PASS",
                ok=True,
                summary=f"Self-test executed for real: datastore ping round-trip measured {latency_ms} ms.",
                details=f"Measured against this deployment's own datastore ({dbname}). This PASS covers this infrastructure layer only — not KCN, MANIFEX, KSI, TEVV, or any external system.",
                measured={"mongo_ping_ms": latency_ms, "task": task, "database": dbname},
            )
        except Exception as e:
            return ConnectorResult(
                state="UNAVAILABLE",
                ok=False,
                summary="Self-test could not reach this deployment's own datastore.",
                details=f"{type(e).__name__}: {e}",
                measured={"elapsed_ms": round((time.perf_counter() - t0) * 1000, 2)},
            )
