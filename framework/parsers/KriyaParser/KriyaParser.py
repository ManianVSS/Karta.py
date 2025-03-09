import re
from copy import deepcopy

from ply.lex import lex, TOKEN
from ply.yacc import yacc

from framework.core.models.test_catalog import TestFeature, TestScenario, TestStep
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
class KriyaLexer(object):
    # All tokens must be named in advance.
    tokens = (
        'FEATURE',
        # 'DESCRIPTION_LINE',
        'BACKGROUND',
        'SCENARIO',
        'STEP',
        'DOC_STRING',
        'TABLE',
        'SCENARIO_OUTLINE',
        'EXAMPLES',
        'TAG',

        'ASSERTION',
        'CONDITION',
        'LOOP',

        "IDENTIFIER",
        "STRING",
        "NUMBER",
        "LBRACE",
        "RBRACE",
        "LBRACKET",
        "RBRACKET",
        "COMMA",
        "COLON",
        "BOOLEAN",
        "NULL",
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

    t_IDENTIFIER = r'[_a-zA-Z][_a-zA-Z0-9]*'

    # Ignored token with an action associated with it
    @TOKEN(r'[\s]+')
    def t_ignore_newline(self, t):
        t.lexer.lineno += t.value.count('\n')
        pass

    @TOKEN(r'(\s+)?\#[^\n]*')
    def t_ignore_COMMENT(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value

    @TOKEN(r'(\s+)?\@[^\n@]*')
    def t_TAG(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('@').strip()
        return t

    @TOKEN(r'(\s+)?Feature:([ \t]+)?[^\n]+')
    def t_FEATURE(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Feature:')
        return t

    @TOKEN(r'(\s+)?Background:')
    def t_BACKGROUND(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(Scenario|Example):([ \t]+)?[^\n]+')
    def t_SCENARIO(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        if t.value.startswith('Scenario:'):
            t.value = t.value.removeprefix('Scenario:')
        if t.value.startswith('Example:'):
            t.value = t.value.removeprefix('Example:')
        return t

    @TOKEN(r'(\s+)?Scenario[ ]Outline:([ \t]+)?[^\n]+')
    def t_SCENARIO_OUTLINE(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        t.value = t.value.removeprefix('Scenario Outline:')
        return t

    @TOKEN(r'(\s+)?Examples:')
    def t_EXAMPLES(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(Given | When | Then | And | But)([ \t]+)?[^\n]+')
    def t_STEP(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(Verify | Validate)([ \t]+)?[^\n]+')
    def t_ASSERTION(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(If | Condition:)([ \t]+)?[^\n]+')
    def t_CONDITION(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(While | Until)([ \t]+)?[^\n]+')
    def t_LOOP(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'("""(.|\n|\s)+?(?=""")""")|(```(.|\n|\s)+?(?=```)```)')
    def t_DOC_STRING(self, t):
        t.lexer.lineno += t.value.count('\n')
        doc_string = t.value.strip()
        # TODO: Support docstring type annotation markdown and other types
        if doc_string.startswith(r'"""'):
            doc_string = doc_string.removeprefix(r'"""').removesuffix(r'"""').strip()
        if doc_string.startswith(r'```'):
            doc_string = doc_string.removeprefix(r'```').removesuffix(r'```').strip()

        doc_string_lines = doc_string.splitlines()
        t.value = ""
        for i in range(len(doc_string_lines)):
            doc_string_lines[i] = doc_string_lines[i].lstrip()
        t.value = '\n'.join(doc_string_lines)
        return t

    @TOKEN(r'(((\s+)?\|.*\|(\s+)?)\n?)+')
    def t_TABLE(self, t):
        t.lexer.lineno += t.value.count('\n')
        table = str(t.value).strip()
        table_lines = str(table).splitlines()
        t.value = []
        for table_line in table_lines:
            columns = re.findall(r'(?<=\|)(?:\\\||\\n|\\t|[\w\s])*?(?=\|)', table_line.strip())
            t.value.append([unescape(column) for column in columns if column != '|'])

        return t

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

    # @TOKEN(r'(\s+)?[^\"\{\}\:\\[\],\n]+')
    # def t_DESCRIPTION_LINE(self, t):
    #     # t.lexer.lineno += t.value.count('\n')
    #     t.value = t.value.strip()
    #     return t

    # Error handler for illegal characters
    def t_error(self, t):
        logger.error(f'Illegal character {t.value[0]!r}')
        t.lexer.skip(1)

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
class KriyaParser(object):
    tokens = KriyaLexer.tokens
    conjunctions = ['Given', 'When', 'Then', 'But', 'And']

    # Write functions for each grammar rule which is
    # specified in the docstring.
    def p_feature(self, p):
        """
        feature : tags FEATURE scenarios
                | tags FEATURE description scenarios
                | tags FEATURE background scenarios
                | tags FEATURE description background scenarios
        """
        tags = []
        if p.slice[1].type == 'tags':
            tags = p[1]
            del p.slice[1]

        description = None
        if p.slice[2].type == 'description':
            description = p[2]
            del p.slice[2]

        background_steps = []
        if p.slice[2].type == 'background':
            background_steps = [*p[2]]
            del p.slice[2]

        p[0] = TestFeature(name=p[1].strip(), description=description, setup_steps=background_steps, scenarios=p[2],
                           tags=tags, )
        p[0].line_number = p.slice[1].lineno

    def p_description(self, p):
        """
        description : DOC_STRING
                    | DOC_STRING description
        """
        p[0] = p[1]
        if len(p) > 2:
            p[0] = p[0] + '\n' + p[2]

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None
        return

    def p_tags(self, p):
        """
        tags : TAG tags
             | empty
        """
        p[0] = [p[1]] if p[1] else []
        if len(p) > 2:
            p[0].extend([*p[2]])

    def p_background(self, p):
        """
        background : BACKGROUND steps
        """
        p[0] = [*p[2]]

    def p_scenarios(self, p):
        """
        scenarios : scenario
                  | scenario scenarios
        """
        p[0] = [p[1]]
        if len(p) > 2:
            for item in p[2]:
                if isinstance(item, TestScenario):
                    p[0].append(item)
                else:
                    p[0].extend(item)

    def p_scenario(self, p):
        """
        scenario : tags SCENARIO steps
                 | tags SCENARIO_OUTLINE steps EXAMPLES TABLE
        """
        tags = []
        if p.slice[1].type == 'tags':
            tags = p[1]
            del p.slice[1]

        if p.slice[1].type == 'SCENARIO':
            p[0] = TestScenario(name=p[1].strip(), steps=p[2], tags=tags, )
            p[0].line_number = p.slice[1].lineno
        else:
            table = p[4]
            table_data = []

            if not table or len(table) < 2:
                raise Exception("At least one example data row needs to be provided.")

            scenarios = []
            template_steps = p[2]
            for i in range(1, len(table)):
                table_data.append({})
                scenario_steps = []
                for template_step in template_steps:
                    scenario_step = deepcopy(template_step)
                    for j in range(len(table[i])):
                        table_data[i - 1][table[0][j]] = table[i][j]
                        scenario_step.name = scenario_step.name.replace("<" + table[0][j] + ">", table[i][j])
                    scenario_steps.append(scenario_step)
                scenario = TestScenario(name=p[1].strip(), steps=scenario_steps, tags=tags, )
                scenario.line_number = p.slice[1].lineno
                scenarios.append(scenario)

            p[0] = scenarios

    def p_steps(self, p):
        """
        steps : step
              | step steps
        """
        p[0] = [p[1]]
        if len(p) > 2:
            for item in p[2]:
                p[0].append(item)

    def p_step(self, p):
        """
        step : STEP
             | STEP TABLE
             | STEP object
             | STEP DOC_STRING
             | STEP DOC_STRING TABLE
             | STEP DOC_STRING object
        """
        name = p[1]
        step_conjunction = None
        for conjunction in self.conjunctions:
            if name.startswith(conjunction):
                step_conjunction, name = (conjunction, name.removeprefix(conjunction).strip())
        doc_string = None
        if len(p) > 2:
            if p.slice[2].type == 'DOC_STRING':
                doc_string = p[2]
                del p.slice[2]

        step_data = {}
        if len(p) > 2:
            if p.slice[2].type == 'TABLE':
                table = p[2]
                del p.slice[2]
                table_data = []
                if table and len(table) > 1:
                    for i in range(1, len(table)):
                        table_data.append({})
                        for j in range(len(table[i])):
                            table_data[i - 1][table[0][j]] = table[i][j]
                    step_data['table_data'] = table_data
            elif p.slice[2].type == 'object':
                step_data = p[2]
                del p.slice[2]

        p[0] = TestStep(conjunction=step_conjunction, name=name, text=doc_string,
                        data=step_data, )
        p[0].line_number = p.slice[1].lineno

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
             | IDENTIFIER COLON value COMMA pair
             | IDENTIFIER COLON value
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

    def p_error(self, p):
        logger.error(f'Syntax error at {p!r}')

    def __init__(self, lexer=KriyaLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self, )

    def parse(self, source):
        return self.parser.parse(source)


if __name__ == '__main__':
    data = r'''
     # fComment 2
     @MyTag1 @MyTag2
     @MyTag3
    Feature: My feature
        # Comment before description
        """
        This feature description describes the feature.
        It is a multi line feature description.
        """
        
         # Comment for Background ## Background:
        Background:
            Given background step1
            And background step2
            ```
            Background step2?
            ===============
            This is the text block for background step2.
            Which could span multiple lines.
            ```
            And background step3
            | f1\|  |  f2\n |  f3\t |
            | v11   |  v12  |  v13  |
            | v21   |  v 22  |  v23  |
            
        # Comment 1
      Example: My Scenario 1
        
        Given scenario 1 step 1
        """
        Scenario 1 step1?
        ===============
        This is the text block for Scenario 1 step1.
        Which could span multiple lines.
        """
        When scenario 1 step 2
          # sComment 1
        Then scenario 1 step 3
        {
                "\"key\":\n\t 3": 1,
                key2: true,
                key3: "\"string value\"\n\t",
                key4: 10.3,
                key5: ["this", "is","an","array","with", 7, "values"],
                key6: {type:"Object value"}
        }
        
    # Comment 2
    @SMyTag1 @SMyTag2
     @SMyTag3
      Scenario: My Scenario 2
        Given scenario 2 step 1
        When scenario 2 step 2
          # sComment 1
        Then scenario 2 step 3
        And scenario 2 step 4
        But scenario 2 step 5
        
    # Comment 3
    @SoMyTag1 @SoMyTag2
     @SoMyTag3
      Scenario Outline: My Scenario outline
        Given <var1> scenario outline step 1
        When scenario outline  step 2
          # sComment 1
        Then scenario outline  step 3
        And <var2> scenario outline  step 4
        But <var3> scenario outline  step 5
        
        Examples:
        |var1   | var2  | var3       |
        |value11 | value12 | value13 |
        |value21 | value22 | value23 | 
    '''

    # # Give the lexer some input
    # # Build the lexer object
    kriya_lexer = KriyaLexer()
    kriya_lexer.test(data)
    kriya_lexer.lexer.lineno = 1

    # Build the parser
    parser = KriyaParser()

    # Parse an expression
    ast = parser.parse(data)
    logger.info(ast)
