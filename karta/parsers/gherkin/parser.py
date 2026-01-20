import re
from copy import deepcopy

from ply.lex import lex, TOKEN
from ply.yacc import yacc

from karta.core.models.test_catalog import TestFeature, TestScenario, TestStep
from karta.core.utils.funcutils import wrap_function_before
from karta.core.utils.logger import logger


# --- Tokenizer

# noinspection PyPep8Naming,PyMethodMayBeStatic,PyTypeChecker
class GherkinLexer(object):
    # All tokens must be named in advance.
    tokens = (
        'FEATURE', 'DESCRIPTION_LINE', 'BACKGROUND', 'RULE', 'SCENARIO', 'STEP', 'DOC_STRING', 'TABLE',
        'SCENARIO_OUTLINE', 'EXAMPLES', 'TAG')

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

    @TOKEN(r'(\s+)?Rule:([ \t]+)?[^\n]+')
    def t_RULE(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Rule:')
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

    # @TOKEN(r'(\s+)? ("""(.|\n)*""")|(```(.|\n)*```)')
    @TOKEN(r'("""[\s\S]*?""")|(\'\'\'[\s\S]*?\'\'\')|(```[\s\S]*?```)')
    def t_DOC_STRING(self, t):
        t.lexer.lineno += t.value.count('\n')
        doc_string: str = t.value.strip()
        # TODO: Support docstring type annotation markdown and other types
        if doc_string.startswith(r'"""'):
            doc_string = doc_string.removeprefix(r'"""').removesuffix(r'"""').strip()
        if doc_string.startswith(r'```'):
            doc_string = doc_string.removeprefix(r'```').removesuffix(r'```').strip()
        if doc_string.startswith(r"'''"):
            doc_string = doc_string.removeprefix(r"'''").removesuffix(r"'''").strip()

        doc_string_lines = doc_string.splitlines()
        t.value = ""
        for i in range(len(doc_string_lines)):
            doc_string_lines[i] = doc_string_lines[i].lstrip()
        t.value = '\n'.join(doc_string_lines)
        return t

    def unescape(self, string):
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

    @TOKEN(r'(((\s+)?\|.*\|(\s+)?)\n?)+')
    def t_TABLE(self, t):
        t.lexer.lineno += t.value.count('\n')
        table = str(t.value).strip()
        table_lines = str(table).splitlines()
        t.value = []
        for table_line in table_lines:
            columns = re.findall(r'(?<=\|)(?:\\\||\\n|\\t|[\w\s])*?(?=\|)', table_line.strip())
            t.value.append([self.unescape(column) for column in columns if column != '|'])
        return t

    @TOKEN(r'(\s+)?[^\n]+')
    def t_DESCRIPTION_LINE(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

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
class GherkinParser(object):
    tokens = GherkinLexer.tokens
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
        description : DESCRIPTION_LINE
                    | DESCRIPTION_LINE description
        """
        p[0] = p[1]
        if len(p) > 2:
            p[0] = p[0] + '\n' + p[2]

    def p_empty(self, p):
        """empty :"""
        pass

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
                   | BACKGROUND description steps
        """
        description = None
        if p.slice[2].type == 'description':
            description = p[2]
            del p.slice[2]

        # Nothing can be done with description for now

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
                 | tags SCENARIO description steps
                 | tags SCENARIO_OUTLINE steps EXAMPLES TABLE
                 | tags SCENARIO_OUTLINE description steps EXAMPLES TABLE
        """
        tags = []
        if p.slice[1].type == 'tags':
            tags = p[1]
            del p.slice[1]

        description = None
        if p.slice[2].type == 'description':
            description = p[2]
            del p.slice[2]

        if p.slice[1].type == 'SCENARIO':
            p[0] = TestScenario(name=p[1].strip(), description=description, steps=p[2], tags=tags, )
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
                scenario = TestScenario(name=p[1].strip(), description=description, steps=scenario_steps, tags=tags, )
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
             | STEP DOC_STRING
             | STEP DOC_STRING TABLE
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
        table = None
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

        p[0] = TestStep(conjunction=step_conjunction, name=name, text=doc_string,
                        data={'table_data': table_data} if (table_data and len(table_data) > 0) else {}, )
        p[0].line_number = p.slice[1].lineno

    def p_error(self, p):
        logger.error(f'Syntax error at {p!r}')

    def __init__(self, lexer=GherkinLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self, )

    def parse(self, source):
        return self.parser.parse(source)
