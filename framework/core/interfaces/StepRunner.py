import abc

from framework.core.models.TestStep import TestStep


class StepRunner(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_steps(self):
        raise NotImplementedError

    @abc.abstractmethod
    def run_step(self, step: TestStep, context: dict):
        raise NotImplementedError
