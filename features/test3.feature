 # fComment 2
 @my_tag3 @my_tag4
 @my_tag5
 Feature: My feature
    # Comment before description
   """
   This feature description describes the feature.
   It is a multi line feature description.
   """
        
   # Comment for Background ## Background:
   Background:
     Given my sample step definition1
     And my sample step definition1
     {
            "\"key\":\n\t 3": 1,
            key2: true,
            key3: "\"string value\"\n\t",
            key4: 10.3,
            key5: ["this", "is","an","array","with", 7, "values"],
            key6: {type:"Object value"}
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
     Given my sample step definition2
     When my sample step definition3
     # sComment 1
     Then my sample step definition4
        
    # Comment 2
   @my_scenario_tag4 @Smy_scenario_tag5
   @Smy_scenario_tag1
   Scenario: My Scenario 2
     Given my sample step definition1
     When my sample step definition2
     # sComment 1
     Then my sample step definition3
     And my sample step definition4
     But my sample step definition1