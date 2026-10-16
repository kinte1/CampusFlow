
from campusflow.storage import (
    DEFAULT_STORAGE_PATH,
    load_tickets,
    save_tickets,
)
from campusflow.validation import PRIORITY_ORDER


def _find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise an error."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must be a non-empty string.")

    ticket_id = ticket_id.strip()

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Ticket {ticket_id} was not found.")


def assign_staff(
    ticket_id,
    staff_name,
    file_path=DEFAULT_STORAGE_PATH,
):
    """Assign a staff member to an existing unresolved ticket."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name cannot be empty.")

    tickets = load_tickets(file_path)
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError(
            "Reopen the ticket before modifying a resolved ticket."
        )

    ticket["assigned_to"] = staff_name.strip()
    save_tickets(tickets, file_path)

    return ticket


def update_ticket_status(
    ticket_id,
    new_status,
    file_path=DEFAULT_STORAGE_PATH,
):
    """Move a ticket through the normal workflow."""
    if new_status not in {"in_progress", "resolved"}:
        raise ValueError(
            "Use 'in_progress' or 'resolved'. "
            "Use reopen_ticket() to reopen a resolved ticket."
        )

    tickets = load_tickets(file_path)
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError(
            "Reopen the ticket before modifying a resolved ticket."
        )

    if new_status == "in_progress":
        if ticket["status"] != "open":
            raise ValueError("Only open tickets can start in progress.")

        if not ticket["assigned_to"]:
            raise ValueError(
                "Assign a staff member before starting the ticket."
            )

    elif new_status == "resolved":
        if ticket["status"] != "in_progress":
            raise ValueError(
                "Only in-progress tickets can be resolved."
            )

    ticket["status"] = new_status
    save_tickets(tickets, file_path)

    return ticket


def reopen_ticket(ticket_id, file_path=DEFAULT_STORAGE_PATH):
    """Reopen a resolved ticket so it can be modified again."""
    tickets = load_tickets(file_path)
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    save_tickets(tickets, file_path)

    return ticket


def get_work_queue(file_path=DEFAULT_STORAGE_PATH):
    """Return open tickets in priority and ID order."""
    tickets = load_tickets(file_path)

    open_tickets = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    return sorted(
        open_tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )
