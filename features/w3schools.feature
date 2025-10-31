@web_automation
@w3schools
Feature: Application Object Model demo feature
  ```
  This feature demonstrates the Application Object Model (AOM) in Karta.
  ```
  Iterations: 2
  IterationPolicy: one scenario per iteration

  @chrome
  Scenario: Navigate W3schools site in chrome
  Probability: 50%
#    Given w3schools application is launched
#    {
#      browser: "chrome"
#    }
    When w3schools learn html home page is opened
    Then w3schools learn html introduction page is opened
    And w3schools learn html home page is opened from html introduction page
    And w3schools home page is opened
#    Then w3schools application is closed

  @firefox
  Scenario: Navigate W3schools site in firefox
  Probability: 50%
#    Given w3schools application is launched
#    {
#      browser: "firefox"
#    }
    When w3schools learn html home page is opened
    Then w3schools learn html introduction page is opened
    And w3schools learn html home page is opened from html introduction page
    And w3schools home page is opened
#    Then w3schools application is closed

