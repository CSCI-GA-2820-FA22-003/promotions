Feature: The promotion store service back-end
    As a promotion Store Admin
    I need a RESTful catalog service
    So that I can keep track of all the promotions

Background:
    Given the following promotions
        | Name        | Description   | Type             | Value | Percent | Status | Expiry     |
        | Promotion 1 | Description 1 | ABS_DISCOUNT     | 20    | 0       | True   | 2019-11-18 |
        | Promotion 2 | Description 2 | ABS_DISCOUNT     | 30    | 0       | True   | 2020-08-13 |
        | Promotion 3 | Description 3 | PERCENT_DISCOUNT | 0     | 10      | False  | 2021-04-01 |
        | Promotion 4 | Description 4 | PERCENT_DISCOUNT | 0     | 20      | True   | 2018-06-04 |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Promotions Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "Promotion 5"
    And I set the "Description" to "Description 5"
    And I select "ABS_DISCOUNT" in the "Type" dropdown
    And I set the "Value" to "50"
    And I set the "Percent" to "0"
    And I select "False" in the "Status" dropdown
    And I set the "Expiry" to "06-16-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Promotion 5" in the "Name" field
    And I should see "Description 5" in the "Description" field
    And I should see "ABS_DISCOUNT" in the "Type" dropdown
    And I should see "50" in the "Value" field
    And I should see "0" in the "Percent" field
    And I should see "False" in the "Status" dropdown
    And I should see "2022-06-16" in the "Expiry" field

Scenario: Get a Promotion
    When I visit the "Home Page"
    And I set the "Name" to "Promotion 6"
    And I set the "Description" to "Description 6"
    And I select "ABS_DISCOUNT" in the "Type" dropdown
    And I set the "Value" to "70"
    And I set the "Percent" to "0"
    And I select "True" in the "Status" dropdown
    And I set the "Expiry" to "06-16-2022"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Promotion 6" in the "Name" field
    And I should see "Description 6" in the "Description" field
    And I should see "ABS_DISCOUNT" in the "Type" dropdown
    And I should see "70" in the "Value" field
    And I should see "0" in the "Percent" field
    And I should see "True" in the "Status" dropdown
    And I should see "2022-06-16" in the "Expiry" field

Scenario: List all Promotions
    When I visit the "Home Page"
    And I press the "Searchall" button
    Then I should see the message "Success"
    And I should see "Promotion 1" in the results
    And I should see "Promotion 2" in the results
    And I should not see "Promotion 5" in the results

Scenario: Activate a Promotion
    When I visit the "Home Page"
    And I select "False" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Promotion 3" in the "Name" field
    And I should see "False" in the "Status" dropdown
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Activate" button
    Then I should see the message "Promotion has been Activated!"
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Promotion 3" in the "Name" field
    And I should see "Description 3" in the "Description" field
    And I should see "True" in the "Status" dropdown

Scenario: Query a promotion using its status
    When I visit the "Home Page"
    And I select "True" in the "Status" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Promotion 1" in the results
    And I should see "Promotion 2" in the results
    And I should see "Promotion 4" in the results
    And I should not see "Promotion 3" in the results
