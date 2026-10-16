"""Centralised validation and ticket rules.

Every public function in this module either returns a normalised value or
raises ValueError. Nothing here performs file I/O or mutates shared state,
so the whole module can be tested without touching the file system.

Import direction: this module imports nothing from the rest of campusflow.
That keeps it free of circular imports and makes it safe for any other
module to depend on.
"""

import re


CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")
STATUSES = ("open", "in_progress", "resolved")

# Statuses in which a follow-up note may be added.
NOTE_STATUSES = ("open", "in_progress")

PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}

PRIORITIES = tuple(PRIORITY_ORDER)

TICKET_ID_PATTERN = r"T\d{3,}"
NOTE_ID_PATTERN = r"N\d{3,}"

NOTE_MIN_LENGTH = 5
NOTE_MAX_LENGTH = 300

TICKET_FIELDS = frozenset(
    {
        "id",
        "title",
        "category",
        "urgency",
        "affected_users",
        "priority",
        "status",
        "assigned_to",
    }
)

NOTE_FIELDS = frozenset({"note_id", "author", "message"})

# The status graph, and nothing else. Whether a ticket is *allowed* to make a
# transition is separate from whether the ticket is in a valid state to do so
# (for example, an open ticket must be assigned before it can start).
ALLOWED_TRANSITIONS = {
    "open": frozenset({"in_progress"}),
    "in_progress": frozenset({"resolved"}),
    "resolved": frozenset({"open"}),
}

# Statuses a ticket can only reach by being assigned, mapped to the wording
# used in the error message. A ticket must be assigned before it can start,
# and only in-progress tickets can be resolved, so both of these imply an
# assignee. A stored record missing one is malformed even though it loads.
ASSIGNED_STATUS_LABELS = {
    "in_progress": "an in-progress",
    "resolved": "a resolved",
}


def validate_title(title):
    """Return the trimmed title, or raise if it is not usable text."""
    if not isinstance(title, str):
        raise ValueError("Ticket title must be text.")

    title = title.strip()

    if not title:
        raise ValueError("Ticket title cannot be empty.")

    return title


def validate_category(category):
    """Return the canonical category name, or raise if it is not supported."""
    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    category = category.strip().title()

    if category not in CATEGORIES:
        raise ValueError(
            f"Invalid category. Choose one of: "
            f"{', '.join(sorted(CATEGORIES))}."
        )

    return category


