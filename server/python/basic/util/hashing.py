from abc import ABC, abstractmethod
import hashlib

class PasswordEncoder(ABC):
    @abstractmethod
    def encode(self, pwd: str)->str:
        pass

class Md5PasswordEncoder(PasswordEncoder):
    def __init__(self):
        pass

    def encode(self, pwd: str)->str:
        return hashlib.md5(pwd.encode("utf-8")).hexdigest()