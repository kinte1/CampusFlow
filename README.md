# CampusFlow

CampusFlow is a Python command-line campus helpdesk ticket management system. It allows users to create and manage support tickets, assign staff, track progress, prioritize urgent issues, add follow-up notes, search tickets, and generate reports.

The application uses Python's standard library and JSON for local data persistence.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Using CampusFlow](#using-campusflow)
- [Priority Rules](#priority-rules)
- [Ticket Workflow](#ticket-workflow)
- [Search and Reports](#search-and-reports)
- [Data Storage and Validation](#data-storage-and-validation)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Team Responsibilities](#team-responsibilities)
- [Development Workflow](#development-workflow)
- [Future Improvements](#future-improvements)

## Features

CampusFlow currently supports:

- Creating tickets with unique IDs.
- Validating ticket information and calculating priority automatically.
- Listing saved tickets.
- Assigning staff to tickets.
- Starting, resolving, and reopening tickets according to workflow rules.
- Displaying an open-ticket work queue sorted by priority and numeric ticket ID.
- Generating reports with ticket totals, status counts, priority counts, category counts, unresolved tickets, and resolution percentage.
- Searching tickets by title, with optional category, status, and priority filters.
- Adding follow-up notes to eligible tickets and viewing their notes.
- Displaying search results sorted by priority and numeric ticket ID.
- Completing the Engineering Understanding Check.
- Saving and loading ticket data using JSON.
- Running automated tests with Python's built-in `unittest` framework.

## Requirements

- Python 3.10 or newer.
- Git, if cloning the repository.

CampusFlow does not require a third-party Python package for its core functionality.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/kinte1/CampusFlow.git
cd CampusFlow
```

### 2. Run the application

On Linux or macOS, run:

```bash
python3 main.py
```

If `python` is available on your system, you can also run:

```bash
python main.py
```

The application displays a menu of available operations.

## Using CampusFlow

The main menu provides the following options:

| Option | Operation | Description |
|---|---|---|
| 1 | Create ticket | Record a ticket with a title, category, urgency, and affected-user count. |
| 2 | List all tickets | Display saved tickets. |
| 3 | Assign staff | Assign a staff member to a ticket. |
| 4 | Start ticket | Move an eligible assigned ticket into progress. |
| 5 | Resolve ticket | Resolve a ticket when workflow requirements are satisfied. |
| 6 | Reopen ticket | Reopen a resolved ticket. |
| 7 | View work queue | Display open tickets in priority order. |
| 8 | View report | Display ticket statistics and resolution metrics. |
| 9 | Search tickets | Search by title with optional filters. |
| 10 | Add follow-up note | Add a note to an open or in-progress ticket. |
| 11 | View ticket notes | Display a ticket's notes in note-ID order. |
| 12 | Search results sorted by priority | Search tickets and sort matching results by priority and ticket ID. |
| 13 | Engineering Understanding Check | Answer questions to check your understanding of the project. |
| 0 | Exit | Leave the application. |

### Creating a ticket

When creating a ticket, enter:

- A non-empty title.
- A supported category: `Network`, `Hardware`, `Software`, or `Other`.
- An urgency level: `low`, `medium`, or `high`.
- A positive whole number of affected users.

Ticket IDs are generated automatically, and priority is calculated from the urgency and affected-user count.

If the affected-user input is invalid, the application displays an error and prompts for another value.

### Adding notes

Notes record follow-up information about a ticket. Each note contains:

- `note_id`
- `author`
- `message`

Notes can be added to tickets with `open` or `in_progress` status. A resolved ticket must be reopened before it can accept additional notes.

## Priority Rules

Priority is calculated automatically. The rules are evaluated from top to bottom, and the first matching rule determines the priority.

| Condition | Priority |
|---|---|
| Urgency is `high` and at least 10 users are affected | `critical` |
| Urgency is `high` or at least 10 users are affected | `high` |
| Urgency is `medium` or at least 3 users are affected | `medium` |
| None of the above conditions apply | `low` |

Examples:

| Urgency | Affected Users | Priority |
|---|---:|---|
| `high` | 12 | `critical` |
| `high` | 5 | `high` |
| `medium` | 10 | `high` |
| `medium` | 4 | `medium` |
| `low` | 2 | `low` |
| `low` | 3 | `medium` |

### Work queue ordering

The work queue includes only tickets with `open` status.

Tickets are ordered by priority:

1. Critical
2. High
3. Medium
4. Low

Tickets with the same priority are ordered by their numeric ticket ID, so `T002` appears before `T010`.

Tickets with `in_progress` or `resolved` status do not appear in the work queue.

## Ticket Workflow

Tickets support three statuses:

- `open`
- `in_progress`
- `resolved`

The workflow enforces the following rules:

- New tickets start as `open`.
- An unassigned ticket cannot move to `in_progress`.
- Tickets must follow the permitted status transitions.
- A resolved ticket must be explicitly reopened before actions requiring reopening can be performed.
- Invalid operations are rejected with an error.
- Rejected operations should not partially change the ticket data.

## Search and Reports

### Search

Search supports:

- Case-insensitive title substring matching.
- Optional category filtering.
- Optional status filtering.
- Optional priority filtering.
- Combining filters, where all supplied filters must match.
- Sorting search results by priority and numeric ticket ID through the corresponding menu option.

### Reports

Reports include ticket totals and summaries by:

- Status.
- Priority.
- Category.

They also report unresolved tickets and the resolution percentage. When there are no tickets, the resolution percentage is zero.

## Data Storage and Validation

CampusFlow stores ticket data in:

```text
data/tickets.json
```

If the file does not exist, the application starts with an empty ticket collection.

### Ticket data format

The file contains a JSON list of ticket objects. A ticket uses the following fields:

| Field | Type | Description |
|---|---|---|
| `id` | String | Unique identifier, such as `T001`. |
| `title` | String | Non-empty ticket title. |
| `category` | String | `Network`, `Hardware`, `Software`, or `Other`. |
| `urgency` | String | `low`, `medium`, or `high`. |
| `affected_users` | Integer | Positive whole number; booleans are rejected. |
| `priority` | String | Calculated priority: `critical`, `high`, `medium`, or `low`. |
| `status` | String | `open`, `in_progress`, or `resolved`. |
| `assigned_to` | String or null | Staff member assigned to the ticket, when applicable. |
| `notes` | List | Follow-up notes containing `note_id`, `author`, and `message`. |

### Storage validation

The application validates ticket data when loading and saving.

- Malformed JSON and invalid ticket records are rejected.
- Duplicate ticket IDs are rejected.
- Invalid or inconsistent priority values are rejected.
- Tickets in progress or resolved must satisfy assignment requirements.
- Malformed notes and duplicate note IDs within a ticket are rejected.
- A rejected load must not silently discard or overwrite existing data.
- A rejected save must leave the existing data file untouched.
- Ticket and note ID sequences are derived from saved records so IDs continue correctly after reloading.

Older data files that do not contain the `notes` field are supported. The application treats missing notes as an empty list and writes the current format on a subsequent save.

## Project Structure

```text
CampusFlow/
├── README.md
├── main.py
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   ├── validation.py
│   ├── storage.py
│   ├── workflow.py
│   ├── notes.py
│   ├── search.py
│   ├── reports.py
│   └── understanding_check.py
├── tests/
│   ├── test_tickets.py
│   ├── test_validation.py
│   ├── test_storage.py
│   ├── test_workflow.py
│   ├── test_notes.py
│   ├── test_search.py
│   ├── test_reports.py
│   └── test_understanding_check.py
├── docs/
│   ├── ai-learning-log.md
│   ├── baseline-check.md
│   └── design-decisions.md
└── data/
    └── tickets.json
```

This structure describes the main application components. The exact files present in the repository may change as the project evolves.

## Testing

CampusFlow uses Python's built-in `unittest` framework.

From the project root, run the full test suite:

```bash
python3 -m unittest discover -s tests -v
```

You can also use `python` instead of `python3` if that command is available on your system.

The tests cover ticket creation, validation, priority calculation, storage, workflow transitions, notes, search, reports, and the Engineering Understanding Check.

## Team Responsibilities

CampusFlow is developed collaboratively by two engineers.

### Engineer A — Ticket Creation, Validation, and Storage

Primary responsibilities include:

- Ticket creation and ID generation.
- Ticket validation and priority calculation.
- JSON persistence and storage error handling.
- Related automated tests and design decisions.

### Engineer B — Workflow, Search, Reports, and Interface

Primary responsibilities include:

- Staff assignment and ticket workflow.
- Reopening tickets and managing the open work queue.
- Search and filtering.
- Reports and statistics.
- Command-line interface and the Engineering Understanding Check.
- Related automated tests and usage documentation.

### Shared responsibilities

Both engineers contribute to integration, testing, documentation, code review, and maintaining readable, reliable code.

## Development Workflow

The team uses Git and GitHub for version control and collaboration.

Recommended workflow:

1. Update the local `main` branch.
2. Create a dedicated branch for a task.
3. Make focused changes and add relevant tests.
4. Run the full test suite.
5. Commit and push the changes.
6. Open a pull request for review.
7. Address feedback and merge after approval.

Example commands:

```bash
git switch main
git pull
git switch -c feature/your-task
```

Use a descriptive branch name that matches the actual task.

Before committing, check which files have changed:

```bash
git status
```

Stage only the files intended for the commit, then commit with a clear message.

## Future Improvements

Potential future extensions include:

- A graphical or web-based interface.
- Database-backed storage.
- Authentication and role-based access control.
- Notifications for important ticket updates.
- Exportable reports.
- Additional integration tests.

These are possible future extensions, not requirements for the current command-line application.

## License

A license has not yet been selected. Licensing information can be added when the project maintainers agree on the appropriate license.