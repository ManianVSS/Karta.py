# fComment 2
@MyTag1 @MyTag2
@MyTag3
Feature: My feature 2
  # Comment before description
  This feature description describes the feature.
  It is a multi line feature description.

  # Comment for Background ## Background:
  Background:
    This background description describes the background steps.
    It is a multi line background description.
    Given background step1
    And background step2
    """
    Background step2?
    ===============
    This is the text block for background step2.
    Which could span multiple lines.
    """
    And background step3
      | f1\| | f2\n | f3\t |
      | v11  | v12  | v13  |
      | v21  | v 22 | v23  |

  Rule: Rule 1+
    Background:
    This background description describes the background steps.
    It is a multi line background description.
    Given background step1
    And background step2
    # Comment 1
    Example: My Scenario 1
      This example description describes the example(scenario).
      It is a multi line example description.
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

  Rule: Rule 2
    # Comment 2
    @SMyTag1 @SMyTag2
    @SMyTag3
    Scenario: My Scenario 2
      This scenario description describes the scenario.
      It is a multi line scenario description.
      Given scenario 2 step 1
      When scenario 2 step 2
      # sComment 1
      Then scenario 2 step 3
      And scenario 2 step 4
      But scenario 2 step 5

    # Comment 3
    @SoMyTag1 @SoMyTag2
    @SoMyTag3
    Scenario Outline: My Scenario outline.
      Given <var1> scenario outline step 1
      When scenario outline  step 2
      # sComment 1
      Then scenario outline  step 3
      And <var2> scenario outline  step 4
      But <var3> scenario outline  step 5

      Examples:
        | var1    | var2    | var3    |
        | value11 | value12 | value13 |
        | value21 | value22 | value23 |