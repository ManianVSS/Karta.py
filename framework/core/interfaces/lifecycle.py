import abc

from framework.core.models.generic import Context


class DependencyInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register(self, name: str, value: object) -> object:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, *list_of_objects) -> bool:
        raise NotImplementedError


class TestLifecycleHook(metaclass=abc.ABCMeta):
    """
        TestLifecycleHooks are called synchronously in the different phases of test lifecycle
    """

    @abc.abstractmethod
    def run_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_start(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_complete(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def run_complete(self, context: dict):
        raise NotImplementedError


class TestEventListener(metaclass=abc.ABCMeta):
    """
        TestEventListeners are notified of test events asynchronously after occurrence.
        This can be used to create report generators.
    """

    @abc.abstractmethod
    def run_started(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_started(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_started(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_started(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def step_completed(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_completed(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_completed(self, context: dict):
        raise NotImplementedError

    @abc.abstractmethod
    def run_completed(self, context: dict):
        raise NotImplementedError
