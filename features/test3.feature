 # fComment 2
 @MyTag1 @MyTag2
 @MyTag3
 Feature: My feature
  # Comment before description
  This feature description describes the feature.
  It is a multi line feature description.
        
  # Comment for Background ## Background:
  Background:
    Given my sample step definition1
    And my sample step definition1

    And my sample step definition2
    | f1\| | f2\n | f3\t |
    | v11  | v12  | v13  |
    | v21  | v 22 | v23  |
            
  # Comment 1
  Example: My Scenario 1
     Given my sample step definition2
        """
        Scenario 1 step1?
        ===============
        This is the text block for Scenario 1 step1.
        Which could span multiple lines.
        """
     When my sample step definition3
          # sComment 1
     Then my sample step definition4
        
    # Comment 2
   @SMyTag1 @SMyTag2
   @SMyTag3
   Scenario: My Scenario 2
     Given my sample step definition1
     When my sample step definition2
          # sComment 1
     Then my sample step definition3
     And my sample step definition4
     But my sample step definition1