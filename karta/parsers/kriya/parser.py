from ply.lex import lex, TOKEN
from ply.yacc import yacc

from karta.core.models.test_catalog import TestFeature, TestScenario, TestStep, StepType, IterationPolicy
from karta.core.models.testdata import GeneratedObjectValue, ListDataValue, IntegerRangeValue, FloatRangeValue, \
    RandomStringValue, OneSelectedFromListValue, SomeSelectedFromListValue, ProbabilityMapOneValue, \
    ProbabilityMapSomeValue
from karta.core.utils.funcutils import wrap_function_before
from karta.core.utils.logger import logger


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
        'ITERATIONS',
        'ITERATION_POLICY',
        'BACKGROUND',
        'SCENARIO',
        "PROBABILITY",
        'STEP',
        'DOC_STRING',
        'TAG',

        'ASSERTION',
        'CONDITION',
        'LOOP',

        "LEFT_CURLY_BRACE",
        "RIGHT_CURLY_BRACE",
        "LEFT_PARENTHESIS",
        "RIGHT_PARENTHESIS",
        "LEFT_SQUARE_BRACKET",
        "RIGHT_SQUARE_BRACKET",

        "STRING",
        "COLON",
        "NUMBER",
        "BOOLEAN",
        "NULL",
        "COMMA",

        "STEPS",

        "DATA_INT_RANGE",
        "DATA_FLOAT_RANGE",
        "DATA_RANDOM_STRING",
        "DATA_ONE_FROM_LIST",
        "DATA_SOME_FROM_LIST",
        "DATA_ONE_FROM_MAP",
        "DATA_SOME_FROM_MAP",
        "DATA_PROBABILITY_PERCENT",

        "IDENTIFIER",
    )

    # brackets regex
    t_LEFT_CURLY_BRACE = r'\{'
    t_RIGHT_CURLY_BRACE = r'\}'
    t_LEFT_PARENTHESIS = r'\('
    t_RIGHT_PARENTHESIS = r'\)'
    t_LEFT_SQUARE_BRACKET = r'\['
    t_RIGHT_SQUARE_BRACKET = r'\]'

    # commas used to separate items in both objects and arrays
    t_COMMA = r','

    # colon used in objects to define key: value pairs
    t_COLON = r':'

    t_DATA_INT_RANGE = r'\$int_range'
    t_DATA_FLOAT_RANGE = r'\$float_range'
    t_DATA_RANDOM_STRING = r'\$random_string'
    t_DATA_ONE_FROM_LIST = r'\$one_from_list'
    t_DATA_SOME_FROM_LIST = r'\$some_from_list'
    t_DATA_ONE_FROM_MAP = r'\$one_from_map'
    t_DATA_SOME_FROM_MAP = r'\$some_from_map'

    t_IDENTIFIER = r'[_a-zA-Z][_a-zA-Z0-9]*'

    # Ignored token with an action associated with it
    @TOKEN(r'[\s]+')
    def t_ignore_whitespaces(self, t):
        t.lexer.lineno += t.value.count('\n')
        pass

    @TOKEN(r'(\#[^\n]*) | (\/\*(.|\n|\s)+?(?=\*\/)\*\/)')
    def t_ignore_COMMENT(self, t):
        t.lexer.lineno += t.value.count('\n')
        t.value = t.value

    @TOKEN(r'\@[^\n@]*')
    def t_TAG(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('@').strip()
        return t

    @TOKEN(r'Feature:([ \t]+)?[^\n]+')
    def t_FEATURE(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Feature:').strip()
        return t

    @TOKEN(r'Iterations:([ \t]+)?[^\n]+')
    def t_ITERATIONS(self, t):
        t.value = t.value.strip().removeprefix('Iterations:').strip()
        t.value = int(t.value)
        return t

    @TOKEN(r'IterationPolicy:([ \t]+)?[^\n]+')
    def t_ITERATION_POLICY(self, t):
        t.value = t.value.strip().removeprefix('IterationPolicy:').strip()
        if t.value == "all scenario per iteration":
            t.value = IterationPolicy.ALL_PER_ITERATION
        elif t.value == "one scenario per iteration":
            t.value = IterationPolicy.ONE_PER_ITERATION
        elif t.value == "some scenario per iteration":
            t.value = IterationPolicy.SOME_PER_ITERATION
        else:
            raise SyntaxError(f"Invalid ScenarioRunPerIteration value: {t.value}")
        return t

    @TOKEN(r'Background:')
    def t_BACKGROUND(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(Scenario|Example):([ \t]+)?[^\n]+')
    def t_SCENARIO(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        if t.value.startswith('Scenario:'):
            t.value = t.value.removeprefix('Scenario:').strip()
        if t.value.startswith('Example:'):
            t.value = t.value.removeprefix('Example:').strip()
        return t

    @TOKEN(r'Probability:\s\d{1,3}(\.\d{1,2})?%')
    def t_PROBABILITY(self, t):
        t.value = t.value.strip()
        if t.value.startswith('Probability:'):
            t.value = t.value.removeprefix('Probability:').strip()[:-1]
            t.value = float(t.value) / 100.0
        return t

    @TOKEN(r'(Given | When | Then | And | But)([ \t]+)?[^\n]+')
    def t_STEP(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(Verify | Validate)([ \t]+)?[^\n]+')
    def t_ASSERTION(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(If | Condition:)([ \t]+)?[^\n]+')
    def t_CONDITION(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip()
        return t

    @TOKEN(r'(While | Until)([ \t]+)?[^\n]+')
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

    @TOKEN(r'%\d{1,2}(\.\d{1,2})?')
    def t_DATA_PROBABILITY_PERCENT(self, t):
        t.value = t.value.strip()
        t.value = float(t.value[1:]) / 100.0
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

    @TOKEN(r'Steps:([ \t]+)?[^\n]*')
    def t_STEPS(self, t):
        # t.lexer.lineno += t.value.count('\n')
        t.value = t.value.strip().removeprefix('Steps:').strip()
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
class KriyaParser(object):
    tokens = KriyaLexer.tokens
    conjunctions = ['Given', 'When', 'Then', 'But', 'And']
    condition_conjunctions = ['If', 'Condition']
    loop_conjunctions = ['While', 'Until']

    # Write functions for each grammar rule which is
    # specified in the docstring.
    def p_feature(self, p):
        """
        feature : tags FEATURE scenarios
                | tags FEATURE ITERATIONS scenarios
                | tags FEATURE ITERATIONS ITERATION_POLICY scenarios
                | tags FEATURE DOC_STRING scenarios
                | tags FEATURE DOC_STRING ITERATIONS scenarios
                | tags FEATURE DOC_STRING ITERATIONS ITERATION_POLICY scenarios
                | tags FEATURE background scenarios
                | tags FEATURE ITERATIONS background scenarios
                | tags FEATURE ITERATIONS ITERATION_POLICY background scenarios
                | tags FEATURE DOC_STRING background scenarios
                | tags FEATURE DOC_STRING ITERATIONS background scenarios
                | tags FEATURE DOC_STRING ITERATIONS ITERATION_POLICY background scenarios
        """
        tags = []
        if p.slice[1].type == 'tags':
            tags = p[1]
            del p.slice[1]

        description = None
        if p.slice[2].type == 'DOC_STRING':
            description = p[2]
            del p.slice[2]

        iterations = 1
        if p.slice[2].type == 'ITERATIONS':
            iterations = p[2]
            del p.slice[2]

        iteration_policy = IterationPolicy.ALL_PER_ITERATION
        if p.slice[2].type == 'ITERATION_POLICY':
            iteration_policy = p[2]
            del p.slice[2]

        background_steps = []
        if p.slice[2].type == 'background':
            background_steps = [*p[2]]
            del p.slice[2]

        p[0] = TestFeature(name=p[1].strip(), description=description, iterations=iterations,
                           iteration_policy=iteration_policy, setup_steps=background_steps, scenarios=p[2], tags=tags, )
        p[0].line_number = p.slice[1].lineno

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
                 | tags SCENARIO PROBABILITY steps
                 | tags SCENARIO DOC_STRING steps
                 | tags SCENARIO DOC_STRING PROBABILITY steps
        """
        tags = []
        if p.slice[1].type == 'tags':
            tags = p[1]
            del p.slice[1]

        description = None
        if p.slice[2].type == 'DOC_STRING':
            description = p[2]
            del p.slice[2]

        probability = 1.0
        if p.slice[2].type == 'PROBABILITY':
            probability = p[2]
            del p.slice[2]

        p[0] = TestScenario(name=p[1].strip(), steps=p[2], tags=tags, description=description, probability=probability)
        p[0].line_number = p.slice[1].lineno

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
             | STEP data_object
             | CONDITION STEPS LEFT_CURLY_BRACE steps RIGHT_CURLY_BRACE
             | CONDITION data_object STEPS LEFT_CURLY_BRACE steps RIGHT_CURLY_BRACE
             | LOOP STEPS LEFT_CURLY_BRACE steps RIGHT_CURLY_BRACE
             | LOOP data_object STEPS LEFT_CURLY_BRACE steps RIGHT_CURLY_BRACE
        """
        name = p[1]
        step_conjunction = None
        step_type = None
        if p.slice[1].type == 'STEP':
            step_type = StepType.STEP
            for conjunction in self.conjunctions:
                if name.startswith(conjunction):
                    step_conjunction, name = (conjunction, name.removeprefix(conjunction).strip())
        elif p.slice[1].type == 'CONDITION':
            step_type = StepType.CONDITION
            for conjunction in self.condition_conjunctions:
                if name.startswith(conjunction):
                    step_conjunction, name = (conjunction, name.removeprefix(conjunction).strip())
        elif p.slice[1].type == 'LOOP':
            step_type = StepType.LOOP
            for conjunction in self.loop_conjunctions:
                if name.startswith(conjunction):
                    step_conjunction, name = (conjunction, name.removeprefix(conjunction).strip())
        doc_string = None
        if len(p) > 2:
            if p.slice[2].type == 'DOC_STRING':
                doc_string = p[2]
                del p.slice[2]

        data_rules = {}
        if len(p) > 2:
            if p.slice[2].type == 'data_object':
                data_rules = p[2]
                del p.slice[2]

        nested_steps = []
        if len(p) > 2:
            if p.slice[2].type == 'STEPS':
                nested_steps = p[4]

        p[0] = TestStep(type=step_type, conjunction=step_conjunction, name=name, data_rules=data_rules,
                        steps=nested_steps if len(nested_steps) > 0 else None)
        p[0].line_number = p.slice[1].lineno

    def p_data_object(self, p):
        """
        data_object : LEFT_CURLY_BRACE pairs RIGHT_CURLY_BRACE
        """
        p[0] = GeneratedObjectValue(fields_dict=p[2])

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
        array : LEFT_SQUARE_BRACKET items RIGHT_SQUARE_BRACKET
        """
        p[0] = ListDataValue(values=p[2])

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
        value : DATA_INT_RANGE LEFT_PARENTHESIS NUMBER COMMA NUMBER RIGHT_PARENTHESIS
              | DATA_FLOAT_RANGE LEFT_PARENTHESIS NUMBER COMMA NUMBER RIGHT_PARENTHESIS
              | DATA_RANDOM_STRING LEFT_PARENTHESIS NUMBER RIGHT_PARENTHESIS
              | DATA_ONE_FROM_LIST array
              | DATA_SOME_FROM_LIST array
              | DATA_ONE_FROM_MAP probability_map
              | DATA_SOME_FROM_MAP probability_map
              | data_object
              | array
              | NUMBER
              | STRING
              | BOOLEAN
              | NULL

        """
        if p.slice[1].type == 'DATA_INT_RANGE':
            p[0] = IntegerRangeValue(min=int(p[3]), max=int(p[5]))
        elif p.slice[1].type == 'DATA_FLOAT_RANGE':
            p[0] = FloatRangeValue(min=float(p[3]), max=float(p[5]))
        elif p.slice[1].type == 'DATA_RANDOM_STRING':
            p[0] = RandomStringValue(length=int(p[3]))
        elif p.slice[1].type == 'DATA_ONE_FROM_LIST':
            p[0] = OneSelectedFromListValue(values=p[2].values if isinstance(p[2], ListDataValue) else p[2])
        elif p.slice[1].type == 'DATA_SOME_FROM_LIST':
            p[0] = SomeSelectedFromListValue(values=p[2].values if isinstance(p[2], ListDataValue) else p[2])
        elif p.slice[1].type == 'DATA_ONE_FROM_MAP':
            p[0] = ProbabilityMapOneValue(probability_map=p[2])
        elif p.slice[1].type == 'DATA_SOME_FROM_MAP':
            p[0] = ProbabilityMapSomeValue(probability_map=p[2])
        elif p.slice[1].type == 'data_object':
            p[0] = p[1]
        elif p.slice[1].type == 'array':
            p[0] = p[1]
        else:
            p[0] = p[1]

    def p_probability_map(self, p):
        """
        probability_map : LEFT_CURLY_BRACE probability_pairs RIGHT_CURLY_BRACE
        """
        p[0] = p[2]

    def p_probability_pairs(self, p):
        """
        probability_pairs : probability_pair
                          | empty
        """
        if p.slice[1].type == 'probability_pair':
            p[0] = p[1]
        else:
            p[0] = {}

    def p_probability_pair(self, p):
        """
        probability_pair : DATA_PROBABILITY_PERCENT COLON value COMMA probability_pair
                         | DATA_PROBABILITY_PERCENT COLON value
        """
        p[0] = {p[3]: p[1]}
        if len(p) > 4:
            p[0].update(p[5])

    def p_error(self, p):
        logger.error(f'Syntax error at {p!r}')

    def __init__(self, lexer=KriyaLexer()):
        self.lexer = lexer
        self.parser = yacc(module=self, )

    def parse(self, source):
        return self.parser.parse(source)


if __name__ == '__main__':
    data = r''' # fComment 2
 @my_tag3 @my_tag4
 @my_tag5
  /*
    Multi line
    comment for the
    feature
  */
 Feature: My feature 3
    # Comment before description
   ```
   This feature description describes the feature.
   It is a multi line feature description.
   ```
   Iterations: 100
   IterationPolicy: one scenario per iteration
        
   # Comment for Background ## Background:
   Background:
     Given my sample step definition1
     And my sample step definition1
     {
            "\"key\":\n\t 3": 1,
            key2: true,
            key3: "\"string value\"\n\t",
            key3: 10.3,
            key5: ["this", "is","an","array","with", 7, "values"],
            key6: {type:"Object value"},

            #Dynamic data
            dyna_data1: $int_range(1, 10),
            dyna_data2: $float_range(1.0, 10.0),
            dyna_data3: $random_string(10),
            dyna_data4: $one_from_list["this", "is","an","array","with", 7, "values"],
            dyna_data5: $some_from_list["this", "is","an","array","with", 7, "values"],
            dyna_data6: $one_from_map{
                %10: "dvalue1",
                %20: "dvalue2",
                %30: "dvalue3",
                %40: "dvalue4"
             },
            dyna_data7: $some_from_map{
                %10: "dsvalue1",
                %20: "dsvalue2",
                %30: "dsvalue3",
                %40: "dsvalue4"
             },
             dyna_object:{
                dyna_odata1: $int_range(1, 10),
                dyna_odata2: $float_range(1.0, 10.0),
                dyna_odata3: $random_string(10),
                dyna_odata4: $one_from_list["this", "is","an","array","with", 7, "values"],
                dyna_odata5: $some_from_list["this", "is","an","array","with", 7, "values"],
                dyna_odata6: $one_from_map{
                    %10: "dovalue1",
                    %20: "dovalue2",
                    %30: "dovalue3",
                    %40: "dovalue4"
                 },
                dyna_odata7: $some_from_map{
                    %10: "dosvalue1",
                    %20: "dosvalue2",
                    %30: "dosvalue3",
                    %40: "dosvalue4"
                 }
             }
     }

     And my sample step definition2
     {
        table_data: [
            {
                f1: "v11",
               "f2\n\t": "v12",
                f3: "v13"
            },
            {
                f1: "v21",
               "f2\n\t": "v22",
                f3: "v23"
            }
        ]
    }
            
   # Comment 1
   Example: My Scenario 1
     Probability: 40%
     Given my sample step definition2
     If my condition 1 is met
     Steps:
     {
        Given my sample step definition1
        And my sample step definition1
     }
     When my sample step definition3
     # sComment 1
     Then my sample step definition4
        
    # Comment 2
   @my_scenario_tag4 @Smy_scenario_tag5
   @Smy_scenario_tag1
   Scenario: My Scenario 2
     Probability: 60%
     Given my sample step definition1
     When my sample step definition2
     # sComment 1
     Then my sample step definition3
     And my sample step definition4
     But my sample step definition1
     While my condition 2 is met
     {
           sample_value:5
     }
     Steps:
     {
        Given my sample step definition1
        And my sample step definition1
     }
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
