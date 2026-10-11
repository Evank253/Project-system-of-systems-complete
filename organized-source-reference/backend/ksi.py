from connectors.base import Connector


class KSI(Connector):
    id = "ksi"
    name = "KSI — Human-Authority Governance"
    role = "Governance connector"
    endpoint_env = "KSI_RUNTIME_ENDPOINT"
    description = "Interface to the KSI governance system. Authority decisions belong to KSI and human operators; this public layer can only query and report."
    capabilities = ["query the configured KSI endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "authority-state"]
