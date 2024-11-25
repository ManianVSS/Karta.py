import random

from framework.core.plugins.kriya import step_def
from framework.core.utils.logger import logger


@step_def("my sample step definition3")
def my_sample_step_definition3(context=None):
    logger.info("context is %s", str(context))
    return {'var3': random.randint(0, 10)}, True


@step_def("my sample step definition4")
def my_sample_step_definition4(context=None):
    logger.info("context is %s", str(context))
    return {'var4': random.randint(0, 10)}, True, None
