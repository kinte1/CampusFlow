import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import (
    load_tickets,
    save_tickets,
    generate_ticket_id,
)


class TestTicketStorage(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_missing_file_returns_empty_list(self):
        tickets = load_tickets(self.file_path)

        self.assertEqual(tickets, [])

    def test_save_and_load_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi is not working",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

        save_tickets(tickets, self.file_path)
        loaded_tickets = load_tickets(self.file_path)

        self.assertEqual(loaded_tickets, tickets)

    def test_saved_file_contains_valid_json(self):
        tickets = [{"id": "T001", "title": "Test ticket"}]

        save_tickets(tickets, self.file_path)

        with self.file_path.open("r", encoding="utf-8") as file:
            loaded_data = json.load(file)

        self.assertEqual(loaded_data, tickets)

    def test_malformed_json_raises_error(self):
        self.file_path.write_text(
            "{invalid json",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_tickets(self.file_path)

    def test_first_ticket_id(self):
        self.assertEqual(generate_ticket_id([]), "T001")

    def test_generates_next_ticket_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T002"},
            {"id": "T003"},
        ]

        self.assertEqual(generate_ticket_id(tickets), "T004")

    def test_ticket_id_does_not_duplicate_deleted_ticket(self):
        tickets = [
            {"id": "T001"},
            {"id": "T003"},
        ]

        self.assertEqual(generate_ticket_id(tickets), "T004")


if __name__ == "__main__":
    unittest.main()


class TestTicketCreationIntegration(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_creates_and_saves_ticket(self):
        from campusflow.storage import create_and_save_ticket

        ticket = create_and_save_ticket(
            "Wi-Fi is down",
            "network",
            "high",
            12,
            self.file_path,
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(load_tickets(self.file_path), [ticket])

    def test_generates_next_id_after_reload(self):
        from campusflow.storage import create_and_save_ticket

        create_and_save_ticket(
            "Printer problem", "Hardware", "low", 1, self.file_path
        )
        create_and_save_ticket(
            "Software problem", "Software", "medium", 3, self.file_path
        )

        reloaded_tickets = load_tickets(self.file_path)

        self.assertEqual(
            [ticket["id"] for ticket in reloaded_tickets],
            ["T001", "T002"],
        )
