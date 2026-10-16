import json
import tempfile
import unittest
from pathlib import Path

from campusflow.notes import add_note, get_notes, next_note_id
from campusflow.storage import create_and_save_ticket
from campusflow.workflow import (
    assign_staff,
    reopen_ticket,
    update_ticket_status,
)


class TestNextNoteId(unittest.TestCase):
    """The ID is derived from the ticket's notes, never from a counter."""

    def test_first_note_id(self):
        self.assertEqual(next_note_id({"notes": []}), "N001")

    def test_derives_from_the_highest_existing_id(self):
        ticket = {"notes": [{"note_id": "N001"}, {"note_id": "N002"}]}

        self.assertEqual(next_note_id(ticket), "N003")

    def test_missing_notes_key_starts_at_n001(self):
        """A legacy record predates the field and must still gain notes."""
        self.assertEqual(next_note_id({}), "N001")

    def test_skips_unusable_note_ids(self):
        """One bad entry must not stop the ticket gaining a new note."""
        ticket = {"notes": [{"note_id": "N002"}, {"note_id": "oops"}, {}]}

        self.assertEqual(next_note_id(ticket), "N003")

    def test_follows_the_highest_not_the_count(self):
        """Gaps are fine: the ID follows the highest, not the total."""
        ticket = {"notes": [{"note_id": "N001"}, {"note_id": "N005"}]}

        self.assertEqual(next_note_id(ticket), "N006")


class TestAddAndGetNotes(unittest.TestCase):
    """Acceptance case 05."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def stored_tickets(self):
        """Return the tickets as stored, straight from the file."""
        return json.loads(self.file_path.read_text(encoding="utf-8"))

    def make_ticket(self):
        return create_and_save_ticket(
            "Wi-Fi is down",
            "Network",
            "high",
            12,
            self.file_path,
        )

    def add(self, ticket_id, message, author="Mentor A"):
        """Add a note to the fixture ticket and return it."""
        return add_note(ticket_id, author, message, self.file_path)

    def test_adds_a_note_with_the_correct_id(self):
        ticket = self.make_ticket()

        note = self.add(ticket["id"], "Investigating switch ports")

        self.assertEqual(
            note,
            {
                "note_id": "N001",
                "author": "Mentor A",
                "message": "Investigating switch ports",
            },
        )

    def test_assigns_sequential_ids(self):
        ticket = self.make_ticket()

        self.add(ticket["id"], "First follow-up")
        second = self.add(ticket["id"], "Second follow-up", author="Mentor B")

        self.assertEqual(second["note_id"], "N002")

    def test_get_notes_returns_them_in_id_order(self):
        ticket = self.make_ticket()

        for number in range(1, 11):
            self.add(ticket["id"], f"Follow-up number {number}")

        notes = get_notes(ticket["id"], self.file_path)
        ids = [note["note_id"] for note in notes]

        self.assertEqual(ids, [f"N{number:03d}" for number in range(1, 11)])
        self.assertLess(ids.index("N002"), ids.index("N010"))

    def test_get_notes_is_empty_for_a_new_ticket(self):
        ticket = self.make_ticket()

        self.assertEqual(get_notes(ticket["id"], self.file_path), [])

    def test_trims_author_and_message_before_storing(self):
        ticket = self.make_ticket()

        note = self.add(
            ticket["id"],
            "  Switch ports replaced  ",
            author="  Mentor A  ",
        )

        self.assertEqual(note["author"], "Mentor A")
        self.assertEqual(note["message"], "Switch ports replaced")

    def test_the_note_is_written_to_the_file(self):
        ticket = self.make_ticket()

        self.add(ticket["id"], "Switch ports replaced")

        stored = self.stored_tickets()[0]["notes"]

        self.assertEqual(
            stored,
            [
                {
                    "note_id": "N001",
                    "author": "Mentor A",
                    "message": "Switch ports replaced",
                }
            ],
        )

    def test_notes_survive_a_reload(self):
        ticket = self.make_ticket()

        self.add(ticket["id"], "Switch ports replaced")

        reloaded = get_notes(ticket["id"], self.file_path)

        self.assertEqual(len(reloaded), 1)
        self.assertEqual(reloaded[0]["message"], "Switch ports replaced")


class TestRejectedNotesLeaveDataUnchanged(unittest.TestCase):
    """Acceptance case 06.

    A refused note has to prove two things: that it was refused, and that the
    failed attempt left nothing behind. assertRaises alone only shows the
    first, so the stored bytes are compared before and after.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def stored_bytes(self):
        """Return the raw file contents, for an exact comparison."""
        return self.file_path.read_bytes()

    def make_ticket(self):
        return create_and_save_ticket(
            "Wi-Fi is down",
            "Network",
            "high",
            12,
            self.file_path,
        )

    def add(self, ticket_id, message, author="Mentor A"):
        """Add a note to the fixture ticket and return it."""
        return add_note(ticket_id, author, message, self.file_path)

    def test_a_blank_author_is_rejected(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaises(ValueError):
            self.add(ticket["id"], "Switch ports replaced", author="   ")

        self.assertEqual(self.stored_bytes(), before)

    def test_a_non_text_author_is_rejected(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaises(ValueError):
            self.add(ticket["id"], "Switch ports replaced", author=42)

        self.assertEqual(self.stored_bytes(), before)

    def test_a_too_short_message_is_rejected(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "between 5 and 300"):
            self.add(ticket["id"], "abcd")

        self.assertEqual(self.stored_bytes(), before)
        self.assertEqual(get_notes(ticket["id"], self.file_path), [])

    def test_a_message_that_is_too_long_is_rejected(self):
        ticket = self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "between 5 and 300"):
            self.add(ticket["id"], "a" * 301)

        self.assertEqual(self.stored_bytes(), before)

    def test_a_rejected_note_does_not_consume_an_id(self):
        ticket = self.make_ticket()

        with self.assertRaises(ValueError):
            self.add(ticket["id"], "abcd")

        note = self.add(ticket["id"], "Switch ports replaced")

        self.assertEqual(note["note_id"], "N001")

    def test_an_unknown_ticket_is_rejected(self):
        self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "was not found"):
            self.add("T999", "Switch ports replaced")

        self.assertEqual(self.stored_bytes(), before)

    def test_a_non_text_ticket_id_is_rejected(self):
        self.make_ticket()
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "must be a non-empty string"):
            self.add(None, "Switch ports replaced")

        self.assertEqual(self.stored_bytes(), before)