def validate_urgency(urgency):
    """Return the lower-cased urgency, or raise if it is not supported."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    urgency = urgency.strip().lower()

    if urgency not in URGENCIES:
        raise ValueError(
            "Invalid urgency. Choose one of: high, low, medium."
        )

    return urgency


def validate_affected_users(affected_users):
    """Return the affected-user count, or raise if it is not a positive int.

    bool is rejected explicitly: isinstance(True, int) is True because bool
    subclasses int, so a plain isinstance check would accept True as 1.
    """
    if isinstance(affected_users, bool) or not isinstance(
        affected_users, int
    ):
        raise ValueError("Affected users must be a positive integer.")

    if affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    return affected_users


def validate_ticket_id(ticket_id):
    """Return the trimmed ticket ID, or raise if it is not T + 3+ digits."""
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text.")

    ticket_id = ticket_id.strip()

    if not re.fullmatch(TICKET_ID_PATTERN, ticket_id):
        raise ValueError(
            "Ticket ID must start with T followed by at least three digits."
        )

    return ticket_id


def validate_status(status):
    """Return the status, or raise if it is not one of the legal values."""
    if not isinstance(status, str):
        raise ValueError("Status must be text.")

    status = status.strip().lower()

    if status not in STATUSES:
        raise ValueError(
            f"Invalid status. Choose one of: {', '.join(STATUSES)}."
        )

    return status


def validate_priority(priority):
    """Return the priority, or raise if it is not a legal value."""
    if not isinstance(priority, str):
        raise ValueError("Priority must be text.")

    priority = priority.strip().lower()

    if priority not in PRIORITY_ORDER:
        raise ValueError(
            f"Invalid priority. Choose one of: {', '.join(PRIORITIES)}."
        )

    return priority


def validate_assigned_to(assigned_to):
    """Return the assignee, or raise if it is neither None nor a label."""
    if assigned_to is None:
        return None

    if not isinstance(assigned_to, str) or not assigned_to.strip():
        raise ValueError(
            "Assigned staff must be None or a non-empty name."
        )

    return assigned_to.strip()


def validate_author(author):
    """Return the trimmed note author, or raise if it is blank."""
    if not isinstance(author, str):
        raise ValueError("Note author must be text.")

    author = author.strip()

    if not author:
        raise ValueError("Note author cannot be empty.")

    return author


def validate_message(message):
    """Return the trimmed note message, or raise if it has a bad length."""
    if not isinstance(message, str):
        raise ValueError("Note message must be text.")

    message = message.strip()

    if not (NOTE_MIN_LENGTH <= len(message) <= NOTE_MAX_LENGTH):
        raise ValueError(
            f"Note message must be between {NOTE_MIN_LENGTH} and "
            f"{NOTE_MAX_LENGTH} characters."
        )

    return message


def validate_note_id(note_id):
    """Return the trimmed note ID, or raise if it is not N + 3+ digits."""
    if not isinstance(note_id, str):
        raise ValueError("Note ID must be text.")

    note_id = note_id.strip()

    if not re.fullmatch(NOTE_ID_PATTERN, note_id):
        raise ValueError(
            "Note ID must start with N followed by at least three digits."
        )

    return note_id


def calculate_priority(urgency, affected_users):
    """Calculate ticket priority from urgency and affected-user count.

    Lives here rather than in tickets.py because validate_ticket has to check
    a stored priority against the rule, and this module must not import from
    the rest of campusflow.
    """
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def can_transition(current, new):
    """Return True if the status graph permits current -> new.

    Pure predicate: it answers a question and changes nothing. It does not
    raise, because "no" is a normal answer here. Callers that need to reject
    an invalid transition should raise themselves, using the reason they
    have access to.

    Anything that is not a string is not a status, so it answers False rather
    than raising. That check has to come first: a list or dict is unhashable,
    and the dictionary lookup below would raise TypeError on it.
    """
    if not isinstance(current, str) or not isinstance(new, str):
        return False

    if current not in ALLOWED_TRANSITIONS:
        return False

    if new not in STATUSES:
        return False

    return new in ALLOWED_TRANSITIONS[current]


def _label(ticket):
    """Describe a ticket for an error message, by ID where possible."""
    if isinstance(ticket, dict):
        ticket_id = ticket.get("id")

        if isinstance(ticket_id, str) and ticket_id.strip():
            return f"Ticket {ticket_id.strip()}"

    return "Ticket"


def validate_notes(notes, label="Ticket"):
    """Return a normalised note list, or raise if the shape is wrong."""
    if not isinstance(notes, list):
        raise ValueError(f"{label}: notes must be a list.")

    seen_ids = set()
    normalised = []

    for position, note in enumerate(notes):
        if not isinstance(note, dict):
            raise ValueError(
                f"{label}: note at position {position} must be a dictionary."
            )

        missing = NOTE_FIELDS - note.keys()

        if missing:
            raise ValueError(
                f"{label}: note at position {position} is missing fields "
                f"{sorted(missing)}."
            )

        note_id = validate_note_id(note["note_id"])

        if note_id in seen_ids:
            raise ValueError(f"{label}: duplicate note ID {note_id}.")

        seen_ids.add(note_id)

        normalised.append(
            {
                "note_id": note_id,
                "author": validate_author(note["author"]),
                "message": validate_message(note["message"]),
            }
        )

    return normalised


def validate_ticket(ticket):
    """Validate a complete ticket record and return a normalised copy.

    The input dictionary is never mutated. Raises ValueError describing the
    first problem found.

    The returned copy always contains a "notes" key, even when the input did
    not (older files predate the field). That is the documented migration
    path: a legacy record loads and is normalised rather than rejected.
    """
    if not isinstance(ticket, dict):
        raise ValueError("Each ticket must be a dictionary.")

    label = _label(ticket)

    missing = TICKET_FIELDS - ticket.keys()

    if missing:
        raise ValueError(f"{label}: missing fields {sorted(missing)}.")

    try:
        ticket_id = validate_ticket_id(ticket["id"])
        title = validate_title(ticket["title"])
        category = validate_category(ticket["category"])
        urgency = validate_urgency(ticket["urgency"])
        affected_users = validate_affected_users(ticket["affected_users"])
        status = validate_status(ticket["status"])
        priority = validate_priority(ticket["priority"])
        assigned_to = validate_assigned_to(ticket["assigned_to"])
    except ValueError as error:
        # Re-raise with the ticket identified, so a 200-record file points at
        # the offending record rather than an anonymous field name.
        raise ValueError(f"{label}: {error}") from error

    expected_priority = calculate_priority(urgency, affected_users)

    if priority != expected_priority:
        raise ValueError(
            f"{label}: priority does not match the ticket details "
            f"(stored {priority!r}, expected {expected_priority!r})."
        )

    if assigned_to is None and status in ASSIGNED_STATUS_LABELS:
        raise ValueError(
            f"{label}: {ASSIGNED_STATUS_LABELS[status]} ticket must be "
            "assigned."
        )

    notes = validate_notes(ticket.get("notes", []), label)

    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
        "notes": notes,
    }
