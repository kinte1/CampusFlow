# AI Learning Log

This document records how both fellows used AI while developing
CampusFlow, what they learned, and how they evaluated or improved the
AI's suggestions.

Each cycle uses the six fields the sprint brief asks for: the concept
gap, the question asked, a summary of the AI guidance, a tiny unrelated
experiment, independent verification, and the final engineering
decision.

Two fields are not present in the original notes: the exact wording of
each question, and a tiny unrelated experiment. They are marked
**not recorded** rather than reconstructed, because inventing them would
misrepresent what happened. Each fellow should paste them from their own
AI session before submission. Everything else below comes from the
records the team already had.

---

# Fellow 1: Ticket Workflow, Reports, and CLI

## Cycle 1: Choosing the Correct Module for Ticket Data

**Concept gap:** Deciding how CampusFlow should be split into modules,
and where the workflow should get its existing tickets from.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Separate the responsibilities of validation,
workflow, storage, reporting, and the command-line interface. A module's
responsibility is different from where its data is stored: the workflow
module manages ticket operations, while the storage module handles JSON
persistence through `load_tickets()` and `save_tickets()`.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The workflow tests exercise the
assignment and persistence paths through `load_tickets()` and
`save_tickets()`, and the module imports resolve without circular
dependencies. The fellow also reviewed how the workflow features
interacted with storage.

**Final engineering decision:** Use the storage module's functions
rather than keeping the ticket list inside `workflow.py`. The fellow
initially suggested the latter and changed position after seeing that
loading existing records is what preserves data between operations.

## Cycle 2: Understanding Ticket Workflow and Validation

**Concept gap:** How to enforce workflow rules — assignment before
work starts, no skipping stages, reopening before modifying a resolved
ticket — and how to test operations that should be rejected.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Explain the allowed status transitions and
raise a clear exception at each invalid one, then test both the
successful operations and the situations that must be rejected.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The fellow tested starting an unassigned
ticket, skipping workflow stages, and modifying a resolved ticket
without reopening it. Those cases are covered by the workflow tests.

**Final engineering decision:** Enforce the rules in the workflow
module with `ValueError` messages that say what the user should do
instead, and keep the invalid cases in the test suite.

## Cycle 3: Testing and Improving the Implementation

**Concept gap:** Interpreting test results, finding edge cases, and
completing the required work within a limited submission window.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Use the failing tests and review feedback
to widen coverage, including boundary conditions, invalid inputs, and
ordering rules. The AI initially proposed a question-and-answer,
learn-by-exploration approach.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The fellow ran the test suite,
investigated failures, checked the command-line interface, and reviewed
the pull-request feedback.

**Final engineering decision:** Stop the question-and-answer approach
and prioritise completing the implementation, because only one hour
remained. Work then went to workflow management, reports, CLI
integration, tests, documentation, and Git collaboration. This is the
team's recorded case of changing the AI's suggested approach after
reviewing the constraints.

### Reflection

AI helped me understand module responsibilities, Python imports,
persistence, and workflow design. I learned that separating
responsibilities makes a project easier to maintain and test, and that
AI assistance should adapt to the task and the time available. I remain
responsible for reviewing the implementation, running tests, and
checking that the requirements are satisfied.

---

# Fellow 2: Ticket Creation, Storage, Testing, and Documentation

## Cycle 1: Understanding Ticket Storage

**Concept gap:** Understanding how ticket creation and JSON storage
should work together.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Keep ticket validation and construction
separate from the functions that load and save ticket data.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The ticket creation and storage tests
passed, including the integration tests that create, save, and load a
ticket again.

**Final engineering decision:** The ticket module validates inputs,
calculates priority, and constructs the record; the storage module
handles persistence and ticket identifiers. The fellow worked on that
split and reviewed the integration tests.

## Cycle 2: Improving Numeric Sorting Test Coverage

**Concept gap:** Verifying that tickets with the same priority are
sorted by their numeric IDs in the work queue.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Add tests using different ticket
identifiers to check the ordering.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The fellow recognised that ordinary
sequential, zero-padded IDs could not distinguish numeric sorting from
lexicographic sorting, and used IDs such as `T999` and `T1000` instead.
The workflow test suite passed, including the numeric sorting test.

**Final engineering decision:** Improve the AI's suggestion rather than
apply it as given: the test now uses IDs whose text order differs from
their numeric order, so it fails if the implementation ever sorts as
strings. This is a recorded case of changing an AI suggestion after
evidence review.

## Cycle 3: Improving the Design Documentation

**Concept gap:** Making the design document accurately describe the
completed CampusFlow implementation.

**Exact question:** _Not recorded in the original log — to be supplied
by the fellow._

**AI guidance (summary):** Document the workflow rules, work-queue
ordering, reporting behaviour, storage decisions, and current
limitations.

**Tiny unrelated experiment:** _Not recorded — to be supplied by the
fellow._

**Independent verification:** The fellow ran `git diff --check` and the
complete test suite. All 53 tests passed at the time.

**Final engineering decision:** Update `docs/design-decisions.md` to
describe the current implementation, correct the Markdown formatting,
and remove completed work from the limitations list.

### Reflection

AI helped me identify gaps in test coverage and improve my
documentation. I learned that AI suggestions need to be evaluated
rather than accepted automatically. Improving the numeric sorting test
taught me to think about whether a test genuinely proves the intended
behaviour. I remain responsible for understanding my changes and
verifying the results.

---

# Team Reflection

AI was used as a learning and development aid during the CampusFlow
sprint. It helped us reason about module responsibilities, storage,
workflow rules, testing, and documentation.

We evaluated suggestions against the assignment requirements, reviewed
the implementation, and used automated tests to check behaviour. We
learned that AI-generated advice should not be accepted without review
and that a passing test must demonstrate the intended behaviour.

Both fellows remain responsible for understanding their contributions,
reviewing code changes, and verifying the final application.
