from campusflow.notes import add_note, get_notes
from campusflow.storage import create_and_save_ticket, load_tickets
from campusflow.workflow import (
    assign_staff,
    get_work_queue,
    reopen_ticket,
    update_ticket_status,
)
from campusflow.reports import print_report
from campusflow.search import search_tickets, sort_by_priority_then_id
from campusflow.understanding_check import run as run_understanding_check
from campusflow.validation import CATEGORIES, STATUSES, PRIORITIES


def show_tickets(tickets):
    if not tickets:
        print("\nNo tickets found.")
        return

    for ticket in tickets:
        print(
            f"\n{ticket['id']} - {ticket['title']}\n"
            f"  Category: {ticket['category']}\n"
            f"  Priority: {ticket['priority']}\n"
            f"  Status: {ticket['status']}\n"
            f"  Assigned to: {ticket['assigned_to'] or 'Unassigned'}"
        )


def prompt_affected_users():
    """Prompt until the user enters a positive whole number."""
    while True:
        value = input("Affected users: ").strip()

        try:
            affected_users = int(value)
        except ValueError:
            print(
                "Error: Please enter a positive whole number, "
                "such as 2. Decimals and text are not accepted."
            )
            continue

        if affected_users <= 0:
            print("Error: Affected users must be greater than zero.")
            continue

        return affected_users


def prompt_optional_filter(label, options):
    """Ask for an optional filter and retry invalid choices."""
    print(f"\nAvailable {label.lower()} options: {', '.join(options)}")

    while True:
        value = input(
            f"{label} (press Enter to skip): "
        ).strip()

        if not value:
            return None

        for option in options:
            if value.casefold() == option.casefold():
                return option

        print(
            f"Invalid {label.lower()}. "
            f"Choose one of: {', '.join(options)}, or press Enter to skip."
        )


def add_note_menu():
    """Collect note details and save a follow-up note."""
    ticket_id = input("Ticket ID: ")
    author = input("Author: ")
    message = input("Note: ")

    note = add_note(ticket_id, author, message)

    print(
        f"Added note {note['note_id']} to ticket {ticket_id.strip()}."
    )


def view_notes_menu():
    """Display a ticket's notes in note-ID order."""
    ticket_id = input("Ticket ID: ")
    notes = get_notes(ticket_id)

    if not notes:
        print(f"\nNo notes found for ticket {ticket_id.strip()}.")
        return

    print(f"\n=== NOTES FOR TICKET {ticket_id.strip()} ===")

    for note in notes:
        print(
            f"\n{note['note_id']} - {note['author']}\n"
            f"  {note['message']}"
        )


def prompt_search_criteria():
    """Collect a title query and optional search filters."""
    query = input(
        "\nTitle contains (press Enter to skip): "
    ).strip()

    category = prompt_optional_filter("Category", CATEGORIES)
    status = prompt_optional_filter("Status", STATUSES)
    priority = prompt_optional_filter("Priority", PRIORITIES)

    return {
        "query": query,
        "category": category,
        "status": status,
        "priority": priority,
    }


def run_search(sorted_by_priority):
    """Collect search criteria, search, and display matching tickets."""
    criteria = prompt_search_criteria()
    results = search_tickets(load_tickets(), **criteria)

    if sorted_by_priority:
        # Keep this view's priority ordering explicit.
        results = sort_by_priority_then_id(results)
        print("\n=== SEARCH RESULTS (SORTED BY PRIORITY) ===")
    else:
        print("\n=== SEARCH RESULTS ===")

    show_tickets(results)


def search_tickets_menu():
    """Search tickets and display matching tickets."""
    run_search(sorted_by_priority=False)


def sorted_search_menu():
    """Search tickets and display results sorted by priority."""
    run_search(sorted_by_priority=True)


def main():
    while True:
        print("\n=== CAMPUSFLOW ===")
        print("1. Create ticket")
        print("2. List all tickets")
        print("3. Assign staff")
        print("4. Start ticket")
        print("5. Resolve ticket")
        print("6. Reopen ticket")
        print("7. View work queue")
        print("8. View report")
        print("9. Search tickets")
        print("10. Add follow-up note")
        print("11. View ticket notes")
        print("12. Search results sorted by priority")
        print("13. Engineering Understanding Check")
        print("0. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Ticket title: ")
                category = input(
                    "Category (Network/Hardware/Software/Other): "
                )
                urgency = input("Urgency (low/medium/high): ")
                affected_users = prompt_affected_users()

                ticket = create_and_save_ticket(
                    title, category, urgency, affected_users
                )
                print(f"Created ticket {ticket['id']}.")

            elif choice == "2":
                show_tickets(load_tickets())

            elif choice == "3":
                ticket_id = input("Ticket ID: ")
                staff_name = input("Staff name: ")
                ticket = assign_staff(ticket_id, staff_name)
                print(f"{ticket['id']} assigned to {ticket['assigned_to']}.")

            elif choice == "4":
                ticket_id = input("Ticket ID: ")
                update_ticket_status(ticket_id, "in_progress")
                print("Ticket marked as in progress.")

            elif choice == "5":
                ticket_id = input("Ticket ID: ")
                update_ticket_status(ticket_id, "resolved")
                print("Ticket resolved.")

            elif choice == "6":
                ticket_id = input("Ticket ID: ")
                reopen_ticket(ticket_id)
                print("Ticket reopened.")

            elif choice == "7":
                show_tickets(get_work_queue())

            elif choice == "8":
                print_report()

            elif choice == "9":
                search_tickets_menu()

            elif choice == "10":
                add_note_menu()

            elif choice == "11":
                view_notes_menu()

            elif choice == "12":
                sorted_search_menu()

            elif choice == "13":
                run_understanding_check()

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Choose from the menu.")

        except (ValueError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()