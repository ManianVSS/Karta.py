from framework.core.models.TestStep import TestStep


class TestScenario:
    def __init__(self, name=None, steps=None):
        self.name = name
        self.steps = []
        for step in steps:
            self.steps.append(TestStep(**step))
