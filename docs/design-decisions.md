# CampusFlow — Design Decisions

## 1. Project Overview

CampusFlow is a campus support-ticket system designed to help users
report technical problems, prioritize requests, and track their progress.

## 2. Ticket Structure

Each ticket contains:

- `id`: Unique ticket identifier, such as T001.
- `title`: Short description of the problem.
- `category`: Network, Hardware, Software, or Other.
- `urgency`: Low, medium, or high.
- `affected_users`: Positive integer representing the number of users affected.
- `priority`: Calculated severity level.
- `status`: Initially open.
- `assigned_to`: Initially None.

## 3. Input Validation

Ticket inputs are validated before a ticket is created.

Titles cannot be empty. Categories and urgency levels must belong
to the supported options. The affected-user count must be a positive
integer; Boolean values are rejected.

Valid text inputs are normalized to consistent formats.

## 4. Priority Calculation

Priority follows these rules, in order:

1. High urgency and at least 10 affected users: critical.
2. High urgency or at least 10 affected users: high.
3. Medium urgency or at least 3 affected users: medium.
4. Otherwise: low.

The first matching rule determines the priority.

## 5. Data Storage

Tickets are stored in `data/tickets.json` as a JSON list.

JSON was selected because it is human-readable and supported by
Python's standard library. It is suitable for this project's initial
command-line implementation.

If the storage file does not exist, loading starts with an empty list.
Malformed JSON raises an error rather than silently discarding data.

Saving uses a temporary file before replacing the destination to
reduce the risk of leaving partially written data.

## 6. Ticket Identifiers

Ticket IDs use the format T001, T002, T003, and so on.

The generator selects the next number after the highest recognized
existing ID. This helps avoid reusing IDs when lower-numbered tickets
have been deleted.

## 7. Automated Testing

The project uses Python's built-in `unittest` framework.

Tests cover validation, priority calculations, ticket creation,
JSON persistence, malformed JSON, and ticket ID generation.

Integration tests verify that created tickets are saved and can
be loaded again.

## 8. Current Limitations

- JSON storage is intended for a small, local application.
- Concurrent writes are not protected by a locking mechanism.
- Authentication and role-based access control are not implemented.
- Workflow, reporting, and command-line integration require their
  own implementation and testing.
