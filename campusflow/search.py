from campusflow.validation import (
    CATEGORIES,
    PRIORITIES,
    PRIORITY_ORDER,
    STATUSES,
)


def _normalise_filter(value, options, label):
    """Return value in its canonical spelling, or None when unsupplied."""
    if value is None:
        return None

    if not isinstance(value, str):
        raise ValueError(
            f"{label} must be a string, found {type(value).__name__}."
        )

    value = value.strip()

    if not value:
        return None

    for option in options:
        if value.casefold() == option.casefold():
            return option

    raise ValueError(
        f"Unknown {label.lower()} {value!r}. "
        f"Choose one of: {', '.join(options)}."
    )


def sort_by_priority_then_id(tickets):
    """Return a new list ordered by priority, then numeric ticket ID.

    The ticket ID is compared numerically, because "T10" sorts before "T2"
    as text.
    """
    return sorted(
        tickets,
        key=lambda ticket: (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket["id"][1:]),
        ),
    )


def search_tickets(
    tickets,
    query=None,
    category=None,
    status=None,
    priority=None,
):
    """Return tickets matching a title and all supplied filters.

    Title matching is case-insensitive substring matching. Supplied filters
    are combined using AND logic, and their values are matched without
    regard to case. The input list is not modified.
    """
    query = (query or "").strip().casefold()
    category = _normalise_filter(category, CATEGORIES, "Category")
    status = _normalise_filter(status, STATUSES, "Status")
    priority = _normalise_filter(priority, PRIORITIES, "Priority")

    results = []

    for ticket in tickets:
        if query not in ticket["title"].casefold():
            continue

        if category is not None and ticket["category"] != category:
            continue

        if status is not None and ticket["status"] != status:
            continue

        if priority is not None and ticket["priority"] != priority:
            continue

        results.append(ticket)

    return sort_by_priority_then_id(results)
