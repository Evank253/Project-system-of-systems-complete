from connectors.base import Connector


class MANIFEX(Connector):
    id = "manifex"
    name = "MANIFEX — Engineering Intelligence & Execution OS"
    role = "Engineering execution connector"
    endpoint_env = "MANIFEX_RUNTIME_ENDPOINT"
    description = "Interface to the MANIFEX execution OS. MANIFEX remains the authoritative system; this connector only forwards tasks and reports real states."
    capabilities = ["forward a task to the configured MANIFEX endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "status", "dispatch-job"]
