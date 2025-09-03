from collections import defaultdict
from ctypes import Union
from decimal import Decimal
import json
import re
from typing import List, Optional
from .singleton import singleton
from .injection import *
from .hashing import *

import sys


class PropertyException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class InvalidIndexForPropertyException(PropertyException):
    def __init__(self, key: str, index: int, next_index: int):
        super().__init__(
            f"Next index for \"{key}\" should be {next_index}, but got {index}")


class RepeatedKeyException(PropertyException):
    def __init__(self, key: str):
        super().__init__(f"{key} is already defined")


type Property = Union[str, List[str]]


@singleton
class Properties:
    __cached: dict[str, Property] = dict()
    __listReader = re.compile(
        r"^((?:[A-Za-z](?:\.(?=[^\=]))?)+(\[\d+\])?)=(.*)$")

    def __init__(self):
        self.__loadFromFile()
        for arg in sys.argv:
            pass

    def __loadFromFile(self, profile: str = 'default'):
        arrays = defaultdict[str,  List[str]](list)
        single = dict[str, str]()
        with open(f"{profile}.properties", 'r') as file:
            for line in file:
                m = self.__listReader.search(line)
                if m is None:
                    continue
                match m.groups():
                    case key, None, value:
                        if key in arrays or key in single:
                            raise RepeatedKeyException(key)
                        single[key] = value
                    case key, index, value:
                        if key in single:
                            raise RepeatedKeyException(key)
                        arr: List[str] = arrays[key]
                        if index != len(arr):
                            raise InvalidIndexForPropertyException(
                                key, index, len(arr))
                        arr.append(value)
        self.__cached.update(arrays)
        self.__cached.update(single)

    def getProperty(self, key: str) -> Optional[Property]:
        if key in self.__cached:
            return self.__cached[key]
        return None


def value(key: str, default: Optional[str] = None) -> Optional[Property]:
    val = Properties().getProperty(key)
    if val == None:
        return default
    return val

def to_json(target: Any) -> str:
    return json.dumps(target, default=lambda o: o.__dict__)