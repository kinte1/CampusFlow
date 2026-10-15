import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from campusflow.storage import (
    create_and_save_ticket,
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

    def test_load_rejects_null_ticket(self):
        self.file_path.write_text(
            "[null]",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "must be a dictionary"):
            load_tickets(self.file_path)

    def test_load_rejects_ticket_missing_fields(self):
        self.file_path.write_text(
            '[{"id": "T001"}]',
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "missing fields"):
            load_tickets(self.file_path)

    def test_load_rejects_incorrect_priority(self):
        ticket = {
            "id": "T001",
            "title": "Wi-Fi is not working",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "low",
            "status": "open",
            "assigned_to": None,
        }

        self.file_path.write_text(
            json.dumps([ticket]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "priority does not match",
        ):
            load_tickets(self.file_path)

    def test_load_rejects_duplicate_ticket_ids(self):
        ticket = {
            "id": "T001",
            "title": "Wi-Fi problem",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
        }

        self.file_path.write_text(
            json.dumps([ticket, ticket]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "duplicate ticket ID",
        ):
            load_tickets(self.file_path)

    def test_load_rejects_unassigned_in_progress_ticket(self):
        ticket = {
            "id": "T001",
            "title": "Wi-Fi problem",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "in_progress",
            "assigned_to": None,
        }

        self.file_path.write_text(
            json.dumps([ticket]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "in-progress ticket must be assigned",
        ):
            load_tickets(self.file_path)

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
            "Printer problem",
            "Hardware",
            "low",
            1,
            self.file_path,
        )

        create_and_save_ticket(
            "Software problem",
            "Software",
            "medium",
            3,
            self.file_path,
        )

        reloaded_tickets = load_tickets(self.file_path)

        self.assertEqual(
            [ticket["id"] for ticket in reloaded_tickets],
            ["T001", "T002"],
        )


class TestTicketIdUniqueness(unittest.TestCase):
    """Issue #9: the create path must never write a duplicate ticket ID."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_rejects_an_id_that_is_already_taken(self):
        existing = create_and_save_ticket(
            "Wi-Fi is down",
            "network",
            "high",
            12,
            self.file_path,
        )
        before = self.file_path.read_bytes()

        # Stub the generator so it hands back the ID already on disk. The real
        # generator derives its ID from the collection, so it does not collide
        # on its own; what is under test is create_and_save_ticket's guard,
        # which has to hold even if the generator is later changed or wrong.
        with mock.patch(
            "campusflow.storage.generate_ticket_id",
            return_value=existing["id"],
        ):
            with self.assertRaisesRegex(ValueError, "already exists"):
                create_and_save_ticket(
                    "Printer jam",
                    "hardware",
                    "low",
                    2,
                    self.file_path,
                )

        self.assertEqual(self.file_path.read_bytes(), before)
        self.assertEqual(len(load_tickets(self.file_path)), 1)

    def test_ordinary_creation_is_unaffected(self):
        """The guard must not reject the normal, non-colliding case."""
        first = create_and_save_ticket(
            "Wi-Fi is down",
            "network",
            "high",
            12,
            self.file_path,
        )
        second = create_and_save_ticket(
            "Printer jam",
            "hardware",
            "low",
            2,
            self.file_path,
        )

        self.assertEqual([first["id"], second["id"]], ["T001", "T002"])


if __name__ == "__main__":
    unittest.main()