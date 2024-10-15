from . import step_definition_mapping


def stepdef(step_identifier):
    def inner(func):
        step_identifier_str = str(step_identifier)
        if step_identifier_str not in step_definition_mapping:
            print("registering ", step_identifier_str)
            step_definition_mapping[step_identifier_str] = func

        def wrapper():
            func()

        return wrapper

    return inner
