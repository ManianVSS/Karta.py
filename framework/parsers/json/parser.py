from ply.lex import lex, TOKEN
from ply.yacc import yacc

from framework.core.utils.funcutils import wrap_function_before
from framework.core.utils.logger import logger


def unescape(string):
    escape_map = {
        "\\n": "\n",
        "\\r": "\r",
        "\\b": "\b",
        "\\t": "\t",
        "\\|": "|",
        "\\\"": "\"",
        "\\\'": "\'",
    }
    string = str(string).strip()
    for unescape_key in escape_map.keys():
        string = string.replace(unescape_key, escape_map[unescape_key])
    return string

# --- Tokenizer

# noinspection PyPep8Naming,PyMethodMayBeStatic,PyTypeChecker
class JSONLexer(object):
    # All tokens must be named in advance.
    tokens = (
        "STRING",
        "NUMBER",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COMMA",
        "COLON",
        "BOOLEAN",
        "NULL"
    )

    # brackets regex
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'

    # commas used to separate items in both objects and arrays
    t_COMMA = r','

    # colon used in objects to define key: value pairs
    t_COLON = r':'

    # string - escaped chars and all but Unicode control characters
    @TOKEN(r'"(\\[bfrnt"/\\]|[^\u0022\u005C\u0000-\u001F\u007F-\u009F]|\\u[0-9a-fA-F]{4})*"')
    def t_STRING(self, t):
        t.value = unescape(t.value[1:-1])
        return t

    @TOKEN(r'(-?)(0|[1-9][0-9]*)(\.[0-9]*)?([eE][+\-]?[0-9]*)?')
    def t_NUMBER(self, t):
        if any(x in t.value for x in ['.', 'e', 'E']):
            t.value = float(t.value)
        else:
            t.value = int(t.value)
        return t

    @TOKEN(r'(true|false)')
    def t_BOOLEAN(self, t):
        t.value = (t.value == 'true')
        return t

    @TOKEN(r'(null)')
    def t_NULL(self, t):
        t.value = None
        return t

    # Ignored token with an action associated with it
    @TOKEN(r'[\s]+')
    def t_ignore_newline(self, t):
        t.lexer.lineno += t.value.count('\n')
        pass

    @TOKEN(r'(\s+)?\#[^\n]*')
    def t_ignore_COMMENT(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value

    # Error handler for illegal characters
    def t_error(self, t):
        t.lexer.skip(1)
        raise SyntaxError(f'Illegal character {t.value[0]!r}')

        # Build the lexer

    def before_input_function(self):
        self.lexer.lineno = 1

    def __init__(self, **kwargs):
        self.lexer = lex(module=self, **kwargs)
        self.lexer.input = wrap_function_before(self.lexer.input, before_function=self.before_input_function)

        # Test it output

    def test(self, input_str):
        self.lexer.input(input_str)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            logger.info(tok)


# --- Parser
# noinspection PyPep8Naming,PyMethodMayBeStatic
class JSONParser(object):
    tokens = JSONLexer.tokens
    conjunctions = ['Given', 'When', 'Then', 'But', 'And']

    def p_json(self, p):
        """
        json : object
             | array
        """
        p[0] = p[1]

    def p_object(self, p):
        """
        object : LBRACE pairs RBRACE
        """
        p[0] = p[2]

    def p_pairs(self, p):
        """
        pairs : pair
              | empty
        """
        if p.slice[1].type == 'pair':
            p[0] = p[1]
        else:
            p[0] = {}

    def p_pair(self, p):
        """
        pair : STRING COLON value COMMA pair
             | STRING COLON value
        """
        p[0] = {p[1]: p[3]}
        if len(p) > 4:
            p[0].update(p[5])

    def p_array(self, p):
        """
        array : LBRACKET items RBRACKET
        """
        p[0] = p[2]

    def p_items(self, p):
        """
        items : item
              | empty
        """
        if p.slice[1].type == 'item':
            p[0] = p[1]
        else:
            p[0] = []

    def p_item(self, p):
        """
        item : value COMMA item
             | value
        """
        p[0] = [p[1]]
        if len(p) > 2:
            p[0].extend(p[3])

    def p_value(self, p):
        """
        value : NUMBER
              | STRING
              | BOOLEAN
              | NULL
              | object
              | array
        """
        p[0] = p[1]

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None
        return

    def p_error(self, p):
        logger.error(f'Syntax error at {p!r}')
        raise SyntaxError(f'Syntax error at {p!r}')

    def __init__(self, lexer=JSONLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self, )

    def parse(self, source):
        return self.parser.parse(source)


if __name__ == '__main__':
    data = r'''# Comment line 1
    {
        "key1": "value1\n\t", # Comment line 2
        "key2": 2.0,
        "key3": false,
        # Comment line 3 "ignoredKey": "Should not appear in AST",
        "key4": [1, 2.0,"abc"],
            # Comment line 4
        "key5": { "a": 1, "b": "valueb"}
    }      # Comment line 5
    '''

    # # Give the lexer some input
    # # Build the lexer object
    json_lexer = JSONLexer()
    json_lexer.test(data)
    json_lexer.lexer.lineno = 1

    # Build the parser
    json_parser = JSONParser()

    # Parse an expression
    ast = json_parser.parse(data)
    logger.info(ast)
