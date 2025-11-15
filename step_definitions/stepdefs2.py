import random

from karta.core.utils.logger import logger
from karta.plugins.dependency_injector import Inject
from karta.plugins.kriya import step_def

test_properties = Inject("properties").get()


@step_def("my sample step definition3")
def my_sample_step_definition3(context=None):
    logger.info("context is %s", str(context))
    logger.info("Injected group2 property is " + str(test_properties['group2']))
    return {'var3': random.randint(0, 10)}, True


@step_def("my sample step definition4")
def my_sample_step_definition4(context=None):
    logger.info("context is %s", str(context))
    return {'var4': random.randint(0, 10)}, True, None


@step_def("my condition 1 is met")
def my_sample_step_definition4(context=None):
    logger.info("context is %s", str(context))
    return True


@step_def("my condition 2 is met")
def my_sample_step_definition4(context=None):
    logger.info("context is %s", str(context))
    if not 'my_condition_2_loop_counter' in context.keys():
        if context.step_data:
            if 'sample_value' in context.step_data.keys():
                context.my_condition_2_loop_counter = context.step_data['sample_value']
        else:
            context.my_condition_2_loop_counter = 1

    condition_met = (context.my_condition_2_loop_counter > 0)
    if condition_met:
        context.my_condition_2_loop_counter = context.my_condition_2_loop_counter - 1
    else:
        context.pop('my_condition_2_loop_counter', None)
    return condition_met
