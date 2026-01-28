import queue
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime

from karta.core.interfaces.plugins import TestLifecycleHook, TestEventListener
from karta.core.models.generic import Context
from karta.core.models.test_catalog import Feature, Scenario, Step
from karta.core.models.test_execution import Run, StepResult, ScenarioResult, FeatureResult, RunResult


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

    def run_start(self, run: Run, run_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_context.run_info = run_info

        # Create a separte event context for event listeners to avoid thead safety issues
        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'tags': run.tags,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.run_start, event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.run_start(run_context)

    def feature_start(self, run: Run, feature: Feature, feature_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature
        feature_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature.name,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_start,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_start(feature_context)

    def feature_iteration_start(self, run: Run, feature: Feature, iteration_index: int,
                                scenarios: list[Scenario], feature_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature
        run_info.iteration_index = iteration_index
        run_info.scenarios = scenarios
        feature_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature.name,
            'iteration_index': iteration_index,
            'scenarios': [scenario.name for scenario in scenarios],
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_iteration_start,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_iteration_start(feature_context)

    def scenario_start(self, run: Run, feature_name: str, iteration_index: int, scenario: Scenario,
                       scenario_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature_name
        run_info.iteration_index = iteration_index
        run_info.scenario = scenario
        scenario_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature_name,
            'iteration_index': iteration_index,
            'scenario': scenario.name,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.scenario_start,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.scenario_start(scenario_context)

    def step_start(self, run: Run, feature_name: str, iteration_index: int, scenario_name: str, step: Step,
                   scenario_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature_name
        run_info.iteration_index = iteration_index
        run_info.scenario = scenario_name
        run_info.step = step
        scenario_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature_name,
            'iteration_index': iteration_index,
            'scenario': scenario_name,
            'step': step.identifier,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.step_start,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.step_start(scenario_context)

    def step_complete(self, run: Run, feature_name: str, iteration_index: int, scenario_name: str,
                      step: Step, result: StepResult, scenario_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature_name
        run_info.iteration_index = iteration_index
        run_info.scenario = scenario_name
        run_info.step = step
        run_info['result'] = result
        scenario_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature_name,
            'iteration_index': iteration_index,
            'scenario': scenario_name,
            'step': step.identifier,
            'result': result,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.step_complete,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.step_complete(scenario_context)

    def scenario_complete(self, run: Run, feature_name: str, iteration_index: int, scenario: Scenario,
                          result: ScenarioResult, scenario_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature_name
        run_info.iteration_index = iteration_index
        run_info.scenario = scenario
        run_info.result = result
        scenario_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature_name,
            'iteration_index': iteration_index,
            'scenario': scenario.name,
            'result': result,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.scenario_complete,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.scenario_complete(scenario_context)

    def feature_iteration_complete(self, run: Run, feature: Feature, iteration_index: int,
                                   result: list[ScenarioResult], feature_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature
        run_info.iteration_index = iteration_index
        run_info.result = result
        feature_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature.name,
            'iteration_index': iteration_index,
            'result': result,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_iteration_complete,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_iteration_complete(feature_context)

    def feature_complete(self, run: Run, feature: Feature, result: FeatureResult, feature_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.feature = feature
        run_info.result = result
        feature_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'feature': feature.name,
            'result': result,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.feature_complete,
                                                            event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.feature_complete(feature_context)

    def run_complete(self, run: Run, result: RunResult, run_context: Context):
        run_info = Context()
        run_info.time = datetime.now()
        run_info.run = run
        run_info.result = result
        run_context.run_info = run_info

        event_context = Context({
            'time': run_info.time,
            'run': run.name,
            'result': result,
        })
        for test_event_listener in self.test_event_listeners:
            self.event_listener_thread_pool_executor.submit(test_event_listener.run_complete, event_context)

        for test_lifecycle_hooks in self.test_lifecycle_hooks:
            test_lifecycle_hooks.run_complete(run_context)
