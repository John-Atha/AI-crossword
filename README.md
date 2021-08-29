# Harvard CS50's Introduction to Artificial Intelligence with Python 2021 course

### Project 3 - Crossword

* An AI to solve the crossword game.
* A board layout and a list of words are given
* The allowed positions should be filled with letters.
* Each word should not be used more than one time.
* Along with the solution logged in the terminal, an output image of it is produced.

##### Implementation
* The problem is being modelized as an Constraint Satisfaction Problem (CSP).
* The `crossword.py` file was given as part of the distribution code.
* The goal was to implement the `enforce_node_consistency`, `revise`, `ac3`, `assignment_complete`, `consistent`, `order_domain_values`, `selected_unassigned_variable`, and `backtrack` methods of the `generate.py` file.
* The `enforce_node_consistency` and `revise` methods aim to test the node and arc consistency respectively.
* The `ac3` method uses a queue with all the words-overlapping constraints to restrict the domains, before the main recursive method `backtrack` is called.
* The `assignment_complete` and `consistent` methods check if an assignment is complete and consistent respectively.
* The `order_domain_values` method is used by the `backtrack` method and it uses the `Least-Constraining-Value` heuristic to sort the preferred values of a domain that are about to be examined next.
* The `selected_unassigned_variable` method is used by the `backtrack` method and it uses the `Minimum-Remaining-Values` and `Degree` heuristics to pick the next unassigned variable to be examined.
* The `backtrack` method is a recursive method that tests the possible assignments that satisfy the constraints of the problem.
- - -

* Developer: Giannis Athanasiou
* Github Username: John-Atha
* Email: giannisj3@gmail.com