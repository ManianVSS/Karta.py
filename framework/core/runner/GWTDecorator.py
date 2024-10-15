from . import step_definition_mapping


def step_def(step_identifier):
    def register_step_definition(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in step_definition_mapping:
            print("registering ", step_identifier_str)
            step_definition_mapping[step_identifier_str] = func

        return func

    return register_step_definition
