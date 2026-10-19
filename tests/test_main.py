
import unittest
from unittest.mock import patch

import main


TICKETS = [{"id": "T900"}]

NOTE = {
    "note_id": "N001",
    "author": "Mentor A",
    "message": "Router rebooted",
}

DISPLAY_TICKET = {
    "id": "T900",
    "title": "Wi-Fi problem",
    "category": "Network",
    "priority": "low",
    "status": "open",
    "assigned_to": None,
}


class TestSearchTicketsMenu(unittest.TestCase):
    @patch("main.load_tickets", return_value=TICKETS)
    @patch("builtins.print")
    @patch("builtins.input", side_effect=[
        "wifi",
        "network",
        "in_progress",
        "critical",
    ])
    @patch("main.search_tickets")
    def test_search_passes_filters_to_search_function(
        self, mock_search, mock_input, mock_print, mock_load_tickets
    ):
        mock_search.return_value = [
            {
                "id": "T001",
                "title": "Wi-Fi connection problem",
                "category": "Network",
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "Alex",
            }
        ]

        main.search_tickets_menu()

        mock_load_tickets.assert_called_once_with()

        mock_search.assert_called_once_with(
            TICKETS,
            query="wifi",
            category="Network",
            status="in_progress",
            priority="critical",
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("T001", printed_output)
        self.assertIn("Wi-Fi connection problem", printed_output)

    @patch("main.load_tickets", return_value=TICKETS)
    @patch("builtins.print")
    @patch("builtins.input", side_effect=[
        " ",
        "invalid",
        "hardware",
        "wrong",
        "open",
        "unknown",
        "high",
    ])
    @patch("main.search_tickets")
    def test_invalid_filters_are_retried_and_normalized(
        self, mock_search, mock_input, mock_print, mock_load_tickets
    ):
        mock_search.return_value = []

        main.search_tickets_menu()

        mock_search.assert_called_once_with(
            TICKETS,
            query="",
            category="Hardware",
            status="open",
            priority="high",
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("Invalid category", printed_output)
        self.assertIn("Invalid status", printed_output)
        self.assertIn("Invalid priority", printed_output)

    @patch("main.load_tickets", return_value=TICKETS)
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["", "", "", ""])
    @patch("main.search_tickets")
    def test_blank_filters_are_allowed(
        self, mock_search, mock_input, mock_print, mock_load_tickets
    ):
        mock_search.return_value = []

        main.search_tickets_menu()

        mock_search.assert_called_once_with(
            TICKETS,
            query="",
            category=None,
            status=None,
            priority=None,
        )

        mock_print.assert_any_call("\nNo tickets found.")


class TestSortedSearchMenu(unittest.TestCase):
    @patch("main.sort_by_priority_then_id", return_value=[DISPLAY_TICKET])
    @patch("main.search_tickets", return_value=[DISPLAY_TICKET])
    @patch("main.load_tickets", return_value=TICKETS)
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["", "", "", ""])
    def test_applies_priority_sort_to_the_results(
        self, mock_input, mock_print, mock_load, mock_search, mock_sort
    ):
        main.sorted_search_menu()

        mock_load.assert_called_once_with()
        mock_search.assert_called_once_with(
            TICKETS,
            query="",
            category=None,
            status=None,
            priority=None,
        )
        mock_sort.assert_called_once_with([DISPLAY_TICKET])

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("SORTED BY PRIORITY", printed_output)
        self.assertIn("T900", printed_output)


class TestAddNoteMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=[
        "T001",
        "Mentor A",
        "Router rebooted",
    ])
    @patch("main.add_note", return_value=NOTE)
    def test_add_note_menu_calls_add_note(
        self, mock_add_note, mock_input, mock_print
    ):
        main.add_note_menu()

        mock_add_note.assert_called_once_with(
            "T001", "Mentor A", "Router rebooted"
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("N001", printed_output)
        self.assertIn("T001", printed_output)


class TestViewNotesMenu(unittest.TestCase):
    NOTES = [
        {"note_id": "N001", "author": "Mentor A", "message": "First"},
        {"note_id": "N002", "author": "Mentor B", "message": "Second"},
    ]

    @patch("builtins.print")
    @patch("builtins.input", return_value="T001")
    @patch("main.get_notes", return_value=NOTES)
    def test_displays_each_note_in_order(
        self, mock_get_notes, mock_input, mock_print
    ):
        main.view_notes_menu()

        mock_get_notes.assert_called_once_with("T001")

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("N001", printed_output)
        self.assertIn("First", printed_output)
        self.assertIn("N002", printed_output)
        self.assertIn("Second", printed_output)

    @patch("builtins.print")
    @patch("builtins.input", return_value="T001")
    @patch("main.get_notes", return_value=[])
    def test_reports_when_there_are_no_notes(
        self, mock_get_notes, mock_input, mock_print
    ):
        main.view_notes_menu()

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("No notes found", printed_output)


class TestMainMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["9", "0"])
    @patch("main.search_tickets_menu")
    def test_main_menu_can_open_search(
        self, mock_search_menu, mock_input, mock_print
    ):
        main.main()

        mock_search_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["10", "0"])
    @patch("main.add_note_menu")
    def test_main_menu_can_open_add_note(
        self, mock_add_note_menu, mock_input, mock_print
    ):
        main.main()

        mock_add_note_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["11", "0"])
    @patch("main.view_notes_menu")
    def test_main_menu_can_open_view_notes(
        self, mock_view_notes_menu, mock_input, mock_print
    ):
        main.main()

        mock_view_notes_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["12", "0"])
    @patch("main.sorted_search_menu")
    def test_main_menu_can_open_sorted_search(
        self, mock_sorted_search_menu, mock_input, mock_print
    ):
        main.main()

        mock_sorted_search_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["10", "0"])
    @patch("main.add_note_menu", side_effect=ValueError(
        "Ticket T999 was not found."
    ))
    def test_a_note_error_is_reported_and_the_menu_continues(
        self, mock_add_note_menu, mock_input, mock_print
    ):
        main.main()

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("Error: Ticket T999 was not found.", printed_output)


if __name__ == "__main__":
    unittest.main()
