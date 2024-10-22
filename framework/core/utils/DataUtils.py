from copy import deepcopy
from os import name


# clone_dict = deepcopy


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

    # return_string = str(char_array)
    # for i in range(carry):
    #     return_string = increment_alphanumerical_string(return_string)

    return str(char_array)


if __name__ == '__main__':
    print(increment_alphanumerical_string('zzz999z'))
