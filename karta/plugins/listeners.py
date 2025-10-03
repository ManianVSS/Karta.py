import json

from pydantic.v1.json import pydantic_encoder

from karta.core.interfaces.lifecycle import TestEventListener, TestLifecycleHook
from karta.core.models.generic import Context
from karta.core.utils.logger import logger


class LoggingTestLifecycleHook(TestLifecycleHook):
    def __init__(self):
        super().__init__()

    def run_start(self, context: Context):
        logger.info("run started: %s", str(context.run_info.run))

    def feature_start(self, context: Context):
        logger.info("feature started: %s", str(context.run_info.feature))

    def feature_iteration_start(self, context: Context):
        logger.info("feature iteration started: %s[%i]", str(context.run_info.feature),
                    int(context.run_info.iteration_index))

    def scenario_start(self, context: Context):
        logger.info("scenario started: %s", str(context.run_info.scenario))

    def step_start(self, context: Context):
        logger.info("step started: %s", str(context.run_info.step))

    def step_complete(self, context: Context):
        logger.info("step complete: %s: %s", str(context.run_info.step), str(context.run_info.result))

    def scenario_complete(self, context: Context):
        logger.info("scenario complete: %s: %s", str(context.run_info.scenario), str(context.run_info.result))

    def feature_iteration_complete(self, context: Context):
        logger.info("feature iteration completed: %s[%i]: %s", str(context.run_info.feature),
                    int(context.run_info.iteration_index), str(context.run_info.result))

    def feature_complete(self, context: Context):
        logger.info("feature complete: %s: %s", str(context.run_info.feature), str(context.run_info.result))

    def run_complete(self, context: Context):
        logger.info("run complete: %s: %s", str(context.run_info.run), str(context.run_info.result))


class DumpToJSONEventListener(TestEventListener):
    def __init__(self, json_file_name='logs/events.json'):
        super().__init__()
        self.json_file_name = json_file_name
        self.event_data = []

    def run_start(self, context: Context):
        self.event_data.append(
            {
                'type': "run_start",
                'run': context.run,
                'tags': context.tags,
            }
        )

    def feature_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_start',
                'run': context.run,
                'feature': context.feature,
            }
        )

    def feature_iteration_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_iteration_start',
                'run': context.run,
                'feature': context.feature,
                'index': context.iteration_index,
                'scenarios': context.scenarios,
            }
        )

    def scenario_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'scenario_start',
                'run': context.run,
                'feature': context.feature,
                'sceanario': context.scenario,
            }
        )

    def step_start(self, context: Context):
        self.event_data.append(
            {
                'type': 'step_start',
                'run': context.run,
                'feature': context.feature,
                'sceanario': context.scenario,
                'step': context.step,
            }
        )

    def step_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'step_complete',
                'run': context.run,
                'feature': context.feature,
                'sceanario': context.scenario,
                'step': context.step,
                'result': context.result.model_dump(),
            }
        )

    def scenario_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'scenario_complete',
                'run': context.run,
                'feature': context.feature,
                'sceanario': context.scenario,
                'result': context.result.model_dump(),
            }
        )

    def feature_iteration_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_iteration_complete',
                'run': context.run,
                'feature': context.feature,
                'index': context.iteration_index,
                'result': [scenario_result.model_dump() for scenario_result in context.result],
            }
        )

    def feature_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'feature_complete',
                'run': context.run,
                'feature': context.feature,
                'result': context.result.model_dump(),
            }
        )

    def run_complete(self, context: Context):
        self.event_data.append(
            {
                'type': 'run_complete',
                'run': context.run,
                'result': context.result.model_dump(),
            }
        )
        with open(self.json_file_name, 'w', encoding='utf-8') as json_file:
            # noinspection PyTypeChecker
            json_file.write(json.dumps(self.event_data, indent=4, default=pydantic_encoder))
        self.event_data.clear()
