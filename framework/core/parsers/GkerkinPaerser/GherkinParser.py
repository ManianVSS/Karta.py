from ply.lex import lex, TOKEN
from ply.yacc import yacc

from framework.core.models.TestFeature import TestFeature
from framework.core.models.TestScenario import TestScenario
from framework.core.models.TestStep import TestStep


# --- Tokenizer

# noinspection PyPep8Naming
class GherkinLexer(object):
    # All tokens must be named in advance.
    tokens = ('FEATURE', 'SCENARIO', 'NAME', 'CONJUNCTION',)

    # Ignored token with an action associated with it
    @TOKEN(r'[\s]+')
    def t_ignore_newline(self, t):
        t.lexer.lineno += t.value.count('\n')

    @TOKEN(r'(\s+)?\#[^\n]*')
    def t_ignore_COMMENT(self, t):
        t.value = t.value

    @TOKEN(r'(\s+)?Feature:')
    def t_FEATURE(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Feature:')
        return t

    @TOKEN(r'(\s+)?Scenario:')
    def t_SCENARIO(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Scenario:')
        return t

    @TOKEN(r'(\s+)?(Given | When | Then | And | But)')
    def t_CONJUNCTION(self, t):
        t.value = t.value.strip()
        return t

    @TOKEN(r'(\s+)?[^\n]+')
    def t_NAME(self, t):
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

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)


# --- Parser
# noinspection PyPep8Naming
class GherkinParser(object):
    tokens = GherkinLexer.tokens

    # Write functions for each grammar rule which is
    # specified in the docstring.
    def p_feature(self, p):
        """
        feature : FEATURE NAME scenarios
        """
        # p is a sequence that represents rule contents.
        #
        # expression : term PLUS term
        #   p[0]     : p[1] p[2] p[3]
        #
        if p.slice[1].type == 'COMMENT':
            del p.slice[1]
        p[0] = TestFeature(name=p[2].strip(), scenarios=p[3])  # ('feature', *p[1:],)

    def p_scenarios(self, p):
        """
        scenarios : scenario
                  | scenario scenarios
        """
        p[0] = [p[1]]
        if len(p) > 2:
            for item in p[2]:
                p[0].append(item)
        # ('scenarios', *p[1:])

    def p_scenario(self, p):
        """
        scenario : SCENARIO NAME steps
        """
        if p.slice[1].type == 'COMMENT':
            del p.slice[1]
        p[0] = TestScenario(name=p[2].strip(), steps=p[3])  # ('scenario', *p[1:])

    def p_steps(self, p):
        """
        steps : step
              | step steps
        """
        p[0] = [p[1]]
        if len(p) > 2:
            for item in p[2]:
                p[0].append(item)
        # p[0] = [*p[1:]]

    def p_step(self, p):
        """
        step : CONJUNCTION NAME
        """
        if p.slice[1].type == 'COMMENT':
            del p.slice[1]
        step = TestStep(conjunction=p[1].strip(), name=p[2].strip())
        # step.conjunction = p[1].strip()
        # step.name = p[2].strip()
        p[0] = step  # ('step', *p[1:])

    def p_error(self, p):
        print(f'Syntax error at {p!r}')

    def __init__(self, lexer=GherkinLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self)

    def parse(self, source):
        ast = parser.parser.parse(data)
        return ast


data = '''
 # fComment 2
Feature: Guess the word

    # Comment 1
  Scenario: Maker starts a game
    
    When the Maker starts a game
      # sComment 1
    Then the Maker waits for a Breaker to join
    
# Comment 2
  Scenario: Breaker joins a game
      # sComment 1
    Given the Maker has started a game with the word "silky"
    When the Breaker joins the Maker's game
    Then the Breaker must guess a word with 5 characters
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
