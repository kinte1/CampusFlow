"""Follow-up notes attached to a ticket.

A note records who followed up and what they said. Note IDs are derived from
the notes already on the ticket rather than stored in a counter, so they
cannot drift across a reload.

Import direction: this module reads and writes ticket storage and takes its
rules from campusflow.validation. It does not import from campusflow.workflow.
"""

import re

from campusflow.storage import (
    DEFAULT_STORAGE_PATH,
    load_tickets,
    save_tickets,
)
from campusflow.validation import (
    NOTE_ID_PATTERN,
    NOTE_STATUSES,
    validate_author,
    validate_message,
)


def _find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise an error.

    Mirrors workflow._find_ticket by hand. The two are kept in step until one
    shared lookup replaces both.
    """
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must be a non-empty string.")

    ticket_id = ticket_id.strip()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def _note_number(note):
    """Return the numeric part of a note ID, or 0 when it is unusable."""
    note_id = note.get("note_id") if isinstance(note, dict) else None

    if not isinstance(note_id, str):
        return 0

    match = re.fullmatch(NOTE_ID_PATTERN, note_id)

    return int(note_id[1:]) if match else 0


def _notes_of(ticket):
    """Return a ticket's notes list, supplying one only when it is absent.

    An absent key means a record written before the field existed, so an
    empty list loses nothing. A key that is present but unusable is a
    different case: it is a malformed record, and reading it as "no notes"
    would hide that in get_notes and destroy it in add_note, which saves.
    The rest of the project refuses unusable data rather than quietly
    replacing it, so this does too.
    """
    if "notes" not in ticket:
        return []

    notes = ticket["notes"]

    if not isinstance(notes, list):
        raise ValueError(
            f"Ticket {ticket['id']} has an unusable notes value: expected "
            f"a list, found {type(notes).__name__}."
        )

    return notes


def next_note_id(ticket):
    """Return the next free note ID for a ticket, derived from its notes.

    Anything that is not a well-formed note ID is skipped, the way
    next_ticket_id skips unusable ticket IDs, so one bad entry cannot
    stop a ticket from gaining new notes.
    """
    notes = ticket.get("notes")

    if not isinstance(notes, list):
        return "N001"

    highest = max((_note_number(note) for note in notes), default=0)

    return f"N{highest + 1:03d}"


def add_note(ticket_id, author, message, file_path=DEFAULT_STORAGE_PATH):
    """Add a follow-up note to a ticket and return the new note.

    Every rejection happens before the note ID is computed and before anything
    is written, so a refused note neither consumes an ID nor touches the file.
    """
    author = validate_author(author)
    message = validate_message(message)

    tickets = load_tickets(file_path)
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] not in NOTE_STATUSES:
        raise ValueError(
            "Reopen the ticket before adding a note to a resolved ticket."
        )

    notes = _notes_of(ticket)

    # A legacy ticket gains the key here. Doing it before the ID is derived
    # keeps next_note_id working from the ticket's real notes.
    ticket["notes"] = notes

    note = {
        "note_id": next_note_id(ticket),
        "author": author,
        "message": message,
    }

    notes.append(note)
    save_tickets(tickets, file_path)

    return note


def get_notes(ticket_id, file_path=DEFAULT_STORAGE_PATH):
    """Return a ticket's notes, ordered by note number.

    Ordering is numeric rather than by text, because "N010" sorts before
    "N002" as a string. Unusable IDs sort first and keep their stored order.
    A ticket whose notes value is unusable is refused rather than reported
    as a ticket with no notes.
    """
    tickets = load_tickets(file_path)
    ticket = _find_ticket(tickets, ticket_id)

    return sorted(_notes_of(ticket), key=_note_number)
