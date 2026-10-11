
from campusflow.storage import DEFAULT_STORAGE_PATH, load_tickets


def generate_report(file_path=DEFAULT_STORAGE_PATH):
    """Return ticket totals grouped by status and priority."""
    tickets = load_tickets(file_path)

    statuses = ("open", "in_progress", "resolved")
    priorities = ("critical", "high", "medium", "low")

    status_counts = {status: 0 for status in statuses}
    priority_counts = {priority: 0 for priority in priorities}

    for ticket in tickets:
        status_counts[ticket["status"]] += 1
        priority_counts[ticket["priority"]] += 1

    return {
        "total": len(tickets),
        "by_status": status_counts,
        "by_priority": priority_counts,
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
