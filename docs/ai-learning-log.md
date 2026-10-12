# AI Learning Log From Ejeme Godwin

# Fellow 1: Ticket Workflow, Reports, and CLI

Updated upstream
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

This document records how both fellows used AI while developing
CampusFlow, what they learned, and how they evaluated or improved
AI suggestions.

---

# Fellow 2: Ticket Creation, Storage, Testing, and Documentation

## Interaction 1: Understanding Ticket Storage

- **Problem:** Understanding how ticket creation and JSON storage
  should work together.

- **AI suggestion:** Keep ticket validation and construction separate
  from the functions that load and save ticket data.

- **What I learned:** The ticket module is responsible for validating
  inputs, calculating priority, and creating a ticket. The storage
  module handles persistence and ticket identifiers.

- **My contribution:** I worked on ticket creation and storage and
  reviewed how the integration tests checked that tickets could
  be created, saved, and loaded again.

- **Verification:** The ticket creation and storage tests passed.

## Interaction 2: Improving Numeric Sorting Test Coverage

- **Problem:** Verifying that tickets with the same priority are
  sorted by their numeric IDs in the work queue.

- **AI suggestion:** Add tests using different ticket identifiers
  to check the ordering.

- **My improvement:** I recognized that ordinary sequential,
  zero-padded ticket IDs were not enough to distinguish numeric
  sorting from lexicographic sorting. I improved the test by using
  IDs such as `T999` and `T1000`.

- **What I learned:** A test can pass without properly proving the
  behavior it is intended to check. Good tests should distinguish
  correct behavior from plausible incorrect behavior.

- **Verification:** The workflow test suite passed, including
  the numeric sorting test.

## Interaction 3: Improving the Design Documentation

- **Problem:** Making the design document accurately describe the
  completed CampusFlow implementation.

- **AI suggestion:** Document the workflow rules, work queue ordering,
  reporting behavior, storage decisions, and current limitations.

- **My contribution:** I updated `docs/design-decisions.md` to explain
  these decisions, corrected the Markdown formatting, and documented
  the workflow and reporting behavior.

- **What I learned:** Documentation should describe the current
  implementation accurately instead of listing completed features
  as unfinished work.

- **Verification:** I ran `git diff --check` and the complete test
  suite. All 53 tests passed.

## Reflection

AI helped me identify gaps in test coverage and improve my
documentation. I learned that AI suggestions need to be evaluated
rather than accepted automatically. Improving the numeric sorting
test taught me to think about whether a test genuinely proves
the intended behavior. I remain responsible for understanding
my changes and verifying the results.

---

# Team Reflection

AI was used as a learning and development aid during the CampusFlow
sprint. It helped us reason about module responsibilities, storage,
workflow rules, testing, and documentation.

We evaluated suggestions against the assignment requirements,
reviewed the implementation, and used automated tests to check
behavior. We learned that AI-generated advice should not be accepted
without review and that testing must demonstrate the intended
behavior.

Both fellows remain responsible for understanding their contributions,
reviewing code changes, and verifying the final application.
Stashed changes
