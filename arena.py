from connectors.base import Connector


class ARENA(Connector):
    id = "arena"
    name = "ARENA — Evaluation Environment"
    role = "Arena environment connector"
    endpoint_env = "ARENA_RUNTIME_ENDPOINT"
    description = "Interface to the ARENA evaluation environment. Benchmark runs happen in ARENA; until it is connected, no benchmark value can be produced here."
    capabilities = ["submit a run request to the configured ARENA endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "list-environments"]
