# CampusFlow — Design Decisions

## 1. Project Overview

CampusFlow is a campus support-ticket system designed to help users
report technical problems, prioritize requests, and track their progress.

The application uses a command-line interface (CLI) built with Python.
It allows users to create tickets, assign staff, manage ticket statuses,
view the work queue, and generate reports.

## 2. Ticket Structure

Each ticket contains the following fields:

- `id`: Unique ticket identifier, such as T001.
- `title`: Short description of the technical problem.
- `category`: Network, Hardware, Software, or Other.
- `urgency`: Low, medium, or high.
- `affected_users`: Positive integer representing the number of users affected.
- `priority`: Calculated severity level.
- `status`: Current ticket status, initially `open`.
- `assigned_to`: Staff member responsible for the ticket, initially `None`.

Ticket IDs are generated automatically to help ensure that every ticket
can be identified separately.

## 3. Input Validation

Ticket inputs are validated before a ticket is created.

The application checks that:

- The ticket title is not empty.
- The category belongs to the supported options.
- The urgency level is valid.
- The number of affected users is a positive integer.
- The ticket ID is unique.

Boolean values are rejected when validating the affected-user count,
because Python treats Boolean values as a special type of integer.

Valid text inputs are normalized to consistent formats where appropriate.
This helps prevent invalid data from entering the system.

## 4. Priority Calculation

Ticket priority is calculated using the urgency level and the number
of affected users.

The rules are checked in the following order:

1. If urgency is high and at least 10 users are affected, priority is `critical`.
2. If urgency is high or at least 10 users are affected, priority is `high`.
3. If urgency is medium or at least 3 users are affected, priority is `medium`.
4. Otherwise, priority is `low`.

The first matching rule determines the priority.

The order matters because a ticket may satisfy more than one condition.
For example, a high-urgency ticket affecting 12 users must be classified
as critical rather than high.

## 5. Data Storage

Tickets are stored in `data/tickets.json` as a JSON list.

JSON was selected because it is human-readable and supported by Python's
standard library. It provides a straightforward way to save and reload
ticket information without requiring an external database.

The storage system follows these rules:

- If the storage file does not exist, the application starts with an empty
  ticket list.
- Existing tickets are loaded from the JSON file.
- Malformed JSON raises an error rather than silently discarding data.
- Saving uses a temporary file before replacing the destination to reduce
  the risk of leaving partially written data.

The file `data/tickets.json` is excluded from Git so that locally generated
ticket data is not accidentally committed to the repository.

## 6. Ticket Identifiers

Ticket IDs use the format `T001`, `T002`, `T003`, and so on.

The identifier generator checks existing ticket IDs and selects the next
number after the highest recognized ID.

This approach helps prevent an existing ticket ID from being reused when
lower-numbered tickets have been deleted.

Ticket IDs also provide a consistent way to reference tickets when
assigning staff, changing statuses, and viewing ticket information.

## 7. Automated Testing

The project uses Python's built-in `unittest` framework.

Automated tests help verify that individual features behave as expected
and that changes do not break existing functionality.

Tests cover areas such as:

- Input validation.
- Priority calculations.
- Ticket creation.
- Ticket identifier generation.
- JSON persistence.
- Handling malformed JSON.
- Ticket assignment and workflow transitions.
- Work-queue ordering.
- Report generation.

Integration tests also verify that ticket creation and storage work
together correctly.

The test suite can be run with:

`python -m unittest discover -s tests -v`

## 8. Ticket Workflow

Tickets follow a defined workflow to ensure that their status changes
occur in the correct order.

The supported statuses are:

- `open`: The ticket has been created but is not currently being processed.
- `in_progress`: A staff member has been assigned and work has started.
- `resolved`: The reported problem has been addressed.

The workflow follows these rules:

- New tickets start with the `open` status.
- A ticket must be assigned to a staff member before it can move to
  `in_progress`.
- An in-progress ticket can move to `resolved`.
- A resolved ticket must be explicitly reopened before it can be modified
  or processed again.

These restrictions help maintain a consistent ticket lifecycle and prevent
invalid status transitions.

## 9. Work Queue and Reports

The work queue displays unresolved tickets in priority order:

1. Critical
2. High
3. Medium
4. Low

Tickets with the same priority are sorted by their numeric ticket ID.
Numeric sorting ensures that ticket identifiers are ordered by their
numbers rather than by their text representation.

The reporting feature summarizes the current state of the system.

Reports include:

- The total number of tickets.
- The number of tickets in each status.
- The number of tickets in each priority category.

Status and priority categories are included even when their counts are zero.
This makes the reports consistent and easier to interpret.

## 10. Current Limitations

CampusFlow meets the requirements of a small command-line support-ticket
application, but some limitations remain:

- JSON storage is intended for a small, local application rather than
  a large system with many simultaneous users.
- Concurrent writes are not protected by a locking mechanism.
- Authentication and role-based access control are not implemented.
- The application does not provide a graphical user interface.
- The system does not currently provide a full production deployment
  environment or multi-user access controls.

These limitations could be addressed in future versions if the project
were expanded beyond its current scope.

## 11. Conclusion

CampusFlow was designed with simplicity, maintainability, and correctness
in mind.

Separating ticket operations, workflow management, storage, reporting,
and command-line interaction helps keep the code organized and easier
to test.

The project also demonstrates the importance of validating inputs,
preserving data, enforcing workflow rules, and using automated tests
to check expected behavior.