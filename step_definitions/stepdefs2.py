import random

from framework.core.utils.logger import logger
from framework.plugins.dependency_injector import Inject
from framework.plugins.kriya import step_def

test_properties = Inject("properties")


@step_def("my sample step definition3")
def my_sample_step_definition3(context=None):
    logger.info("context is %s", str(context))
    logger.info("Injected group2 property is " + str(test_properties['group2']))
    return {'var3': random.randint(0, 10)}, True


@step_def("my sample step definition4")
def my_sample_step_definition4(context=None):
    logger.info("context is %s", str(context))
    return {'var4': random.randint(0, 10)}, True, None
