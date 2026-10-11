from connectors.base import Connector


class IndependentWitness(Connector):
    id = "independent-witness"
    name = "Independent Witness"
    role = "Third-party verification interface"
    endpoint_env = "WITNESS_ENDPOINT"
    description = "Reserved interface for independent witness verification. Verification cannot be self-issued by the system it verifies; this connector exists so the gate is explicit, not implied."
    capabilities = ["request a witness session from a configured witness endpoint", "report the factual connection state"]
    suggested_tasks = ["ping", "request-witness-session"]
