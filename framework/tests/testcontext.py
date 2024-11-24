from framework.core.models.generic import Context


def test():
    my_context = Context()

    my_context.update({
        "name": "value",
        "age": 2,
        "colors": ["red", "green", "blue"]
    })

    my_context.dynamic_key_as_attr = "DynamicValue"

    my_context.new_key = my_context.dynamic_key_as_attr + ' updated'
    print(str(my_context))

    for key in my_context.keys():
        print(str(key), '=', str(my_context[key]))

    try:
        print(my_context.unknown_key_error)
    except AttributeError:
        print("Got error for unknown attribute as expected")


if __name__ == '__main__':
    test()
