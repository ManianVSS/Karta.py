from . import step_definition_mapping


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in step_definition_mapping:
            print("registering ", step_identifier_str)
            step_definition_mapping[step_identifier_str] = func

        return func

    return register_step_definition


step_definition = step_def
step = step_def
given = step_def
when = step_def
then = step_def

Given = step_def
When = step_def
Then = step_def
