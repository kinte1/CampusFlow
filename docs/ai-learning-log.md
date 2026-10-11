# AI Learning Log

- **Interaction 1:** Understanding Application Structure

- **My work:** I worked on organizing CampusFlow into separate modules for ticket storage, workflow management, reports, and the command-line interface.

- **How I used AI:** I asked questions about the responsibilities of each module and how they should communicate with one another.

- **What I learned:** I developed a better understanding of separation of concerns, Python imports, and why related functionality should be organized into appropriate modules.

- **How I applied the learning:** I used this understanding while implementing and reviewing the workflow features and their interactions with the storage module.

— **Interaction 2:** Understanding Ticket Workflow and Validation

- **My work:** I implemented ticket assignment, status transitions, reopening resolved tickets, and priority-based work queue ordering.

- **How I used AI:** I asked for explanations of workflow rules, validation approaches, and how to write tests for invalid operations.

-**What I learned:** I learned how to enforce business rules, raise meaningful exceptions, and test both successful operations and situations where an operation should be rejected.

- **How I applied the learning:** I tested scenarios such as starting an unassigned ticket, skipping workflow stages, and modifying a resolved ticket without reopening it.

- **Interaction 3:** Testing and Improving the Implementation

- **My work:** I ran the test suite, investigated failures, checked the command-line interface, and reviewed feedback on my pull request.

- **How I used AI:** I asked for help interpreting test results, understanding potential edge cases, and evaluating suggestions for improving test coverage.

- **What I learned:** I learned that passing tests are important, but tests should also cover boundary conditions, invalid inputs, and ordering rules.

- **How I applied the learning:** I used test results and review feedback to identify additional cases worth covering, including numeric ticket-ID ordering and invalid status values.

## Reflection

I used AI as a learning and debugging aid throughout CampusFlow. My focus was to understand the implementation, verify behaviour through tests, and make informed decisions about changes. The project helped me practise Python modules, JSON persistence, input validation, exception handling, workflow management, automated testing, and GitHub collaboration.

I will continue improving my ability to explain the code, identify edge cases, and implement solutions independently.
