from karta.plugins.step_identifier import StepIdentifier


def test_plain_text_match():
    identifier = StepIdentifier("I have cucumbers")
    step_text = "I have cucumbers"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [])


def test_single_regex_match():
    identifier = StepIdentifier('I have "\\d+" cucumbers')

    step_text = 'I have "10" cucumbers'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, ['10'])

    step_text = 'I have 15 cucumbers'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, ['15'])

    step_text = 'I have abc cucumbers'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert result == False


def test_multiple_regex_match():
    identifier = StepIdentifier('I have "\\d+" apples and "\\d+" oranges')

    step_text = 'I have "10" apples and 12 oranges'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, ['10', '12'])

    step_text = 'I have 15 apples and "100" oranges'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, ['15', "100"])

    step_text = 'I have 20 apples and "abc" oranges'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert result == False


def test_negative_extra_text():
    identifier = StepIdentifier('Hello world')
    step_text = 'Hello world!!'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (False, [])


def test_negative_partial_match():
    identifier = StepIdentifier('I have "\\d+" cucumbers')
    step_text = 'I have "10" cucumbers in my basket'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (False, ['10'])


def test_escaped_quotes_in_regex():
    identifier = StepIdentifier('I said \\"hello\\" to "(.*)"')
    step_text = 'I said \\"hello\\" to World'
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, ['World'])


def test_cucumber_expressions():
    identifier = StepIdentifier('I have {int} cucumbers')
    step_text = "I have 50 cucumbers"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [50])
    step_text = "I have abc cucumbers"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (False, [])

    identifier = StepIdentifier('I have {float} liters of orange juice')
    step_text = "I have 3.14 liters of orange juice"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [3.14])

    identifier = StepIdentifier('I have {bigdecimal} liters of orange juice and {double} liters of apple juice')
    step_text = "I have 10 liters of orange juice and .56789 liters of apple juice"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [10.0, 0.56789])
    step_text = "I have -.0 liters of orange juice and -0. liters of apple juice"
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [0.0, 0.0])

    identifier=StepIdentifier("I have {int} {word} and my message is {string}")
    step_text = "I have 10 oranges and my message is \"Hello to the world may be the 10\'th time!!\""
    result, parameters = identifier.match(step_text)
    print(
        "Matching step_identifier: [" + identifier.identifier + "] with step text: [" + step_text + "]:  Result:" + str(
            result) + " parameters:" + str(parameters))
    assert (result, parameters) == (True, [10, 'oranges',"Hello to the world may be the 10\'th time!!"])

def main():
    test_plain_text_match()
    test_single_regex_match()
    test_multiple_regex_match()
    test_negative_extra_text()
    test_negative_partial_match()
    test_escaped_quotes_in_regex()
    test_cucumber_expressions()

    print("All tests have passed")


if __name__ == '__main__':
    main()
