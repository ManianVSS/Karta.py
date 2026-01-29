from karta.core.utils.logger import logger
from karta.plugins.dependency_injector import Inject
from karta.plugins.kriya import step_def

test_properties = Inject("properties").get()


@step_def('Regex1 I have "\\d+" cucumbers')
def step_def_regex1(context: dict, n: int):
    logger.info("context is %s", str(context))
    logger.info("There are %s cucumber", str(n))
    return True


@step_def('Regex2 I have "\\d+" apples and "\\d+" oranges')
def step_def_regex1(context: dict, apples: int, oranges: int):
    logger.info("context is %s", str(context))
    logger.info("There are %s apples and %s oranges", str(apples) , str(oranges))
    return True

@step_def("CE1 I have {int} {word} and my message is {string}")
def step_def_ce1(context:dict, n: int, word: str, string: str):
    logger.info("context is %s", str(context))
    logger.info("There are %d %s and the message is \"%s\"",n,word,string )