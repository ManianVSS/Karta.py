import abc

from karta.core.interfaces.test_interfaces import Plugin
from karta.core.models.generic import Context


class DependencyInjector(Plugin):
    @abc.abstractmethod
    def register(self, name: str, value: object) -> object:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, *list_of_objects) -> bool:
        raise NotImplementedError


class TestLifecycleHook(Plugin):
    """
        TestLifecycleHooks are called synchronously in the different phases of test lifecycle
    """

    @abc.abstractmethod
    def run_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_iteration_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_iteration_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def run_complete(self, context: Context):
        raise NotImplementedError


class TestEventListener(Plugin):
    """
        TestEventListeners are notified of test events asynchronously after occurrence.
        This can be used to create report generators.
    """

    @abc.abstractmethod
    def run_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_iteration_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_start(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_iteration_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_complete(self, context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def run_complete(self, context: Context):
        raise NotImplementedError
