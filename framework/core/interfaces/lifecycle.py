import abc

from framework.core.models.generic import Context


class DependencyInjector(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def register(self, name: str, value: object) -> object:
        raise NotImplementedError

    @abc.abstractmethod
    def inject(self, *list_of_objects) -> bool:
        raise NotImplementedError


class EventListener(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def run_started(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_started(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_started(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_started(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def step_completed(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def scenario_completed(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def feature_completed(self, event_context: Context):
        raise NotImplementedError

    @abc.abstractmethod
    def run_completed(self, event_context: Context):
        raise NotImplementedError
