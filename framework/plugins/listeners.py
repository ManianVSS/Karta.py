import json

from pydantic.v1.json import pydantic_encoder

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

    def feature_iteration_start(self, context: Context):
        logger.info("feature iteration started: %s[%i]", str(context.feature.name), int(context.iteration_index))

    def scenario_start(self, context: Context):
        logger.info("scenario started: %s", str(context.scenario.name))

    def step_start(self, context: Context):
        logger.info("step started: %s", str(context.step.name))

    def step_complete(self, context: Context):
        logger.info("step complete: %s: %s", str(context.step.name), str(context.result))

    def scenario_complete(self, context: Context):
        logger.info("scenario complete: %s: %s", str(context.scenario.name), str(context.result))

    def feature_iteration_complete(self, context: Context):
        logger.info("feature iteration completed: %s[%i]: %s", str(context.feature.name), int(context.iteration_index),
                    str(context.result))

    def feature_complete(self, context: Context):
        logger.info("feature complete: %s: %s", str(context.feature.name), str(context.result))

    def run_complete(self, context: Context):
        logger.info("run complete: %s: %s", str(context.run.name), str(context.result))


class DumpToJSONEventListener(TestEventListener):
    def __init__(self, json_file_name='logs/events.json'):
        super().__init__()
        self.json_file_name = json_file_name
        self.event_data = []

    def run_start(self, context: Context):
        self.event_data.append(
            {
                'type': "run_start",
                'run': context.run.name,
                'tags': context.run.tags,
            }
        )

    def feature_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_start',
                'run': context.run.name,
                'feature': context.feature.name,
            }
        )

    def feature_iteration_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_iteration_start',
                'run': context.run.name,
                'feature': context.feature.name,
                'index': context.iteration_index,
                'scenarios': [scenario.name for scenario in context.scenarios],
            }
        )

    def scenario_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'scenario_start',
                'run': context.run.name,
                'feature': context.feature.name,
                'sceanario': context.scenario.name,
            }
        )

    def step_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'step_start',
                'run': context.run.name,
                'feature': context.feature.name,
                'sceanario': context.scenario.name,
                'step': context.step.name,
            }
        )

    def step_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'step_complete',
                'run': context.run.name,
                'feature': context.feature.name,
                'sceanario': context.scenario.name,
                'step': context.step.name,
                'result': context.result.model_dump(),
            }
        )

    def scenario_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'scenario_complete',
                'run': context.run.name,
                'feature': context.feature.name,
                'sceanario': context.scenario.name,
                'result': context.result.model_dump(),
            }
        )

    def feature_iteration_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_iteration_complete',
                'run': context.run.name,
                'feature': context.feature.name,
                'index': context.iteration_index,
                'result': [scenario_result.model_dump() for scenario_result in context.result],
            }
        )

    def feature_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_complete',
                'run': context.run.name,
                'feature': context.feature.name,
                'result': context.result.model_dump(),
            }
        )

    def run_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'run_complete',
                'run': context.run.name,
                'result': context.result.model_dump(),
            }
        )
        with open(self.json_file_name, 'w', encoding='utf-8') as json_file:
            # noinspection PyTypeChecker
            json_file.write(json.dumps(self.event_data, indent=4, default=pydantic_encoder))
        self.event_data.clear()
