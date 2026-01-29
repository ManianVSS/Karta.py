import re

from re import Pattern
from typing import Union, Any, Callable

from karta.core.models.generic import Context


# noinspection SpellCheckingInspection
class StepIdentifier:
    """
    Represents a step identifier for step definitions.
    Step identifier can have regex patterns enclosed in double quotes to match dynamic parts.
    Step identifers can also have cucumber expressions like {int}, {string}, etc.
    The backend step definitions will consume the matched regex groups or cucumber expression parameters.
    StepIdentifier stores the segements of patterns for matching step texts.
    """

    SEGMENTS_TYPE_TO_DECLARATION_REGEX_PATTERNS = {
        "regex": re.compile(r'"(.*?)(?<!\\)"'),
        "cucumber_ex_int": re.compile(r'\{int}'),
        "cucumber_ex_float": re.compile(r'\{float}'),
        "cucumber_ex_word": re.compile(r'\{word}'),
        "cucumber_ex_string": re.compile(r'\{string}'),
        # Not support anonymouss {} cucumber expression for now
        "cucumber_ex_bigdecimal": re.compile(r'\{bigdecimal}'),
        "cucumber_ex_double": re.compile(r'\{double}'),
        "cucumber_ex_byte": re.compile(r'\{byte}'),
        "cucumber_ex_short": re.compile(r'\{short}'),
        "cucumber_ex_long": re.compile(r'\{long}'),
    }

    INT_PATTERN = re.compile(r'(-?\d+)')
    FLOAT_PATTERN = re.compile(r'(-?(\d+(\.?(\d*)?))|(-?\d*\.\d+))')

    SEGMENT_TYPE_TO_REGEX_PATTERNS = {
        # Regex patten will come from the step identifier directly
        "regex": "",
        "cucumber_ex_int": INT_PATTERN,
        "cucumber_ex_float": FLOAT_PATTERN,
        "cucumber_ex_word": re.compile(r'(\w+)'),
        "cucumber_ex_string": re.compile(r'"(.*?)"'),
        "cucumber_ex_bigdecimal": FLOAT_PATTERN,
        "cucumber_ex_double": FLOAT_PATTERN,
        "cucumber_ex_byte": INT_PATTERN,
        "cucumber_ex_short": INT_PATTERN,
        "cucumber_ex_long": INT_PATTERN,
    }

    # Regex to match special characters that denote the start of a segment
    SPECIAL_CHARACTERS_REGEX = re.compile(r'(?<!\\)"|{')

    def __init__(self, identifier: str, backend_function: Union[Callable, None] = None):
        """

        :param identifier:
        :param backend_function: A callable function which takes Context as the first parameter
        and optionally positional arguments matching regex or cucumber expression groups
        """
        self.identifier: str = identifier
        # Split the identifier into segments based on the defined patterns
        self.segments: list[tuple[str, Union[str, list[Pattern]]]] = self._parse_identifier_to_segments(identifier)

        self.backend_function: Callable[[dict, ...], Union[None, bool, dict, tuple[bool, dict]]] = backend_function

    def __str__(self):
        return self.identifier

    def _parse_identifier_to_segments(self, identifier: str) -> list[tuple[str, Union[str, list[Pattern]]]]:
        segments: list[tuple[str, Union[str, list[Pattern]]]] = []
        current_index = 0

        while current_index < len(identifier):
            matched = False
            for segment_type, pattern in self.SEGMENTS_TYPE_TO_DECLARATION_REGEX_PATTERNS.items():
                match = pattern.search(identifier, current_index)
                if match and match.start() == current_index:
                    if segment_type == "regex":
                        regex_pattern = match.group(1)
                        segments.append(
                            (segment_type, [re.compile(regex_pattern), re.compile('"' + regex_pattern + '"')]))
                    else:
                        segments.append((segment_type, [self.SEGMENT_TYPE_TO_REGEX_PATTERNS[segment_type]]))
                    current_index = match.end()
                    matched = True
                    break
            # If not matched by any regex or cucumber expression segment type, it is a text segment
            # Extract the static text until the next special segment
            if not matched:
                match_until_special = self.SPECIAL_CHARACTERS_REGEX.search(identifier, current_index)
                end_index = match_until_special.start() if match_until_special else len(identifier)
                text_segment = identifier[current_index:end_index]
                segments.append(("text", text_segment))
                current_index = end_index

        # If index is not at the end, it means there are unmatched parts, throw value error
        if current_index != len(identifier):
            raise ValueError(f"Invalid step identifier format: {identifier}")

        return segments

    def match(self, step_text: str) -> tuple[bool, list]:
        """
        Check if the step_text matches this step identifers using the segments.
        Also extract the value of the matched regex or cucumber expression groups to return as parameters
        :param step_text: The text of the step to match.
        :return: A tuple of bool and the matched parameters as a list.
        """
        paramters_matched = []

        current_index = 0

        # Iterate through the segments and match against the step text
        for segment_type, expected in self.segments:
            if segment_type == 'text':
                # Match the text segment
                segment_len = len(expected)
                if step_text[current_index:current_index + segment_len] == expected:
                    current_index += segment_len
                else:
                    return False, paramters_matched
            else:  # Segment is a regex or cucumber expression
                matched = False
                for pattern in expected:
                    match = pattern.match(step_text, current_index)
                    if match:
                        matched = True
                        matched_text: str = match.group(0)
                        current_index += len(matched_text)

                        # Depending on the segment type process the matched_text to parse the value
                        if (segment_type == "cucumber_ex_int") or (segment_type == "cucumber_ex_byte") or (
                                segment_type == "cucumber_ex_short") or (segment_type == "cucumber_ex_long"):
                            paramters_matched.append(int(matched_text))
                        elif (segment_type == "cucumber_ex_float") or (segment_type == "cucumber_ex_bigdecimal") or (
                                segment_type == "cucumber_ex_double"):
                            paramters_matched.append(float(matched_text))
                        elif segment_type == "cucumber_ex_word":
                            paramters_matched.append(matched_text)
                        elif (segment_type == "cucumber_ex_string") or (segment_type == "regex"):
                            # If matched text is enclosed within double quotes, remove them
                            if matched_text.startswith('"') and matched_text.endswith('"'):
                                matched_text = matched_text[1:-1]
                            paramters_matched.append(matched_text)
                        else:
                            # Unexpected condition
                            return False, paramters_matched

        # If the entire step_text is not consumed, it is not a match
        if current_index != len(step_text):
            return False, paramters_matched

        return True, paramters_matched
