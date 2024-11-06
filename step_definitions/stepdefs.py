from framework.core.runner.GWTDecorator import step_def, Given, step


@Given("my sample step definition1")
def my_sample_step_definition1(context=None):
    print('Step is:', str(context.step_name))
    print('Context is:', str(context))
    print('Test data passed is ', str(context.step_data))
    context['var1'] = 1


@step("my sample step definition2")
def my_sample_step_definition2(context=None):
    print('Step is:', str(context.step_name))
    print('Context is:', str(context))
    print('Test data passed is ', str(context.step_data))
    context['var2'] = 2
