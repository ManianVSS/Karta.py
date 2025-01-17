import queue
from datetime import datetime

from pydantic import BaseModel

from framework.core.interfaces.lifecycle import TestLifecycleHook, TestEventListener
from framework.core.models.generic import Context


class Event(BaseModel):
    time: datetime


class RunEvent(BaseModel):
    pass


class EventManager:
    test_lifecycle_hooks: list[TestLifecycleHook] = []
    test_event_listeners: list[TestEventListener] = []

    def __init__(self, test_lifecycle_hooks=None,
                 test_event_listeners=None):
        super().__init__()
        if test_event_listeners is None:
            test_event_listeners = []
        if test_lifecycle_hooks is None:
            test_lifecycle_hooks = []

        self.test_lifecycle_hooks = test_lifecycle_hooks
        self.test_event_listeners = test_event_listeners

        self.event_queue = queue.Queue

    def run_start(self, run):
        context = Context()
        context.time = datetime.now()
        context.run = run

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.run_start(context)

    def feature_start(self, feature):
        context = Context()
        context.time = datetime.now()
        context.feature = feature

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.feature_start(context)

    def sceanrio_start(self, sceanrio):
        context = Context()
        context.time = datetime.now()
        context.scenario = sceanrio

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.scenario_start(context)

    def step_start(self, step):
        context = Context()
        context.time = datetime.now()
        context.step = step

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.step_start(context)

    def step_complete(self, step):
        context = Context()
        context.time = datetime.now()
        context.step = step

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.step_complete(context)

    def scenario_complete(self, sceanrio):
        context = Context()
        context.time = datetime.now()
        context.scenario = sceanrio

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.scenario_complete(context)

    def feature_complete(self, feature):
        context = Context()
        context.time = datetime.now()
        context.feature = feature

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.feature_complete(context)

    def run_complete(self, run):
        context = Context()
        context.time = datetime.now()
        context.run = run

        for test_lifecycle_hook in self.test_lifecycle_hooks:
            test_lifecycle_hook.run_complete(context)
