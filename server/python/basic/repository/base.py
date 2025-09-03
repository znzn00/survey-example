from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
import logging
import os
import sqlite3
from typing import Any, Optional
from util import inject, ProviderRegistry, singleton, context_scoped, value

logger = logging.getLogger('Repository')

class DataSessionState(Enum):
    NOT_CHANGES = 0
    CHANGES = 1
    ERROR = 2
    CLOSED = 3


@context_scoped
class DataSession(ABC):
    state: DataSessionState = DataSessionState.NOT_CHANGES

    @abstractmethod
    def run(func: Callable[[Any], None]):
        pass

    @abstractmethod
    def query(self, *args, **kwargs):
        pass

    @abstractmethod
    def close(self):
        pass

    def notifyError(self):
        self.state = DataSessionState.ERROR
        self.close()


class Datasource(ABC):
    @abstractmethod
    def createSession(self) -> DataSession:
        pass

    @abstractmethod
    def init(self):
        pass


class SQLite3Session(DataSession):
    __conn: sqlite3.Connection

    def __init__(self, conn: sqlite3.Connection):
        logger.debug(f"{self} started")
        super().__init__()
        self.__conn = conn

    def run(self, func: Callable[[sqlite3.Connection], None]):
        if self.state == DataSessionState.ERROR:
            return
        self.state = DataSessionState.CHANGES
        func(self.__conn)

    def query(self, *args, **kwargs):
        return self.__conn.execute(*args)

    def close(self):
        match self.state:
            case DataSessionState.CLOSED:
                logger.debug(f"{self} is already stopped")
                return
            case DataSessionState.ERROR:
                self.__conn.rollback()
            case DataSessionState.CHANGES:
                self.__conn.commit()
        self.__conn.close()
        self.state = DataSessionState.CLOSED
        logger.debug(f"{self} stopped")

    def __del__(self):
        # Just making sure it's destroyed
        if self.state == DataSessionState.CLOSED:
            logger.debug(f"{self} destroyed")
            return
        self.close()
        logger.debug(f"{self} destroyed")


@singleton
class SQLite3Datasource(Datasource):
    file = value('datasource.sqlite.file')

    def __init__(self):
        super().__init__()

    def init(self):
        if not os.path.exists(self.file):
            self.__runInitScript()
        elif value('datasource.prune', '').lower() == 'true':
            os.remove(self.file)
            self.__runInitScript()

    def __runInitScript(self):
        logger.info("Executing init script", exc_info=type(self))
        conn = self.__createConn()
        with open('../../../planning/sqlite3.sql', 'r') as script:
            conn.executescript(script.read())
        conn.commit()
        conn.close()

    def __createConn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.file, autocommit=False)

    def createSession(self) -> DataSession:
        return SQLite3Session(self.__createConn())
