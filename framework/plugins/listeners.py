import json

from pydantic.v1.json import pydantic_encoder

from framework.core.interfaces.lifecycle import TestEventListener, TestLifecycleHook, Event, RunStartEvent, \
    FeatureStartEvent, ScenarioStartEvent, StepStartEvent, StepCompleteEvent, ScenarioCompleteEvent, \
    FeatureCompleteEvent, RunCompleteEvent
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
    def __init__(self, json_file_name='logs/events.json'):
        super().__init__()
        self.json_file_name = json_file_name
        self.event_data = []

    def process_event(self, event: Event):
        if isinstance(event, RunStartEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'tags': event.run.tags,
                }
            )
        elif isinstance(event, FeatureStartEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                }
            )
        elif isinstance(event, ScenarioStartEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                    'sceanario': event.scenario.name,
                }
            )
        elif isinstance(event, StepStartEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                    'sceanario': event.scenario.name,
                    'step': event.step.name,
                }
            )
        elif isinstance(event, StepCompleteEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                    'sceanario': event.scenario.name,
                    'step': event.step.name,
                    'result': event.result.model_dump(),
                }
            )
        elif isinstance(event, ScenarioCompleteEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                    'sceanario': event.scenario.name,
                    'result': event.result.model_dump(),
                }
            )
        elif isinstance(event, FeatureCompleteEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'feature': event.feature.name,
                    'result': event.result.model_dump(),
                }
            )
        elif isinstance(event, RunCompleteEvent):
            self.event_data.append(
                {
                    'type': event.__class__.__name__,
                    'run': event.run.name,
                    'result': event.result.model_dump(),
                }
            )
            with open(self.json_file_name, 'w', encoding='utf-8') as json_file:
                # noinspection PyTypeChecker
                json_file.write(json.dumps(self.event_data, default=pydantic_encoder))
            self.event_data.clear()
        else:
            self.event_data.append(event)
