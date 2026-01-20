import os
from pathlib import Path

from karta.parsers.gherkin.parser import GherkinLexer, GherkinParser
from karta.core.utils.logger import logger

if __name__ == '__main__':
    current_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    feature_file_path = current_dir.parent / 'resources' / 'test1.feature'

    with open(feature_file_path) as f:
        data = f.read()

    lexer = GherkinLexer()
    lexer.test(data)
    lexer.lexer.lineno = 1

    parser = GherkinParser()
    ast = parser.parse(data)
    logger.info("Parsed AST: %s", str(ast))
