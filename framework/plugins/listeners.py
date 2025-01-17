import json

from framework.core.interfaces.lifecycle import TestEventListener, TestLifecycleHook
from framework.core.models.generic import Context
from framework.core.utils.logger import logger


class LoggingTestLifecycleHook(TestLifecycleHook):
    def __init__(self):
        super().__init__()

    def run_start(self, context: Context):
        logger.info("run started: %s", str(context.run.name))

    def feature_start(self, context: Context):
        logger.info("feature started: %s", str(context.feature.name))

    def scenario_start(self, context: Context):
        logger.info("scenario started: %s", str(context.scenario.name))

    def step_start(self, context: Context):
        logger.info("step started: %s", str(context.step.name))

    def step_complete(self, context: Context):
        logger.info("step complete: %s", str(context.step.name))

    def scenario_complete(self, context: Context):
        logger.info("scenario complete: %s", str(context.scenario.name))

    def feature_complete(self, context: Context):
        logger.info("feature complete: %s", str(context.feature.name))

    def run_complete(self, context: Context):
        logger.info("run complete: %s", str(context.run.name))


class DumpToJSONEventListener(TestEventListener):
    def __init__(self, json_file_name='results/events.json'):
        super().__init__()
        self.json_file_name = json_file_name
        self.event_data = []

    def run_started(self, event_context: Context):
        self.event_data.clear()
        self.event_data.append(event_context)

    def feature_started(self, event_context: Context):
        self.event_data.append(event_context)

    def scenario_started(self, event_context: Context):
        self.event_data.append(event_context)

    def step_started(self, event_context: Context):
        self.event_data.append(event_context)

    def step_completed(self, event_context: Context):
        self.event_data.append(event_context)

    def scenario_completed(self, event_context: Context):
        self.event_data.append(event_context)

    def feature_completed(self, event_context: Context):
        self.event_data.append(event_context)

    def run_completed(self, event_context: Context):
        self.event_data.append(event_context)
        with open(self.json_file_name, 'w', encoding='utf-8') as json_file:
            # noinspection PyTypeChecker
            json.dump(self.event_data, json_file, ensure_ascii=False, indent=4)
        self.event_data.clear()
