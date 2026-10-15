import copy
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import create_and_save_ticket, load_tickets
from campusflow.validation import (
    NOTE_MAX_LENGTH,
    can_transition,
    validate_message,
    validate_notes,
    validate_ticket,
)
from campusflow.workflow import update_ticket_status


def make_ticket(**overrides):
    """Return a valid ticket record, with optional field overrides."""
    ticket = {
        "id": "T001",
        "title": "Wi-Fi is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }

    ticket.update(overrides)

    return ticket


class TestCanTransition(unittest.TestCase):
    """The status graph on its own, independent of ticket state."""

    def test_legal_transitions(self):
        legal = [
            ("open", "in_progress"),
            ("in_progress", "resolved"),
            ("resolved", "open"),
        ]

        for current, new in legal:
            with self.subTest(current=current, new=new):
                self.assertTrue(can_transition(current, new))

    def test_illegal_transitions(self):
        illegal = [
            ("open", "resolved"),        # must pass through in_progress
            ("resolved", "in_progress"),  # must reopen first
            ("open", "open"),             # not a transition at all
            ("in_progress", "in_progress"),
        ]

        for current, new in illegal:
            with self.subTest(current=current, new=new):
                self.assertFalse(can_transition(current, new))

    def test_unknown_statuses_are_never_allowed(self):
        self.assertFalse(can_transition("pending", "open"))
        self.assertFalse(can_transition("open", "pending"))

    def test_does_not_raise_on_bad_input(self):
        """A predicate answers a question; "no" is a normal answer."""
        for current, new in [(None, "open"), ("open", None), (1, 2)]:
            with self.subTest(current=current, new=new):
                self.assertFalse(can_transition(current, new))


class TestValidateTicket(unittest.TestCase):
    def test_accepts_a_valid_ticket(self):
        ticket = make_ticket()

        validated = validate_ticket(ticket)

        self.assertEqual(validated["id"], "T001")
        self.assertEqual(validated["priority"], "critical")

    def test_migrates_a_missing_notes_key_to_an_empty_list(self):
        """Legacy files predate the notes field and must still load."""
        ticket = make_ticket()

        self.assertNotIn("notes", ticket)

        validated = validate_ticket(ticket)

        self.assertEqual(validated["notes"], [])

    def test_does_not_mutate_the_input(self):
        ticket = make_ticket()
        original = copy.deepcopy(ticket)

        validate_ticket(ticket)

        self.assertEqual(ticket, original)

    def test_rejects_a_missing_field(self):
        ticket = make_ticket()
        del ticket["urgency"]

        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_ticket(ticket)

    def test_rejects_a_priority_that_does_not_match(self):
        ticket = make_ticket(priority="low")

        with self.assertRaisesRegex(ValueError, "priority does not match"):
            validate_ticket(ticket)

    def test_rejects_an_unassigned_in_progress_ticket(self):
        ticket = make_ticket(status="in_progress", assigned_to=None)

        with self.assertRaisesRegex(
            ValueError, "in-progress ticket must be assigned"
        ):
            validate_ticket(ticket)

    def test_accepts_an_assigned_in_progress_ticket(self):
        ticket = make_ticket(status="in_progress", assigned_to="Grace")

        validated = validate_ticket(ticket)

        self.assertEqual(validated["assigned_to"], "Grace")

    def test_rejects_booleans_as_affected_users(self):
        for value in (True, False):
            with self.subTest(value=value):
                ticket = make_ticket(affected_users=value)

                with self.assertRaises(ValueError):
                    validate_ticket(ticket)

    def test_rejects_a_non_dictionary(self):
        with self.assertRaisesRegex(ValueError, "must be a dictionary"):
            validate_ticket(["not", "a", "ticket"])

    def test_trims_text_fields_without_losing_them(self):
        ticket = make_ticket(title="  Printer jam  ", assigned_to=" Grace ")

        validated = validate_ticket(ticket)

        self.assertEqual(validated["title"], "Printer jam")
        self.assertEqual(validated["assigned_to"], "Grace")


class TestValidateNotes(unittest.TestCase):
    def make_note(self, note_id="N001", author="Mentor A", message="Router rebooted"):
        return {"note_id": note_id, "author": author, "message": message}

    def test_accepts_a_valid_note_list(self):
        notes = [self.make_note("N001"), self.make_note("N002")]

        self.assertEqual(len(validate_notes(notes)), 2)

    def test_accepts_an_empty_list(self):
        self.assertEqual(validate_notes([]), [])

    def test_rejects_duplicate_note_ids_within_a_ticket(self):
        notes = [self.make_note("N001"), self.make_note("N001")]

        with self.assertRaisesRegex(ValueError, "duplicate note ID"):
            validate_notes(notes)

    def test_rejects_a_non_list(self):
        with self.assertRaisesRegex(ValueError, "notes must be a list"):
            validate_notes({"N001": "oops"})

    def test_rejects_a_note_missing_fields(self):
        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_notes([{"note_id": "N001"}])

    def test_rejects_a_malformed_note_id(self):
        with self.assertRaisesRegex(ValueError, "Note ID must start with N"):
            validate_notes([self.make_note("note-1")])


class TestValidateMessage(unittest.TestCase):
    def test_accepts_a_message_at_the_minimum_length(self):
        message = "a" * 5

        self.assertEqual(validate_message(message), message)

    def test_accepts_a_message_at_the_maximum_length(self):
        message = "a" * NOTE_MAX_LENGTH

        self.assertEqual(validate_message(message), message)

    def test_rejects_a_message_that_is_too_short(self):
        with self.assertRaisesRegex(ValueError, "between 5 and 300"):
            validate_message("abcd")

    def test_rejects_a_message_that_is_too_long(self):
        with self.assertRaisesRegex(ValueError, "between 5 and 300"):
            validate_message("a" * (NOTE_MAX_LENGTH + 1))

    def test_length_is_measured_after_trimming(self):
        """Whitespace must not pad a too-short message into validity."""
        with self.assertRaises(ValueError):
            validate_message("    ab    ")


class TestRejectedActionsLeaveDataUnchanged(unittest.TestCase):
    """Acceptance case 02.

    Proving an invalid action changes nothing needs a before/after comparison
    of the stored data. assertRaises alone only shows that an error was
    raised, not that the failed action left no trace behind.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def stored_bytes(self):
        """Return the raw file contents, for an exact comparison."""
        return self.file_path.read_bytes()

    def make_ticket(self, urgency="high", affected_users=12):
        return create_and_save_ticket(
            "Wi-Fi is down",
            "Network",
            urgency,
            affected_users,
            self.file_path,
        )

    def test_unassigned_open_ticket_cannot_start(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "Assign a staff member"):
            update_ticket_status(
                ticket["id"], "in_progress", self.file_path
            )

        self.assertEqual(self.stored_bytes(), before)

    def test_rejected_creation_writes_no_record(self):
        self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaises(ValueError):
            create_and_save_ticket(
                "Broken ticket",
                "Network",
                "high",
                0,
                self.file_path,
            )

        self.assertEqual(self.stored_bytes(), before)
        self.assertEqual(len(load_tickets(self.file_path)), 1)

    def test_rejected_transition_leaves_status_untouched(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaises(ValueError):
            update_ticket_status(ticket["id"], "resolved", self.file_path)

        self.assertEqual(self.stored_bytes(), before)
        self.assertEqual(load_tickets(self.file_path)[0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
