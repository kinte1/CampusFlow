from campusflow.validation import (
    CATEGORIES,
    PRIORITIES,
    PRIORITY_ORDER,
    STATUSES,
    URGENCIES,
    calculate_priority,
    can_transition,
    validate_affected_users,
    validate_assigned_to,
    validate_author,
    validate_category,
    validate_message,
    validate_note_id,
    validate_notes,
    validate_priority,
    validate_status,
    validate_ticket,
    validate_ticket_id,
    validate_title,
    validate_urgency,
)

# Re-exported so existing callers and tests can keep importing validation
# helpers from campusflow.tickets. Kept until every caller imports from
# campusflow.validation directly.
__all__ = [
    "CATEGORIES",
    "PRIORITIES",
    "PRIORITY_ORDER",
    "STATUSES",
    "URGENCIES",
    "calculate_priority",
    "can_transition",
    "create_ticket",
    "validate_affected_users",
    "validate_assigned_to",
    "validate_author",
    "validate_category",
    "validate_message",
    "validate_note_id",
    "validate_notes",
    "validate_priority",
    "validate_status",
    "validate_ticket",
    "validate_ticket_id",
    "validate_title",
    "validate_urgency",
]


def create_ticket(ticket_id, title, category, urgency, affected_users):
    """Create and return a validated support ticket.

    Every field is validated before the ticket dictionary is built, so an
    invalid argument raises without producing a partially-formed record.
    """
    ticket_id = validate_ticket_id(ticket_id)
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    priority = calculate_priority(urgency, affected_users)

    return {
        "id": ticket_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
