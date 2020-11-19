""" Skill SDK for Python """

import importlib
import contextlib
from typing import Callable, ContextManager

from . import manage

from .skill import (
    initialize,
    intent_handler,
    test_intent
)

from .intents import (
    Context,
    context
)

from .sessions import Session

from .responses import (
    Card,
    Response,
    Reprompt,
    ask,
    tell,
    ask_freetext
)


def lazy_load(
        module: str,
        attr: str
) -> Callable[..., ContextManager]:
    """ Lazy load a context manager from module, return `contextlib.suppress` (no-op) if loading failed

    :param module:  Module name
    :param attr:    Context manager name
    :return:
    """
    def wrapper(*args) -> ContextManager:
        """ Get a context manager
        """
        try:
            cls = getattr(importlib.import_module(module, __package__), attr)
        except (AttributeError, ModuleNotFoundError):
            cls = contextlib.suppress
        return cls(*args)
    return wrapper


K8sChecks = lazy_load('.services.k8s', 'K8sChecks')
RequiredForReadiness = lazy_load('.services.k8s', 'required_for_readiness')
