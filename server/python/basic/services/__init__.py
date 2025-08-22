import logging
from util import ProviderRegistry
from .auth import *


def load_services():
    providerRegistry = ProviderRegistry()
    providerRegistry.register_provider_for_context(AuthService, lambda _: AuthService())
