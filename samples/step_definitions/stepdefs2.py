from framework.core.runner.GWTDecorator import stepdef


@stepdef("my sample step definition3")
def my_sample_step_definition3(step, context=None):
    print('Step is:', str(step.name))
    print('Context is:', str(context))
    print('Test data passed is ', str(step.test_data))
    context['var3'] = 3


@stepdef("my sample step definition4")
def my_sample_step_definition4(step, context=None):
    print('Step is:', str(step.name))
    print('Context is:', str(context))
    print('Test data passed is ', str(step.test_data))
    context['var4'] = 4
