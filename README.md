# CampusFlow

CampusFlow is a Python command-line campus helpdesk ticket management system. It helps users report problems, assign tickets to staff, track progress, prioritize urgent issues, and generate reports.

The project is being developed collaboratively by two engineers using Python, Git, and GitHub.

## Table of Contents

- [Project Overview](#project-overview)
- [Project Goals](#project-goals)
- [Planned Features](#planned-features)
- [Priority Rules](#priority-rules)
- [Validation Rules](#validation-rules)
- [Team Responsibilities](#team-responsibilities)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development Setup](#development-setup)
- [Testing](#testing)
- [Collaboration Workflow](#collaboration-workflow)
- [Project Status](#project-status)
- [Future Improvements](#future-improvements)

## Project Overview

CampusFlow is designed to make campus helpdesk operations easier to manage.

Students and other campus users often experience problems involving network connectivity, hardware, software, and other services. CampusFlow will provide a structured way to record these problems, prioritize them, assign staff members, and track their resolution.

The application will use JSON for local data persistence and Python's built-in `unittest` framework for automated testing.

## Project Goals

The main goals are to:

- Provide a simple and reliable ticket management system.
- Validate user input before creating tickets.
- Calculate ticket priorities automatically.
- Generate unique ticket identifiers.
- Assign tickets to staff members.
- Enforce valid ticket status transitions.
- Organize open tickets into a priority-based work queue.
- Save and load tickets using JSON.
- Generate useful reports and statistics.
- Maintain readable, modular, and testable Python code.
- Support effective collaboration through Git and GitHub.

## Planned Features

### 1. Ticket Creation

The application will:

- Create tickets with unique identifiers, such as `T001`, `T002`, and `T003`.
- Store the ticket title, category, urgency, affected-user count, priority, status, and assigned staff member.
- Validate input before creating a ticket.
- Calculate priority automatically.
- Prevent duplicate ticket identifiers.

### 2. Ticket Management

The application will allow users to:

- View all tickets.
- View the details of an individual ticket.
- Identify tickets by their unique IDs.
- Track the status and priority of each ticket.

### 3. Staff Assignment

The application will support:

- Assigning tickets to staff members.
- Tracking the staff member responsible for each ticket.
- Preventing invalid assignment and workflow operations.

### 4. Ticket Status Management

Tickets will support the following statuses:

- `open`
- `in_progress`
- `resolved`

The workflow will follow these rules:

- Newly created tickets will start with the `open` status.
- An unassigned ticket cannot move to `in_progress`.
- A ticket can be marked as `resolved` when the appropriate workflow conditions are satisfied.
- A resolved ticket must be explicitly reopened before it can be modified in ways that require reopening.
- Invalid status transitions will produce clear errors.

### 5. Priority-Based Work Queue

The application provides a work queue containing only tickets with an
`open` status that are awaiting work.

Tickets are sorted using the following priority order:

1. Critical priority.
2. High priority.
3. Medium priority.
4. Low priority.

When two tickets have the same priority, the ticket with the lower
numeric ID appears first.

For example, `T002` appears before `T005` when both tickets have
the same priority.

Tickets with `in_progress` or `resolved` status do not appear in
the work queue.

### 6. Reports and Statistics

The reporting module will provide useful information, including:

- Total number of tickets.
- Number of open tickets.
- Number of tickets in progress.
- Number of resolved tickets.
- Number of tickets in each priority category.
- Other useful summaries of helpdesk activity.

### 7. JSON Data Persistence

The application will save ticket information in JSON format.

The storage module will:

- Save tickets to a local JSON file.
- Load previously saved tickets when the application starts.
- Start with an empty collection if the data file does not exist.
- Preserve ticket identifiers across application restarts.
- Detect malformed JSON and report a clear error.
- Avoid silently discarding or overwriting corrupted data.

### 8. Automated Testing

The project will include automated tests for:

- Ticket creation and validation.
- Priority calculation.
- Unique ticket identifiers.
- JSON saving and loading.
- Storage error handling.
- Staff assignment.
- Ticket status transitions.
- Ticket reopening.
- Priority-based queue sorting.
- Reports and application integration.

## Priority Rules

Ticket priority will be calculated automatically using the following rules, in order:

| Condition | Priority |
|---|---|
| Urgency is high AND at least 10 users are affected | Critical |
| Urgency is high OR at least 10 users are affected | High |
| Urgency is medium OR at least 3 users are affected | Medium |
| None of the above conditions apply | Low |

**Important:** The rules are evaluated from top to bottom. The first matching rule determines the ticket's priority.

For example:

| Urgency | Affected Users | Priority |
|---|---:|---|
| High | 12 | Critical |
| High | 5 | High |
| Medium | 10 | High |
| Medium | 4 | Medium |
| Low | 2 | Low |
| Low | 3 | Medium |

## Validation Rules

Tickets must satisfy the following requirements.

### Ticket Title

- The title must not be blank.
- Leading and trailing whitespace should not make an otherwise empty title valid.

### Category

Supported categories are:

- `Network`
- `Hardware`
- `Software`
- `Other`

### Urgency

Supported urgency levels are:

- `low`
- `medium`
- `high`

### Affected Users

- The affected-user count must be a positive integer.
- Zero and negative values are invalid.
- Boolean values must not be accepted as integers.

### Ticket Identifier

- Every ticket must have a unique identifier.
- Identifiers will follow a format such as `T001`, `T002`, and `T003`.
- Existing identifiers must be considered when new tickets are created after loading saved data.

### Ticket Status

Supported statuses are:

- `open`
- `in_progress`
- `resolved`

Invalid statuses and prohibited transitions must be rejected with clear errors.

## Team Responsibilities

The project is divided between two engineers to support parallel development.

Each engineer owns specific modules and tests while both remain responsible for integration, documentation, code quality, and successful delivery.

### Engineer A — Ticket Creation, Validation, and Storage

**Primary responsibility:** Implement ticket creation, input validation, priority calculation, and JSON persistence.

#### Assigned Files

**`campusflow/tickets.py`**

Responsibilities:

- Create tickets.
- Generate unique ticket IDs.
- Validate ticket information.
- Calculate ticket priorities.
- Maintain the agreed ticket data structure.

**`tests/test_tickets.py`**

Responsibilities:

- Test ticket creation.
- Test input validation.
- Test priority calculation.
- Test unique ID generation.
- Test relevant edge cases.

**`campusflow/storage.py`**

Responsibilities:

- Save tickets to JSON.
- Load tickets from JSON.
- Handle missing data files.
- Report malformed JSON clearly.
- Preserve ticket data across application restarts.

**`tests/test_storage.py`**

Responsibilities:

- Test JSON saving and loading.
- Test behavior when the data file is missing.
- Test malformed JSON handling.
- Verify that saved data can be loaded correctly.

**`docs/design-decisions.md`**

Responsibilities:

- Document important technical decisions.
- Explain the ticket data structure.
- Record decisions about persistence and validation.
- Document relevant trade-offs and their reasoning.

### Engineer B — Workflow, Assignment, Reports, and Interface

**Primary responsibility:** Implement ticket workflows, staff assignment, queue management, reporting, and the command-line interface.

#### Assigned Files

**`campusflow/workflow.py`**

Responsibilities:

- Assign tickets to staff members.
- Manage ticket status transitions.
- Enforce workflow rules.
- Support explicit reopening of resolved tickets.
- Build the open ticket queue.
- Sort tickets by priority and numeric ticket ID.

**`tests/test_workflow.py`**

Responsibilities:

- Test staff assignment.
- Test valid and invalid status transitions.
- Test reopening behavior.
- Test open-ticket queue filtering.
- Test queue sorting and tie-breaking.

**`campusflow/reports.py`**

Responsibilities:

- Generate ticket summaries.
- Calculate status statistics.
- Summarize ticket priorities.
- Provide useful helpdesk reports.

**`main.py`**

Responsibilities:

- Provide the command-line interface.
- Accept user commands and input.
- Connect the ticket, workflow, storage, and reporting modules.
- Display useful results and error messages.
- Make the application straightforward to use.

**README usage instructions**

Responsibilities:

- Add practical usage instructions as the application becomes runnable.
- Document supported commands.
- Provide examples of common operations.
- Keep the documentation consistent with the actual implementation.

### Shared Responsibilities

Both engineers will:

- Agree on function names, parameters, return values, and error-handling conventions before integration.
- Agree on the ticket data structure used across modules.
- Write automated tests for their contributions.
- Keep code modular, readable, and maintainable.
- Integrate their modules and resolve compatibility issues.
- Run the full test suite before merging changes.
- Review each other's pull requests.
- Provide constructive feedback.
- Update documentation when behavior changes.
- Record relevant AI assistance and learning outcomes in `docs/ai-learning-log.md`.
- Verify that the completed application meets the project requirements.

File ownership identifies the primary implementer. It does not prevent the other engineer from reviewing, testing, or helping improve a feature.

## Project Structure

The planned project structure is:

```text
CampusFlow/
├── README.md
├── .gitignore
├── main.py
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   ├── workflow.py
│   ├── storage.py
│   └── reports.py
├── tests/
│   ├── test_tickets.py
│   ├── test_workflow.py
│   └── test_storage.py
└── docs/
    ├── ai-learning-log.md
    └── design-decisions.md
```

This is the planned structure. Files and features will be added as development progresses.

### File Ownership Summary

| File | Primary Owner | Purpose |
|---|---|---|
| `campusflow/tickets.py` | Engineer A | Ticket creation, validation, and priorities |
| `tests/test_tickets.py` | Engineer A | Ticket creation and validation tests |
| `campusflow/storage.py` | Engineer A | JSON persistence |
| `tests/test_storage.py` | Engineer A | Storage tests |
| `docs/design-decisions.md` | Engineer A | Technical decisions |
| `campusflow/workflow.py` | Engineer B | Assignment, lifecycle, and queue |
| `tests/test_workflow.py` | Engineer B | Workflow and queue tests |
| `campusflow/reports.py` | Engineer B | Reports and statistics |
| `main.py` | Engineer B | Command-line interface |
| `README.md` | Shared, with Engineer B leading usage instructions | Project documentation |
| `docs/ai-learning-log.md` | Shared | AI assistance and learning record |

## Technology Stack

The project uses the following technologies:

- **Python 3.12+:** Main programming language.
- **JSON:** Local data persistence.
- **Git:** Version control.
- **GitHub:** Remote repository, collaboration, and pull requests.
- **`unittest`:** Automated testing using Python's standard library.
- **Virtual environment (`venv`):** Dependency and environment isolation.

The initial implementation is intended to use Python's standard library wherever practical.

## Development Setup

### Prerequisites

Install Python 3.12 or a compatible newer version, Git, and a terminal.

### 1. Clone the Repository

```bash
git clone https://github.com/kinte1/CampusFlow.git
cd CampusFlow
```

### 2. Create a Virtual Environment

On Linux or macOS:

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

```bash
source .venv/bin/activate
```

### 4. Check the Python Version

```bash
python --version
```

### 5. Run the Application

The application is still under development. Once `main.py` and the required modules have been implemented, the exact startup command and available operations will be documented here.

## Testing

The project will use Python's built-in `unittest` framework.

To run an individual test module after it has been created:

```bash
python -m unittest tests.test_tickets -v
```

To run the workflow tests:

```bash
python -m unittest tests.test_workflow -v
```

To run the storage tests:

```bash
python -m unittest tests.test_storage -v
```

To discover and run all available tests:

```bash
python -m unittest discover -s tests -v
```

Tests will be added as features are implemented. Test commands may need adjustment if the final test package structure changes.

## Collaboration Workflow

The team will use Git and GitHub to coordinate development and protect the main branch.

### 1. Keep the Main Branch Stable

The `main` branch should contain integrated work that has been reviewed and tested.

### 2. Create a Branch for Each Task

Each engineer should create a separate branch for their work.

For example, Engineer A might use:

```bash
git switch -c feature/ticket-creation
```

Engineer B might use:

```bash
git switch -c feature/workflow
```

Use a descriptive branch name that matches the task being implemented.

### 3. Commit Changes Regularly

Use clear commit messages describing what changed.

Examples:

```bash
git add .
git commit -m "feat: implement ticket validation"
```

```bash
git commit -m "test: add workflow tests"
```

Only stage files that belong in the commit. Do not commit virtual environments, secrets, or generated local data.

### 4. Push the Branch to GitHub

```bash
git push -u origin feature/ticket-creation
```

Replace `feature/ticket-creation` with the actual name of your branch.

### 5. Open a Pull Request

Open a pull request on GitHub to propose merging the branch into `main`.

The pull request should explain:

- What was implemented.
- Which files were changed.
- Which tests were run.
- Any known limitations.
- Any decisions that the other engineer should review.

### 6. Review and Test

The other engineer should review the changes, check the tests, and request corrections when necessary.

Resolve feedback before merging.

### 7. Integrate the Changes

After approval and successful tests, merge the pull request into `main`.

Both engineers should update their local `main` branch before starting work that depends on the latest integration.

### 8. Communicate Shared Interfaces

Before integrating modules, agree on how the modules will communicate.

For example, both engineers should agree on:

- The ticket dictionary structure.
- Function names and parameters.
- Expected return values.
- Error handling.
- How ticket IDs are generated and preserved.
- How the storage module receives and returns ticket data.

This agreement will reduce integration conflicts and duplicated work.

## Project Status

**Current stage:** Initial project setup and planning.

### Completed

- Git repository initialized.
- Initial project files created.
- GitHub remote repository configured.
- Initial project commit pushed to GitHub.
- Feature requirements and priority rules documented.
- Initial division of engineering responsibilities defined.

### Planned

- Implement ticket creation and validation.
- Implement automatic priority calculation.
- Implement JSON persistence.
- Implement staff assignment and ticket lifecycle management.
- Implement the open work queue.
- Implement reports and statistics.
- Build the command-line interface.
- Write and run automated tests.
- Integrate both engineers' contributions.
- Review and verify the completed application.

A feature should only be marked as completed after its implementation has been reviewed and tested.

## Future Improvements

Possible future improvements include:

- A graphical user interface.
- A web-based interface.
- A database-backed storage option.
- User authentication and role-based access control.
- Ticket search and filtering.
- Ticket activity history.
- Notifications for important ticket updates.
- Exportable reports.
- More comprehensive integration testing.

These improvements are potential extensions, not promises for the initial version.

## Contribution Guidelines

Contributors should:

1. Work on a dedicated branch.
2. Follow the agreed module responsibilities.
3. Write tests for new functionality.
4. Keep commits focused and descriptive.
5. Update documentation when necessary.
6. Open pull requests for review.
7. Avoid committing secrets, virtual environments, or local generated data.
8. Explain any AI-assisted work and verify its correctness.

## License

A license has not yet been selected. Licensing information will be added once the project maintainers agree on the appropriate license.

## Running CampusFlow

CampusFlow is a Python command-line application for managing campus technical support tickets. It uses the Python standard library and stores tickets in a JSON file.

### Requirements

- Python 3.10 or newer
- Git

### Start the application

From the project root, run:

```bash
python main.py
```

### Available operations

The menu allows users to:

1. Create a ticket with a title, category, urgency, and affected-user count.
2. List all saved tickets.
3. Assign a staff member to a ticket.
4. Start work on an assigned ticket.
5. Resolve a ticket.
6. Reopen a resolved ticket.
7. View the open work queue, sorted by priority and ticket ID.
8. View totals, counts by status, priority and category, and the resolution percentage.
9. Search tickets by title substring, with optional category, status and priority filters.
10. Add a follow-up note to an open or in-progress ticket.
11. View a ticket's notes in note-ID order.
12. Search tickets and display the results sorted by priority, then ticket ID.
13. Take the Engineering Understanding Check.

Tickets are saved in `data/tickets.json`. If the file does not exist, the application starts with an empty ticket list.

## JSON Data Format

`data/tickets.json` contains a JSON list. Each element is a ticket object.

### Version 2 (current)

| Field | Type | Notes |
|---|---|---|
| `id` | string | `T001`, `T002`, ... unique |
| `title` | string | non-empty after trimming |
| `category` | string | `Network`, `Hardware`, `Software` or `Other` |
| `urgency` | string | `low`, `medium` or `high` |
| `affected_users` | integer | strictly positive; booleans rejected |
| `priority` | string | `critical`, `high`, `medium` or `low`, derived from urgency and affected users |
| `status` | string | `open`, `in_progress` or `resolved` |
| `assigned_to` | string or null | required once a ticket is `in_progress` or `resolved` |
| `notes` | list | each note is `{"note_id", "author", "message"}` |

Example:

```json
[
    {
        "id": "T001",
        "title": "Wi-Fi is not working",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": null,
        "notes": [
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "Router rebooted"
            }
        ]
    }
]
```

### Version 1 (legacy)

Version 1 files contain the same fields **except `notes`**. Loading a v1
record is supported: it is read as `notes: []` in memory. That migration
is in memory only — the file keeps its old shape until the next save,
which writes the v2 form. No source data is discarded.

### Validation on load and save

- A missing file means an empty collection.
- Malformed JSON, a non-list document, a missing field, an unknown
  category/urgency/status, an inconsistent priority, an unassigned
  in-progress or resolved ticket, a duplicate ticket ID, a malformed
  `notes` value, or duplicate note IDs within one ticket all cause the
  load to be refused.
- A refused load changes neither the file nor any in-memory collection.
- `save_tickets()` validates every record before it creates a directory
  or writes a temporary file, and writes the normalised records. A
  refused save leaves the existing file untouched.
- Ticket and note IDs are derived from the records on disk, so a reload
  does not reset either sequence.

### Run tests

From a fresh clone, run:

```bash
python -m unittest discover -s tests -v
```

On systems where `python` is not on `PATH`, use `python3`.

The test suite covers ticket validation, priority calculation, JSON
persistence, workflow rules, notes, search, reporting and the
understanding check.
