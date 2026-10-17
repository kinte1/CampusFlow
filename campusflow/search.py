
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets
from campusflow.validation import PRIORITY_ORDER


def search_tickets(
    query="",
    category=None,
    status=None,
    priority=None,
    file_path=DEFAULT_STORAGE_PATH,
    sort_by_priority=True,
):
    """Return tickets matching a title and all supplied filters.

    Title matching is case-insensitive substring matching.
    Supplied filters are combined using AND logic.
    Results are sorted by priority and ticket ID by default.
    Set sort_by_priority=False to sort by numeric ticket ID instead.
    Searching does not modify stored tickets.
    """
    tickets = load_tickets(file_path)
    query = query.strip().casefold()

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

    if sort_by_priority:
        results.sort(
            key=lambda ticket: (
                PRIORITY_ORDER[ticket["priority"]],
                int(ticket["id"][1:]),
            )
        )
    else:
        results.sort(
            key=lambda ticket: int(ticket["id"][1:])
        )

    return results