class TestNotesAcrossTicketStatus(unittest.TestCase):
    """Acceptance case 07.

    The ticket is driven through the real workflow rather than having its
    status written directly, so these also check the two modules agree on
    what each status means.
    """

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def stored_bytes(self):
        """Return the raw file contents, for an exact comparison."""
        return self.file_path.read_bytes()

    def make_ticket(self):
        return create_and_save_ticket(
            "Wi-Fi is down",
            "Network",
            "high",
            12,
            self.file_path,
        )

    def add(self, ticket_id, message, author="Mentor A"):
        """Add a note to the fixture ticket and return it."""
        return add_note(ticket_id, author, message, self.file_path)

    def start(self, ticket):
        """Assign the ticket and move it to in_progress."""
        assign_staff(ticket["id"], "Grace", self.file_path)
        update_ticket_status(ticket["id"], "in_progress", self.file_path)

    def resolve(self, ticket):
        """Drive the ticket to resolved through the normal workflow."""
        self.start(ticket)
        update_ticket_status(ticket["id"], "resolved", self.file_path)

    def test_an_in_progress_ticket_accepts_a_note(self):
        ticket = self.make_ticket()
        self.start(ticket)

        note = self.add(ticket["id"], "Switch ports replaced")

        self.assertEqual(note["note_id"], "N001")

    def test_a_note_on_a_resolved_ticket_is_refused(self):
        ticket = self.make_ticket()
        self.resolve(ticket)
        before = self.stored_bytes()

        with self.assertRaisesRegex(ValueError, "Reopen the ticket"):
            self.add(ticket["id"], "Switch ports replaced")

        self.assertEqual(self.stored_bytes(), before)

    def test_resolved_tickets_keep_their_earlier_notes(self):
        ticket = self.make_ticket()
        self.add(ticket["id"], "Investigating ports")

        self.resolve(ticket)

        notes = get_notes(ticket["id"], self.file_path)

        self.assertEqual([note["note_id"] for note in notes], ["N001"])
        self.assertEqual(notes[0]["message"], "Investigating ports")

    def test_a_note_is_accepted_again_after_reopen(self):
        """The refusal lasts only while the ticket is resolved."""
        ticket = self.make_ticket()
        self.resolve(ticket)

        with self.assertRaises(ValueError):
            self.add(ticket["id"], "Too early")

        reopen_ticket(ticket["id"], self.file_path)

        note = self.add(ticket["id"], "Switch ports replaced")

        self.assertEqual(note["note_id"], "N001")

    def test_numbering_continues_after_reopen(self):
        """Reopening must not restart the sequence at N001."""
        ticket = self.make_ticket()
        self.add(ticket["id"], "Investigating ports")

        self.resolve(ticket)
        reopen_ticket(ticket["id"], self.file_path)
        self.add(ticket["id"], "Ports replaced", author="Mentor B")

        notes = get_notes(ticket["id"], self.file_path)
        ids = [note["note_id"] for note in notes]

        self.assertEqual(ids, ["N001", "N002"])


if __name__ == "__main__":
    unittest.main()
