def validate_title(title):
    """Validate a support ticket title."""
    if not isinstance(title, str):
        raise ValueError("Ticket title must be text.")

    title = title.strip()

    if not title:
        raise ValueError("Ticket title cannot be empty.")

    return title

def validate_category(category):
    """Validate a support ticket category."""
    allowed_categories = {"Network", "Hardware", "Software", "Other"}

    if not isinstance(category, str):
        raise ValueError("Category must be text.")

    category = category.strip().title()

    if category not in allowed_categories:
        raise ValueError(
            f"Invalid category. Choose one of: {', '.join(sorted(allowed_categories))}."
        )

    return category

def validate_urgency(urgency):
    """Validate a support ticket urgency level."""
    allowed_urgencies = {"low", "medium", "high"}

    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")

    urgency = urgency.strip().lower()

    if urgency not in allowed_urgencies:
        raise ValueError(
            "Invalid urgency. Choose one of: high, low, medium."
        )

    return urgency

def validate_affected_users(affected_users):
    """Validate the number of users affected by a support issue."""
    if isinstance(affected_users, bool) or not isinstance(affected_users, int):
        raise ValueError("Affected users must be a positive integer.")

    if affected_users <= 0:
        raise ValueError("Affected users must be a positive integer.")

    return affected_users

def calculate_priority(urgency, affected_users):
    """Calculate ticket priority from urgency and affected-user count."""
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"

def create_ticket(ticket_id, title, category, urgency, affected_users):
    """Create and return a validated support ticket."""
    if not isinstance(ticket_id, str) or not ticket_id.strip():
        raise ValueError("Ticket ID must be non-empty text.")

    ticket_id = ticket_id.strip()

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
    }
