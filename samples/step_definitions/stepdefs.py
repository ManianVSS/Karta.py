from framework.core.runner.GWTDecorator import stepdef


@stepdef("my sample step definition1")
def my_sample_step_definition1(step, context=None):
    print('Step is:', str(step.name))
    print('Context is:', str(context))
    print('Test data passed is ', str(step.test_data))
    context['var1'] = 1


@stepdef("my sample step definition2")
def my_sample_step_definition2(step, context=None):
    print('Step is:', str(step.name))
    print('Context is:', str(context))
    print('Test data passed is ', str(step.test_data))
    context['var2'] = 2
