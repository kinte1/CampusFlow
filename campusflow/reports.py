
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets
from campusflow.validation import CATEGORIES, PRIORITIES, STATUSES


def generate_report(file_path=DEFAULT_STORAGE_PATH):
    """Return ticket totals grouped by status, priority, and category."""
    tickets = load_tickets(file_path)

    status_counts = {status: 0 for status in STATUSES}
    priority_counts = {priority: 0 for priority in PRIORITIES}
    category_counts = {category: 0 for category in CATEGORIES}

    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1
        category_counts[ticket["category"]] += 1

    total = len(tickets)
    resolved = status_counts["resolved"]
    unresolved = status_counts["open"] + status_counts["in_progress"]

    if total == 0:
        resolution_percentage = 0.0
    else:
        resolution_percentage = round((resolved / total) * 100, 1)

    return {
        "total": total,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "by_category": category_counts,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": resolution_percentage,
    }


def print_report(file_path=DEFAULT_STORAGE_PATH):
    """Display a readable ticket report."""
    report = generate_report(file_path)

    print("\n=== CAMPUSFLOW TICKET REPORT ===")
    print(f"Total tickets: {report['total']}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status.replace('_', ' ').title()}: {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority.title()}: {count}")

    print("\nBy category:")
    for category, count in report["by_category"].items():
        print(f"  {category}: {count}")

    print(f"\nUnresolved tickets: {report['unresolved']}")
    print(f"Resolved tickets: {report['resolved']}")
    print(f"Resolution rate: {report['resolution_percentage']:.1f}%")
