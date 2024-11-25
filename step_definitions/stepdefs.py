import random

from framework.core.plugins.kriya import Given, step
from framework.core.utils.logger import logger


@Given("my sample step definition1")
def my_sample_step_definition1(context=None):
    logger.info("context is %s", str(context))
    # return {'var1': random.randint(0, 10)}


@step("my sample step definition2")
def my_sample_step_definition2(context=None):
    logger.info("context is %s", str(context))
    return {'var2': random.randint(0, 10)}
