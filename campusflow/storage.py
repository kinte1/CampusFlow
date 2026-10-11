import json
import re
from pathlib import Path

from campusflow.tickets import create_ticket


DEFAULT_STORAGE_PATH = Path("data/tickets.json")


def load_tickets(file_path=DEFAULT_STORAGE_PATH):
    """Load and validate tickets from a JSON file."""
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

    required_fields = {
        "id",
        "title",
        "category",
        "urgency",
        "affected_users",
        "priority",
        "status",
        "assigned_to",
    }

    seen_ids = set()

    for index, ticket in enumerate(tickets):
        if not isinstance(ticket, dict):
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "each ticket must be a dictionary."
            )

        missing_fields = required_fields - ticket.keys()

        if missing_fields:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                f"missing fields {sorted(missing_fields)}."
            )

        ticket_id = ticket["id"]

        if not isinstance(ticket_id, str):
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "Ticket ID must be text."
            )

        ticket_id = ticket_id.strip()

        if ticket_id in seen_ids:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                f"duplicate ticket ID {ticket_id}."
            )

        seen_ids.add(ticket_id)

        try:
            validated_ticket = create_ticket(
                ticket_id,
                ticket["title"],
                ticket["category"],
                ticket["urgency"],
                ticket["affected_users"],
            )
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid ticket at position {index}: {error}"
            ) from error

        if ticket["priority"] != validated_ticket["priority"]:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "priority does not match the ticket details."
            )

        if ticket["status"] not in {
            "open",
            "in_progress",
            "resolved",
        }:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "unknown status."
            )

        assigned_to = ticket["assigned_to"]

        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "assigned_to must be None or a non-empty string."
            )

        if ticket["status"] == "in_progress" and assigned_to is None:
            raise ValueError(
                f"Invalid ticket at position {index}: "
                "an in-progress ticket must be assigned."
            )

    return tickets


def save_tickets(tickets, file_path=DEFAULT_STORAGE_PATH):
    """Save tickets to a JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = file_path.with_suffix(file_path.suffix + ".tmp")

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(tickets, file, indent=4)
            file.write("\n")

        temporary_path.replace(file_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def generate_ticket_id(tickets):
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


def create_and_save_ticket(
    title,
    category,
    urgency,
    affected_users,
    file_path=DEFAULT_STORAGE_PATH,
):
    """Create a validated ticket, assign its ID, save it, and return it."""
    tickets = load_tickets(file_path)
    ticket_id = generate_ticket_id(tickets)

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