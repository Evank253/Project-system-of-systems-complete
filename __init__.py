from connectors.app_selftest import AppSelftest
from connectors.kcn import KCN
from connectors.manifex import MANIFEX
from connectors.ksi import KSI
from connectors.tevv import TEVV
from connectors.arena import ARENA
from connectors.witness import IndependentWitness

CONNECTORS = {c.id: c for c in [AppSelftest(), KCN(), MANIFEX(), KSI(), TEVV(), ARENA(), IndependentWitness()]}
