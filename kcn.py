from connectors.base import Connector


class KCN(Connector):
    id = "kcn"
    name = "KCN — Ketchum Cognitive Network"
    role = "Cognitive core connector"
    endpoint_env = "KCN_RUNTIME_ENDPOINT"
    description = "Interface to the KCN cognitive runtime. KCN is an authoritative external system: this package connects to it, it never replaces or redefines it."
    capabilities = ["forward a task to the configured KCN endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "status", "run-task"]
