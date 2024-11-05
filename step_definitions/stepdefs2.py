from framework.core.runner.GWTDecorator import step_def


@step_def("my sample step definition3")
def my_sample_step_definition3(context=None):
    print('Step is:', str(context.step_name))
    print('Context is:', str(context))
    print('Test data passed is ', str(context.step_data))
    context['var3'] = 3


@step_def("my sample step definition4")
def my_sample_step_definition4(context=None):
    print('Step is:', str(context.step_name))
    print('Context is:', str(context))
    print('Test data passed is ', str(context.step_data))
    context['var4'] = 4
