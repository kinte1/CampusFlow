import tempfile
import unittest
from pathlib import Path

from campusflow.storage import (
    create_and_save_ticket,
    load_tickets,
    save_tickets,
)
from campusflow.workflow import (
    assign_staff,
    get_work_queue,
    reopen_ticket,
    update_ticket_status,
)


class TestTicketWorkflow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_ticket(self, title, urgency="low", affected_users=1):
        return create_and_save_ticket(
            title,
            "Network",
            urgency,
            affected_users,
            self.file_path,
        )

    def test_assign_staff_and_save(self):
        ticket = self.create_ticket("Wi-Fi issue")

        updated = assign_staff(
            ticket["id"], "Grace", self.file_path
        )

        self.assertEqual(updated["assigned_to"], "Grace")
        self.assertEqual(
            load_tickets(self.file_path)[0]["assigned_to"],
            "Grace",
        )

    def test_reject_empty_staff_name(self):
        ticket = self.create_ticket("Wi-Fi issue")

        with self.assertRaises(ValueError):
            assign_staff(ticket["id"], "  ", self.file_path)

    def test_reject_unknown_ticket(self):
        with self.assertRaises(ValueError):
            assign_staff("T999", "Grace", self.file_path)

    def test_cannot_start_without_assignment(self):
        ticket = self.create_ticket("Wi-Fi issue")

        with self.assertRaises(ValueError):
            update_ticket_status(
                ticket["id"], "in_progress", self.file_path
            )

    def test_ticket_moves_through_workflow(self):
        ticket = self.create_ticket("Wi-Fi issue")
        ticket_id = ticket["id"]

        assign_staff(ticket_id, "Grace", self.file_path)
        update_ticket_status(
            ticket_id, "in_progress", self.file_path
        )
        updated = update_ticket_status(
            ticket_id, "resolved", self.file_path
        )

        self.assertEqual(updated["status"], "resolved")

    def test_cannot_skip_workflow_steps(self):
        ticket = self.create_ticket("Wi-Fi issue")

        with self.assertRaises(ValueError):
            update_ticket_status(
                ticket["id"], "resolved", self.file_path
            )

    def test_resolved_ticket_must_be_reopened_before_assignment(self):
        ticket = self.create_ticket("Wi-Fi issue")
        ticket_id = ticket["id"]

        assign_staff(ticket_id, "Grace", self.file_path)
        update_ticket_status(ticket_id, "in_progress", self.file_path)
        update_ticket_status(ticket_id, "resolved", self.file_path)

        with self.assertRaises(ValueError):
            assign_staff(ticket_id, "David", self.file_path)

        reopened = reopen_ticket(ticket_id, self.file_path)
        self.assertEqual(reopened["status"], "open")

        updated = assign_staff(ticket_id, "David", self.file_path)
        self.assertEqual(updated["assigned_to"], "David")

    def test_work_queue_prioritizes_critical_tickets(self):
        self.create_ticket("Low issue")
        self.create_ticket("Critical issue", "high", 10)
        self.create_ticket("High issue", "high", 1)

        queue = get_work_queue(self.file_path)

        self.assertEqual(
            [ticket["title"] for ticket in queue],
            ["Critical issue", "High issue", "Low issue"],
        )

    def test_work_queue_excludes_resolved_tickets(self):
        ticket = self.create_ticket("Resolved issue")
        ticket_id = ticket["id"]

        assign_staff(ticket_id, "Grace", self.file_path)
        update_ticket_status(ticket_id, "in_progress", self.file_path)
        update_ticket_status(ticket_id, "resolved", self.file_path)

        queue = get_work_queue(self.file_path)

        self.assertEqual(queue, [])

    
    def test_work_queue_sorts_ticket_ids_numerically(self):
        """Same-priority tickets are sorted by numeric ID."""
        self.create_ticket("Ticket ten")
        self.create_ticket("Ticket two")

        tickets = load_tickets(self.file_path)
        tickets[0]["id"] = "T010"
        tickets[1]["id"] = "T002"
        save_tickets(tickets, self.file_path)

        queue = get_work_queue(self.file_path)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T002", "T010"],
        )


    def test_reject_invalid_status(self):
        ticket = self.create_ticket("Wi-Fi issue")

        with self.assertRaises(ValueError):
            update_ticket_status(
                ticket["id"], "pending", self.file_path
            )


if __name__ == "__main__":
    unittest.main()