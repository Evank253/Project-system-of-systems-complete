from connectors.base import Connector


class TEVV(Connector):
    id = "tevv"
    name = "TEVV — Test, Evaluation, Verification & Validation"
    role = "Evaluation infrastructure connector"
    endpoint_env = "TEVV_RUNTIME_ENDPOINT"
    description = "Interface to the TEVV infrastructure. Verification issued by this public layer would be self-issued; real verification must come from TEVV and independent witnesses."
    capabilities = ["submit an evaluation request to the configured TEVV endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "submit-evaluation"]
