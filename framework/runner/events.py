import queue
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

from framework.core.interfaces.lifecycle import TestLifecycleHook, TestEventListener
from framework.core.models.generic import Context
from framework.core.models.test_catalog import TestFeature, TestScenario, TestStep
from framework.core.models.test_execution import Run, StepResult, ScenarioResult, FeatureResult, RunResult


class EventProcessor:
    test_lifecycle_hooks: list[TestLifecycleHook] = []
    test_event_listeners: list[TestEventListener] = []

    number_of_threads: int = 1
    event_listener_thread_pool_executor: ThreadPoolExecutor = None

    def __init__(self, test_lifecycle_hooks=None, test_event_listeners=None, number_of_threads=1):
        super().__init__()
        if test_event_listeners is None:
            test_event_listeners = []
        if test_lifecycle_hooks is None:
            test_lifecycle_hooks = []

        self.test_lifecycle_hooks = test_lifecycle_hooks
        self.test_event_listeners = test_event_listeners

        self.event_queue = queue.Queue
        self.number_of_threads = number_of_threads

    def __enter__(self):
        self.event_listener_thread_pool_executor = ThreadPoolExecutor(max_workers=self.number_of_threads)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.event_listener_thread_pool_executor:
            self.event_listener_thread_pool_executor.shutdown(wait=True, cancel_futures=False)

    def start(self):
        self.__enter__()

    def stop(self):
        self.__exit__(None, None, None)

    def run_start(self, run: Run):
        context = Context()
        context.time = datetime.now()
        context.run = run

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.run_start, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.run_start(context)

    def feature_start(self, run: Run, feature: TestFeature):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_start, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_start(context)

    def feature_iteration_start(self, run: Run, feature: TestFeature, iteration_index: int,
                                scenarios: list[TestScenario]):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.iteration_index = iteration_index
        context.scenarios = scenarios

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_iteration_start, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_iteration_start(context)

    def scenario_start(self, run: Run, feature: TestFeature, scenario: TestScenario):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.scenario = scenario

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.scenario_start, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.scenario_start(context)

    def step_start(self, run: Run, feature: TestFeature, scenario: TestScenario, step: TestStep):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.scenario = scenario
        context.step = step

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.step_start, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.step_start(context)

    def step_complete(self, run: Run, feature: TestFeature, scenario: TestScenario, step: TestStep, result: StepResult):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.scenario = scenario
        context.step = step
        context.result = result

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.step_complete, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.step_complete(context)

    def scenario_complete(self, run: Run, feature: TestFeature, scenario: TestScenario, result: ScenarioResult):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.scenario = scenario
        context.result = result

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.scenario_complete, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.scenario_complete(context)

    def feature_iteration_complete(self, run: Run, feature: TestFeature, iteration_index: int,
                                   result: list[ScenarioResult]):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.iteration_index = iteration_index
        context.result = result

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_iteration_complete, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_iteration_complete(context)

    def feature_complete(self, run: Run, feature: TestFeature, result: FeatureResult):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.feature = feature
        context.result = result

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_complete, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_complete(context)

    def run_complete(self, run: Run, result: RunResult):
        context = Context()
        context.time = datetime.now()
        context.run = run
        context.result = result

        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.run_complete, context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.run_complete(context)
