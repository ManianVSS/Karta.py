from karta.core.models.generic import Context


def replace_variables_from_dict(string_to_process, variable_dictionary, variable_prefix='${', variable_suffix='}'):
    replaced_string = string_to_process

    for variable, value in variable_dictionary.items():
        replaced_string = replaced_string.replace(variable_prefix + variable + variable_suffix, str(value))

    return replaced_string


def replace_variables(string_to_process, context: Context, step_data, environment_dictionary):
    replaced_string = string_to_process

    # Replacement in the priority order
    replaced_string = context.replace_variables_from_dict(replaced_string)
    replaced_string = replace_variables_from_dict(replaced_string, step_data, )
    replaced_string = replace_variables_from_dict(replaced_string, environment_dictionary, )

    return replaced_string


def replace_variables_in_str_array(string_array, context, step_data, environment_dictionary):
    return [replace_variables(string_item, context, step_data, environment_dictionary) for string_item in string_array]
