import re

import yaml

number_regex = r'^(([0-9]*)|(([0-9]*)\.([0-9]*)))$'
array_regex = r'^\[([^,],?)*\]$'


def is_builtin_class_instance(obj):
    return obj.__class__.__module__ in ['__builtin__', 'builtins']


def parse_value(value: str) -> object:
    check_value = value.strip()
    if ((check_value.lower() == 'true') or (check_value.lower() == 'false')
            or re.search(number_regex, check_value) or
            re.search(array_regex, check_value)):
        return yaml.safe_load(value)
    else:
        return value


def get_empty_tuple():
    return tuple()


def get_empty_list():
    return list()


def get_empty_dict():
    return dict()


def merge_lists(*lists_to_merge):
    merged_list = []
    for list_to_merge in lists_to_merge:
        merged_list.extend(list_to_merge)
    return merged_list


def add_missing_items_from_lists(destination_list, *source_lists):
    for source_list in source_lists:
        destination_list.extend([element for element in source_list if element not in destination_list])


def merge_dicts(*dicts_to_merge):
    merged_dict = {}
    for dict_to_merge in dicts_to_merge:
        merged_dict.update(dict_to_merge)
    return merged_dict


def deep_update(dest: dict, source: dict, update_existing_only=False):
    for k in source.keys():
        if k in dest.keys():
            if isinstance(dest[k], dict) and isinstance(source[k], dict):
                deep_update(dest[k], source[k], update_existing_only)
            else:
                dest[k] = source[k]
        else:
            if not update_existing_only:
                dest[k] = source[k]


def in_range(value, min_value, max_value, include_min=True, include_max=True):
    return (((value >= min_value) if include_min else (value > min_value))
            and
            ((value <= max_value) if include_max else (value < max_value)))


def object_to_integer(obj):
    return obj if isinstance(obj, int) else int(obj)


def increment_char(c):
    return chr(ord(c) + 1)


def increment_alphanumerical_string(current_string):
    char_array = list(current_string)

    carry = 1
    for j in range(len(char_array) - 1, -1, -1):
        if carry > 0:
            if in_range(char_array[j], 'a', 'z'):
                if char_array[j] != 'z':
                    char_array[j] = increment_char(char_array[j])
                    carry = 0
                    break
                else:
                    char_array[j] = 'a'
                    carry = 1

            elif in_range(char_array[j], 'A', 'Z'):
                if char_array[j] != 'Z':
                    char_array[j] = increment_char(char_array[j])
                    carry = 0
                    break
                else:
                    char_array[j] = 'A'
                    carry = 1

            elif in_range(char_array[j], '0', '9'):
                if char_array[j] != '9':
                    char_array[j] = increment_char(char_array[j])
                    carry = 0
                    break
                else:
                    char_array[j] = '0'
                    carry = 1

    return str(char_array), carry
