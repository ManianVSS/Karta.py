import os
from pathlib import Path

from karta.parsers.gherkin.parser import GherkinLexer, GherkinParser
from karta.core.utils.logger import logger


def get_test_feature_path(feature_name: str) -> Path:
    current_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    return current_dir.parent / 'resources' / f'{feature_name}.feature'


def test_gherkin_parsing(feature_name: str):
    feature_file_path = get_test_feature_path(feature_name)

    with open(feature_file_path) as f:
        data = f.read()

    lexer = GherkinLexer()
    lexer.test(data)
    lexer.lexer.lineno = 1

    parser = GherkinParser()
    ast = parser.parse(data)
    logger.info("Parsed AST for %s: %s", feature_name, str(ast))
    return ast


def test1():
    return test_gherkin_parsing('test1')


def test2():
    return test_gherkin_parsing('RuleTest')


if __name__ == '__main__':
    test1()
    test2()
