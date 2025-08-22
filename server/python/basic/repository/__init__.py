from util import Context
from .base import *
from .question import *
from .users import *


def load_repository():
    providerRegistry = ProviderRegistry()
    match value('datasource.type'):
        case 'SQLite3':
            logging.debug(f"Loading datasource \"SQLite3\"...")
            providerRegistry.register_provider(Datasource, SQLite3Datasource)
            def getUserRepository(ctx: Context) -> UserRepositorySqlite3Impl:
                return UserRepositorySqlite3Impl()
            providerRegistry.register_provider_for_context(UserRepository, getUserRepository)
            logging.debug(f"Loaded datasource \"SQLite3\"")
        case _:
            raise Exception("Not datasource configured")
    
    # Running init scripts
    datasource = inject(Datasource)
    datasource.init()

    def getTransactionForContext(ctx: Context) -> DataSession:
        dataSource = inject(Datasource)
        return dataSource.createSession()
    
    providerRegistry.register_provider_for_context(DataSession, getTransactionForContext)
