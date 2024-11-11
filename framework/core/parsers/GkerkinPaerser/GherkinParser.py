from ply.lex import lex, TOKEN
from ply.yacc import yacc

from framework.core.models.TestFeature import TestFeature
from framework.core.models.TestScenario import TestScenario
from framework.core.models.TestStep import TestStep


# --- Tokenizer

# noinspection PyPep8Naming,PyMethodMayBeStatic
class GherkinLexer(object):
    # All tokens must be named in advance.
    tokens = ('FEATURE', 'DESCRIPTION_LINE', 'BACKGROUND', 'SCENARIO', 'STEP', 'DOC_STRING')

    # Ignored token with an action associated with it
    @TOKEN(r'[\s]+')
    def t_ignore_newline(self, t):
        t.lexer.lineno += t.value.count('\n')

    @TOKEN(r'(\s+)?\#[^\n]*')
    def t_ignore_COMMENT(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value

    @TOKEN(r'(\s+)?Feature:([ \t]+)?[^\n]+')
    def t_FEATURE(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Feature:')
        return t

    @TOKEN(r'(\s+)?Background:')
    def t_BACKGROUND(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?(Scenario|Example):([ \t]+)?[^\n]+')
    def t_SCENARIO(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        if t.value.startswith('Scenario:'):
            t.value = t.value.removeprefix('Scenario:')
        if t.value.startswith('Example:'):
            t.value = t.value.removeprefix('Example:')
        return t

    @TOKEN(r'(\s+)?(Given | When | Then | And | But)([ \t]+)?[^\n]+')
    def t_STEP(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)? ("""(.|\n)*""")|(```(.|\n)*```)')
    def t_DOC_STRING(self, t):
        t.lexer.lineno += t.value.count('\n')
        doc_string = t.value.strip()
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

    @TOKEN(r'(\s+)?[^\n]+')
    def t_DESCRIPTION_LINE(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    # Error handler for illegal characters
    def t_error(self, t):
        print(f'Illegal character {t.value[0]!r}')
        t.lexer.skip(1)

        # Build the lexer

    def __init__(self, **kwargs):
        self.lexer = lex(module=self, **kwargs)

        # Test it output

    def test(self, input_str):
        self.lexer.input(input_str)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


# --- Parser
# noinspection PyPep8Naming,PyMethodMayBeStatic
class GherkinParser(object):
    tokens = GherkinLexer.tokens
    conjunctions = ['Given', 'When', 'Then', 'But', 'And']

    # Write functions for each grammar rule which is
    # specified in the docstring.
    def p_feature(self, p):
        """
        feature : FEATURE scenarios
                | FEATURE description scenarios
                | FEATURE background scenarios
                | FEATURE description background scenarios
        """
        description = None
        if p.slice[2].type == 'description':
            description = p[2]
            del p.slice[2]

        background_steps = None
        if p.slice[2].type == 'background':
            background_steps = [*p[2]]
            del p.slice[2]

        p[0] = TestFeature(name=p[1].strip(), description=description, background_steps=background_steps,
                           scenarios=p[2])

    def p_description(self, p):
        """
        description : DESCRIPTION_LINE
                    | DESCRIPTION_LINE description
        """
        p[0] = p[1]
        if len(p) > 2:
            p[0] = p[0] + '\n' + p[2]

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
                p[0].append(item)

    def p_scenario(self, p):
        """
        scenario : SCENARIO steps
        """
        p[0] = TestScenario(name=p[1].strip(), steps=p[2])  # ('scenario', *p[1:])

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
             | STEP DOC_STRING
        """
        name = p[1]
        step_conjunction = None
        for conjunction in self.conjunctions:
            if name.startswith(conjunction):
                step_conjunction, name = (conjunction, name.removeprefix(conjunction).strip())
        doc_string = None
        if len(p) > 2:
            doc_string = p[2]
        p[0] = TestStep(conjunction=step_conjunction, name=name, text=doc_string)

    def p_error(self, p):
        print(f'Syntax error at {p!r}')

    def __init__(self, lexer=GherkinLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self)

    def parse(self, source):
        return parser.parser.parse(data)


data = '''
 # fComment 2
Feature: My feature
    # Comment before description
    This feature description describes the feature.
    It is a multi line feature description.
    
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
    
# Comment 2
  Scenario: My Scenario 2
    Given scenario 2 step 1
    When scenario 2 step 2
      # sComment 1
    Then scenario 2 step 3
    And scenario 2 step 4
    But scenario 2 step 5
'''

# # Give the lexer some input
# # Build the lexer object
gherkin_lexer = GherkinLexer()
gherkin_lexer.test(data)

# Build the parser
parser = GherkinParser(lexer=gherkin_lexer)

# Parse an expression
ast = parser.parse(data)
print(ast)
