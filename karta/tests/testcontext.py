from karta.core.models.generic import Context
from karta.core.utils.logger import logger


def test():
    my_context = Context()

    my_context.update({
        "name": "value",
        "age": 2,
        "colors": ["red", "green", "blue"]
    })

    my_context.dynamic_key_as_attr = "DynamicValue"

    my_context.new_key = my_context.dynamic_key_as_attr + ' updated'
    logger.info(str(my_context))

    for key in my_context.keys():
        logger.info("%s = %s", str(key), str(my_context[key]))

    try:
        logger.info(my_context.unknown_key_error)
    except AttributeError:
        logger.info("Got error for unknown attribute as expected")


if __name__ == '__main__':
    test()
