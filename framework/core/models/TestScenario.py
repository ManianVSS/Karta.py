from framework.core.models.TestStep import TestStep


class TestScenario:
    def __init__(self, name=None, steps=None):
        self.name = name
        self.steps = [TestStep(**step) for step in steps]
