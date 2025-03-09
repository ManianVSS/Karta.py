 # fComment 2
 @my_tag4 @my_tag5
 @my_tag1
 Feature: My feature 2
   # Comment before description
   """
   This feature description describes the feature.
   It is a multi line feature description.
   """

  # Comment 1
   Example: My Scenario 21
     Given my sample step definition1
     When my sample step definition4
     # sComment 1
     Then my sample step definition3

   # Comment 2
   @my_scenario_tag5 @Smy_scenario_tag1
   @Smy_scenario_tag2
   Scenario: My Scenario 22
     Given my sample step definition2
     When my sample step definition1
     # sComment 1
     Then my sample step definition4
     And my sample step definition3
     But my sample step definition2