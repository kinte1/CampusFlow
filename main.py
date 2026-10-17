
from campusflow.storage import (
    create_and_save_ticket,
    load_tickets,
)
from campusflow.workflow import (
    assign_staff,
    get_work_queue,
    reopen_ticket,
    update_ticket_status,
)
from campusflow.reports import print_report
from campusflow.search import search_tickets
from campusflow.notes import add_note, get_notes
from campusflow.understanding_check import (
    run as run_understanding_check,
)
from campusflow.validation import CATEGORIES, STATUSES, PRIORITIES


def prompt_optional_filter(label, options):
    """Ask for an optional filter and retry invalid choices."""
    while True:
        value = input(
            f"{label} ({'/'.join(options)}, or Enter to skip): "
        ).strip()

        if not value:
            return None

        normalized = value.lower()

        for option in options:
            if normalized == option.lower():
                return option

        print(f"Invalid {label.lower()}. Please try again.")


def collect_search_filters():
    """Collect the title query and optional ticket filters."""
    query = input(
        "\nTitle contains (press Enter to skip): "
    ).strip()

    category = prompt_optional_filter("Category", CATEGORIES)
    status = prompt_optional_filter("Status", STATUSES)
    priority = prompt_optional_filter("Priority", PRIORITIES)

    return query, category, status, priority


def show_tickets(tickets):
    """Display tickets in a readable format."""
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


def search_tickets_menu():
    """Search tickets and display results by ticket ID."""
    query, category, status, priority = collect_search_filters()

    results = search_tickets(
        query=query,
        category=category,
        status=status,
        priority=priority,
        sort_by_priority=False,
    )

    print("\n=== SEARCH RESULTS (TICKET ID ORDER) ===")
    show_tickets(results)


def add_follow_up_note_menu():
    """Prompt for note details and save a follow-up note."""
    ticket_id = input("Ticket ID: ").strip()
    author = input("Author name: ").strip()
    message = input("Follow-up note: ").strip()

    note = add_note(ticket_id, author, message)

    print(
        f"Added note {note['note_id']} to ticket {ticket_id}."
    )


def view_ticket_notes_menu():
    """Display the notes belonging to a ticket."""
    ticket_id = input("Ticket ID: ").strip()
    notes = get_notes(ticket_id)

    print(f"\n=== NOTES FOR {ticket_id} ===")

    if not notes:
        print("No follow-up notes found.")
        return

    for note in notes:
        print(
            f"\n{note['note_id']} - {note['author']}\n"
            f"  {note['message']}"
        )


def search_by_priority_menu():
    """Search tickets and display results by priority."""
    query, category, status, priority = collect_search_filters()

    results = search_tickets(
        query=query,
        category=category,
        status=status,
        priority=priority,
        sort_by_priority=True,
    )

    print("\n=== PRIORITY-SORTED SEARCH RESULTS ===")
    show_tickets(results)


def main():
    while True:
        print("\n=== CAMPUSFLOW ===")
        print("1. Create ticket")
        print("2. Update ticket status")
        print("3. Assign ticket")
        print("4. Reopen resolved ticket")
        print("5. View all tickets")
        print("6. View work queue")
        print("7. View report")
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
                    f"Category ({'/'.join(CATEGORIES)}): "
                )
                urgency = input("Urgency (low/medium/high): ")
                affected_users = input("Affected users: ")

                try:
                    affected_users = int(affected_users)
                except ValueError:
                    print("Error: Affected users must be a positive integer.")
                    continue

                ticket = create_and_save_ticket(
                    title,
                    category,
                    urgency,
                    affected_users,
                )
                print(
                    f"Created ticket {ticket['id']} "
                    f"with priority {ticket['priority']}."
                )

            elif choice == "2":
                ticket_id = input("Ticket ID: ").strip()
                new_status = input(
                    "New status (in_progress/resolved): "
                ).strip()

                ticket = update_ticket_status(ticket_id, new_status)
                print(
                    f"{ticket['id']} status updated to "
                    f"{ticket['status']}."
                )

            elif choice == "3":
                ticket_id = input("Ticket ID: ").strip()
                staff_name = input("Staff name: ")
                ticket = assign_staff(ticket_id, staff_name)
                print(
                    f"{ticket['id']} assigned to "
                    f"{ticket['assigned_to']}."
                )

            elif choice == "4":
                ticket_id = input("Ticket ID: ").strip()
                ticket = reopen_ticket(ticket_id)
                print(f"{ticket['id']} has been reopened.")

            elif choice == "5":
                show_tickets(load_tickets())

            elif choice == "6":
                show_tickets(get_work_queue())

            elif choice == "7":
                print_report()

            elif choice == "9":
                search_tickets_menu()

            elif choice == "10":
                add_follow_up_note_menu()

            elif choice == "11":
                view_ticket_notes_menu()

            elif choice == "12":
                search_by_priority_menu()

            elif choice == "13":
                run_understanding_check()

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Please choose again.")

        except (ValueError, KeyError, OSError) as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
