import json
import re
from pathlib import Path

from campusflow.tickets import create_ticket
from campusflow.validation import validate_ticket


DEFAULT_STORAGE_PATH = Path("data/tickets.json")


def load_tickets(file_path=DEFAULT_STORAGE_PATH):
    """Load, validate and normalise tickets from a JSON file.

    Validation is delegated to validate_ticket, which also supplies the
    legacy migration: a record written before the notes field existed comes
    back with an empty notes list rather than being rejected.

    The file is never written to here. A migrated record keeps its old shape
    on disk until something saves it, so reading stays a pure operation for
    the callers that only want to look.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Ticket storage contains invalid JSON: {file_path}"
        ) from error

    if not isinstance(tickets, list):
        raise ValueError("Ticket storage must contain a JSON list.")

    normalised = []
    seen_ids = set()

    for index, ticket in enumerate(tickets):
        try:
            validated = validate_ticket(ticket)
        except ValueError as error:
            raise ValueError(
                f"Invalid ticket at position {index}: {error}"
            ) from error

        ticket_id = validated["id"]

        # validate_ticket sees one record at a time, so it cannot know that
        # two of them share an ID. That check needs the whole collection.
        if ticket_id in seen_ids:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                f"duplicate ticket ID {ticket_id}."
            )

        seen_ids.add(ticket_id)
        normalised.append(validated)

    return normalised


def save_tickets(tickets, file_path=DEFAULT_STORAGE_PATH):
    """Validate every ticket, then write them to a JSON file.

    Validation runs before any filesystem work, so a refused save leaves the
    directory and the file exactly as they were. The validated copies are
    what get written, which keeps the stored form canonical and makes saving
    the mirror of loading.
    """
    if not isinstance(tickets, list):
        raise ValueError("Ticket storage must be a list of tickets.")

    validated = []

    for index, ticket in enumerate(tickets):
        try:
            validated.append(validate_ticket(ticket))
        except ValueError as error:
            raise ValueError(
                f"Refusing to save invalid ticket at position {index}: "
                f"{error}"
            ) from error

    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(validated, file, indent=4)
            file.write("\n")

        temporary_path.replace(file_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def next_ticket_id(tickets):
    """Generate the next ticket ID without reusing existing IDs."""
    highest_number = 0

    for ticket in tickets:
        ticket_id = ticket.get("id", "")

        if not isinstance(ticket_id, str):
            continue

        match = re.fullmatch(r"T(\d+)", ticket_id)

        if match:
            highest_number = max(
                highest_number,
                int(match.group(1)),
            )

    return f"T{highest_number + 1:03d}"


# docs/task-split.md section 2 names next_ticket_id as the published
# interface. The old name stays bound to the same function object so imports
# written against it keep working, rather than a second copy to drift.
generate_ticket_id = next_ticket_id


def create_and_save_ticket(
    title,
    category,
    urgency,
    affected_users,
    file_path=DEFAULT_STORAGE_PATH,
):
    """Create a validated ticket, assign its ID, save it, and return it."""
    tickets = load_tickets(file_path)
    ticket_id = next_ticket_id(tickets)

    # create_ticket() only sees the arguments it is handed, so it cannot know
    # whether that ID is already taken in the collection it is about to join.
    # The ID is derived from the collection above and should never collide, so
    # reaching this means the generator is wrong rather than the caller. Fail
    # here, before anything is appended or written, rather than save a second
    # record under an ID that already exists.
    if any(ticket.get("id") == ticket_id for ticket in tickets):
        raise ValueError(
            f"Ticket ID {ticket_id} already exists in the collection."
        )

    ticket = create_ticket(
        ticket_id,
        title,
        category,
        urgency,
        affected_users,
    )

    tickets.append(ticket)
    save_tickets(tickets, file_path)

    return ticket
