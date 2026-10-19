import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from campusflow.notes import add_note, get_notes
from campusflow.storage import (
    create_and_save_ticket,
    generate_ticket_id,
    load_tickets,
    next_ticket_id,
    save_tickets,
)


def make_record(**overrides):
    """Return a complete, valid stored record, with optional overrides."""
    record = {
        "id": "T001",
        "title": "Wi-Fi is not working",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    record.update(overrides)

    return record


def make_note(note_id="N001", author="Mentor A", message="Router rebooted"):
    """Return a complete, valid stored note."""
    return {"note_id": note_id, "author": author, "message": message}


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
                "notes": [],
            }
        ]

        save_tickets(tickets, self.file_path)
        loaded_tickets = load_tickets(self.file_path)

        self.assertEqual(loaded_tickets, tickets)

    def test_saved_file_contains_valid_json(self):
        tickets = [
            {
                "id": "T001",
                "title": "Test ticket",
                "category": "Network",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        ]

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
        self.assertEqual(next_ticket_id([]), "T001")

    def test_generates_next_ticket_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T002"},
            {"id": "T003"},
        ]

        self.assertEqual(next_ticket_id(tickets), "T004")

    def test_ticket_id_does_not_duplicate_deleted_ticket(self):
        tickets = [
            {"id": "T001"},
            {"id": "T003"},
        ]

        self.assertEqual(next_ticket_id(tickets), "T004")

    def test_old_name_is_still_the_same_function(self):
        """A-12: the rename must not leave a second copy to drift."""
        self.assertIs(generate_ticket_id, next_ticket_id)

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

    def test_load_rejects_unassigned_resolved_ticket(self):
        """Resolved is only reachable via in_progress, so it needs an owner."""
        ticket = {
            "id": "T001",
            "title": "Wi-Fi problem",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "resolved",
            "assigned_to": None,
        }

        self.file_path.write_text(
            json.dumps([ticket]),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            ValueError,
            "resolved ticket must be assigned",
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
        # The patch target is the name create_and_save_ticket actually calls:
        # the old name is an alias of the same object, so patching it would
        # rebind only the alias and leave the call un-stubbed.
        with mock.patch(
            "campusflow.storage.next_ticket_id",
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


class TestLoadHardening(unittest.TestCase):
    """Issue #11 / D2: load validates, normalises, and writes nothing."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def write(self, records):
        """Write records straight to disk, bypassing save validation."""
        self.file_path.write_text(
            json.dumps(records),
            encoding="utf-8",
        )

    def test_normalises_a_legacy_record_without_writing(self):
        """A pre-notes record loads, and reading it changes nothing.

        The normalisation must be in memory only: load_tickets is called by
        the read-only paths too, and a load that rewrites the file would make
        get_notes and the report mutate stored data.
        """
        legacy = make_record()
        del legacy["notes"]

        self.write([legacy])
        before = self.file_path.read_bytes()

        loaded = load_tickets(self.file_path)

        self.assertEqual(loaded[0]["notes"], [])
        self.assertEqual(self.file_path.read_bytes(), before)

        with self.file_path.open("r", encoding="utf-8") as file:
            self.assertNotIn("notes", json.load(file)[0])

    def test_rejects_a_malformed_notes_value(self):
        for value in ("oops", {}, 3, None):
            with self.subTest(value=value):
                self.write([make_record(notes=value)])

                with self.assertRaisesRegex(
                    ValueError, "notes must be a list"
                ):
                    load_tickets(self.file_path)

    def test_rejects_duplicate_note_ids_within_one_ticket(self):
        """validate_notes sees one ticket, so this check is per ticket."""
        note = make_note()

        self.write([make_record(notes=[note, note])])

        with self.assertRaisesRegex(ValueError, "duplicate note ID"):
            load_tickets(self.file_path)

    def test_reports_the_position_of_the_offending_record(self):
        """A bad record in a long file has to be findable.

        The second record needs its own ID: reusing T001 would make the
        duplicate-ID check fire first and the test would pass on a loader
        that never looked at notes at all.
        """
        self.write(
            [make_record(), make_record(id="T002", notes="oops")]
        )

        with self.assertRaisesRegex(ValueError, "position 1"):
            load_tickets(self.file_path)

    def test_canonicalises_stored_values(self):
        self.write([make_record(category="  network  ")])

        loaded = load_tickets(self.file_path)

        self.assertEqual(loaded[0]["category"], "Network")

    def test_drops_an_unknown_extra_key(self):
        """The returned record is the canonical set, not the stored one."""
        self.write([make_record(legacy_counter=7)])

        loaded = load_tickets(self.file_path)

        self.assertNotIn("legacy_counter", loaded[0])


class TestSaveHardening(unittest.TestCase):
    """Issue #11 / D3: save validates before it touches the disk."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_rejects_an_invalid_ticket_without_touching_the_file(self):
        save_tickets([make_record()], self.file_path)
        before = self.file_path.read_bytes()

        broken = make_record(id="T002", priority="low")

        with self.assertRaisesRegex(
            ValueError, "Refusing to save invalid ticket at position 1"
        ):
            save_tickets([make_record(), broken], self.file_path)

        self.assertEqual(self.file_path.read_bytes(), before)

    def test_rejects_an_invalid_ticket_without_creating_a_directory(self):
        """Validation runs before mkdir, so a refused save leaves no trace."""
        nested = Path(self.temp_directory.name) / "fresh" / "tickets.json"

        with self.assertRaises(ValueError):
            save_tickets([make_record(urgency="impossible")], nested)

        self.assertFalse(nested.parent.exists())

    def test_writes_the_normalised_form(self):
        """A caller's record is written canonical, not as handed in."""
        stale = make_record(category="  network  ", legacy_counter=7)

        save_tickets([stale], self.file_path)

        with self.file_path.open("r", encoding="utf-8") as file:
            written = json.load(file)[0]

        self.assertEqual(written["category"], "Network")
        self.assertEqual(written["notes"], [])
        self.assertNotIn("legacy_counter", written)

    def test_rejects_duplicate_ids_without_touching_the_file(self):
        """A save must not write what the next load would refuse.

        validate_ticket sees one record at a time, so two otherwise valid
        tickets sharing an ID both pass it. Without a check on this side,
        save_tickets writes them and load_tickets then rejects the file it
        just produced — the round trip broken at the boundary between its
        own two halves.
        """
        save_tickets([make_record()], self.file_path)
        before = self.file_path.read_bytes()

        with self.assertRaisesRegex(
            ValueError, "duplicate ticket ID T001"
        ):
            save_tickets([make_record(), make_record()], self.file_path)

        self.assertEqual(self.file_path.read_bytes(), before)
        self.assertEqual(len(load_tickets(self.file_path)), 1)

    def test_rejects_duplicate_ids_before_creating_a_directory(self):
        nested = Path(self.temp_directory.name) / "fresh" / "tickets.json"

        with self.assertRaisesRegex(ValueError, "duplicate ticket ID"):
            save_tickets([make_record(), make_record()], nested)

        self.assertFalse(nested.parent.exists())

    def test_everything_saved_can_be_loaded(self):
        """The invariant D3 exists for: save and load must not disagree."""
        tickets = [
            make_record(),
            make_record(
                id="T002",
                title="Printer jam",
                urgency="low",
                affected_users=1,
                priority="low",
            ),
            make_record(id="T003", notes=[make_note("N001")]),
        ]

        save_tickets(tickets, self.file_path)

        self.assertEqual(load_tickets(self.file_path), tickets)

    def test_rejects_a_non_list(self):
        with self.assertRaisesRegex(
            ValueError, "must be a list of tickets"
        ):
            save_tickets("not a list", self.file_path)

    def test_save_and_load_round_trip_a_ticket_with_notes(self):
        ticket = make_record(notes=[make_note("N001"), make_note("N002")])

        save_tickets([ticket], self.file_path)

        self.assertEqual(load_tickets(self.file_path), [ticket])


class TestPersistenceAcceptance(unittest.TestCase):
    """Acceptance cases 12 and 13 from docs/task-split.md section 5."""

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_directory.name) / "tickets.json"

    def tearDown(self):
        self.temp_directory.cleanup()

    def stored_bytes(self):
        return self.file_path.read_bytes()

    def test_case_12_save_and_load_preserves_notes_and_next_ids(self):
        """Case 12: notes and the derived IDs survive a reload."""
        ticket = create_and_save_ticket(
            "Wi-Fi is down",
            "Network",
            "high",
            12,
            self.file_path,
        )

        add_note(
            ticket["id"],
            "Mentor A",
            "Router rebooted, monitoring.",
            self.file_path,
        )

        reloaded = load_tickets(self.file_path)

        self.assertEqual(
            [note["note_id"] for note in reloaded[0]["notes"]],
            ["N001"],
        )

        # The IDs are derived from what is on disk, so a reload must not
        # reset either of them to the start.
        self.assertEqual(next_ticket_id(reloaded), "T002")

        second = add_note(
            ticket["id"],
            "Mentor B",
            "Confirmed stable after an hour.",
            self.file_path,
        )

        self.assertEqual(second["note_id"], "N002")
        self.assertEqual(
            get_notes(ticket["id"], self.file_path),
            reloaded[0]["notes"] + [second],
        )

    def test_case_13_corrupt_json_is_rejected_without_state_loss(self):
        """Case 13: a corrupt file is refused, and stays as it was."""
        self.file_path.write_text("{invalid json", encoding="utf-8")
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.file_path)

        self.assertEqual(self.stored_bytes(), before)

    def test_case_13_duplicate_ids_are_rejected_without_state_loss(self):
        """Case 13: two records sharing an ID are refused, with no loss."""
        duplicate = make_record()

        self.file_path.write_text(
            json.dumps([duplicate, duplicate]),
            encoding="utf-8",
        )
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "duplicate ticket ID T001"):
            load_tickets(self.file_path)

        self.assertEqual(self.stored_bytes(), before)


if __name__ == "__main__":
    unittest.main()