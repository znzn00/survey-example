
from typing import Type, TypeVar
import logging

logger = logging.getLogger('Singleton')

T = TypeVar('T')

class SingletonRegistry:
    """
    Just a static Class to hold all instancecs of Singleton
    """
    instances: dict[Type[T], T] = dict()

    @classmethod
    def _register(cls, clazz, instance):
        cls.instances[clazz] = instance
        return instance

    @classmethod
    def get_instance(cls, clazz):
        return cls.instances[clazz]


def singleton(cls: T):
    """
    Decorator to indicate it's singleton and any hold only one instance 
    even if there are multiple calls to it's constructor.
    """
    def get_instance(*args, **kwargs) -> Type[T]:
        if cls not in SingletonRegistry.instances:
            logger.debug(f"Created sigleton of {cls}")
            return SingletonRegistry._register(cls, cls(*args, **kwargs))
        return SingletonRegistry.get_instance(cls)
    
    return get_instance
