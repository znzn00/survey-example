

from abc import ABC, abstractmethod
import logging
from typing import Optional

from model import User
from util import context_scoped, get_context
from .base import DataSession, SQLite3Session


@context_scoped
class UserRepository(ABC):
    @abstractmethod
    def get_user_by_username_and_password(self, username: str, password: str) -> Optional[User]:
        pass


class UserRepositorySqlite3Impl(UserRepository):

    def __init__(self):
        super().__init__()


    def get_user_by_username_and_password(self, username: str, encoded_pwd: str) -> Optional[User]:
        context = get_context(self)
        transction: SQLite3Session = context.get_instance(DataSession)
        cursor = transction.query("SELECT user_id, role,name, username, password, organization_id FROM USER WHERE username=? AND password=? LIMIT 1", (username, encoded_pwd))
        row = cursor.fetchone()
        if row is None:
            return None
        return User(*row)
