import inspect
from typing import Any, Callable, Type, TypeVar
import logging
from inspect import isabstract
from .singleton import singleton


T = TypeVar('T')

# Some excepcions


class NotSuchProviderException(Exception):
    def __init__(self, target: Type):
        super().__init__(f"There aren't providers for {target}")


class ContextOnlyException(Exception):
    def __init__(self, target: Type):
        super().__init__(f"{target} should be only be injected in a Context")


class NotContextFoundException(Exception):
    def __init__(self, instance: Any):
        super().__init__(f"{instance} doesn't have a Context")


class InstanceAlreadyExistsInContextException(Exception):
    def __init__(self, ctx, target: Type):
        super().__init__(
            f"For context {ctx}, instance of {target} have been created")


class InvalidClassForProviderException(Exception):
    def __init__(self, target: Type):
        super().__init__(
            f"{target} is not a interface, providers should be for interfaces")


@singleton
class ProviderRegistry:
    __provider: dict[Type, Callable[[], Any]]
    __providerForContext: dict[Type, Callable[[Any], Any]]

    def __init__(self):
        self.__provider = dict()
        self.__providerForContext = dict()

    def __solveClassForProvider(self, func):
        if inspect.isclass(func):
            return func
        elif 'return' in func.__annotations__:
            typerRef = func.__annotations__['return']
            if isinstance(typerRef, Type):
                return typerRef
            return typerRef

        return func

    def register_provider(self, target: Type, func: Callable[[], T]):
        if not isabstract(target):
            raise InvalidClassForProviderException(target)
        typeRef = self.__solveClassForProvider(func)
        logging.debug(f"Register provider for {target} with {typeRef}.")
        self.__provider[target] = func

    def register_provider_for_context(self, target: Type, func: Callable[[Any], Any]):
        if not isabstract(target) and not hasattr(target, '__context_only'):
            raise InvalidClassForProviderException(target)
        typeRef = self.__solveClassForProvider(func)
        logging.debug(
            f"For contexts, register provider for {target} with {typeRef}.")
        self.__providerForContext[target] = func

    def get(self, target: Type):
        if target not in self.__provider:
            raise NotSuchProviderException(target)
        return self.__provider[target]()

    def _createInstanceForContext(self, ctx, target: Type):
        if target not in self.__providerForContext:
            raise NotSuchProviderException(target)
        if target not in ctx._instances:
            return self.__providerForContext[target](ctx)
        raise InstanceAlreadyExistsInContextException(ctx, target)


# Context, it should only hold instances
class Context:
    _instances: dict[Type[T], T]

    def __init__(self):
        self._instances = dict()

    def get_instance(self, target: Type[T]) -> T:
        if target not in self._instances:
            instance = ProviderRegistry()._createInstanceForContext(self, target)
            setattr(instance, '__context_only', self)
            self._instances[target] = instance
        return self._instances[target]


def inject(type: Type[T]) -> T:
    """Dependency injection where is applicable and isn't context_scoped.\n
    I made it just to use diferent implemetation depending on configuration
    """
    if hasattr(type, '__context_only'):
        raise ContextOnlyException(type)
    if isabstract(type):
        provider = ProviderRegistry()
        return provider.get(type)
    else:
        """
        If it's a class, it shouldn't have a provider.
         And if it's a singleton, there should be only one
        """
        return type()


def context_scoped(cls):
    """Decorator to add a hidden attribute to Class to indicate it's instances are only for scoped for context"""
    setattr(cls, '__context_only', None)
    return cls


def get_context(instance) -> Context:
    if hasattr(instance, '__context_only'):
        return getattr(instance, '__context_only')
    raise NotContextFoundException(instance)
