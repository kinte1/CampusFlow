
import unittest
from unittest.mock import patch

import main


class TestSearchTicketsMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch(
        "builtins.input",
        side_effect=["wifi", "network", "in_progress", "critical"],
    )
    @patch("main.search_tickets")
    def test_search_passes_filters_to_search_function(
        self, mock_search, mock_input, mock_print
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

        mock_search.assert_called_once_with(
            query="wifi",
            category="Network",
            status="in_progress",
            priority="critical",
            sort_by_priority=False,
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("Wi-Fi connection problem", printed_output)

    @patch("builtins.print")
    @patch(
        "builtins.input",
        side_effect=[
            " ",
            "invalid",
            "hardware",
            "wrong",
            "open",
            "unknown",
            "high",
        ],
    )
    @patch("main.search_tickets")
    def test_invalid_filters_are_retried_and_normalized(
        self, mock_search, mock_input, mock_print
    ):
        mock_search.return_value = []

        main.search_tickets_menu()

        mock_search.assert_called_once_with(
            query="",
            category="Hardware",
            status="open",
            priority="high",
            sort_by_priority=False,
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("No tickets found.", printed_output)

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["", "", "", ""])
    @patch("main.search_tickets")
    def test_blank_filters_are_allowed(
        self, mock_search, mock_input, mock_print
    ):
        mock_search.return_value = []

        main.search_tickets_menu()

        mock_search.assert_called_once_with(
            query="",
            category=None,
            status=None,
            priority=None,
            sort_by_priority=False,
        )


class TestNoteMenus(unittest.TestCase):
    @patch("builtins.print")
    @patch(
        "builtins.input",
        side_effect=["T001", "Alex", "Checked the network cable"],
    )
    @patch("main.add_note")
    def test_add_note_menu_saves_and_displays_note_id(
        self, mock_add_note, mock_input, mock_print
    ):
        mock_add_note.return_value = {
            "note_id": "N001",
            "author": "Alex",
            "message": "Checked the network cable",
        }

        main.add_follow_up_note_menu()

        mock_add_note.assert_called_once_with(
            "T001", "Alex", "Checked the network cable"
        )
        mock_print.assert_any_call("Added note N001 to ticket T001.")

    @patch("builtins.print")
    @patch("builtins.input", return_value="T001")
    @patch("main.get_notes")
    def test_view_notes_menu_displays_notes(
        self, mock_get_notes, mock_input, mock_print
    ):
        mock_get_notes.return_value = [
            {
                "note_id": "N001",
                "author": "Alex",
                "message": "Checked the network cable",
            }
        ]

        main.view_ticket_notes_menu()

        mock_get_notes.assert_called_once_with("T001")

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("N001", printed_output)
        self.assertIn("Alex", printed_output)
        self.assertIn("Checked the network cable", printed_output)

    @patch("builtins.print")
    @patch("builtins.input", return_value="T001")
    @patch("main.get_notes", return_value=[])
    def test_view_notes_menu_handles_empty_notes(
        self, mock_get_notes, mock_input, mock_print
    ):
        main.view_ticket_notes_menu()

        mock_print.assert_any_call("No follow-up notes found.")


class TestPrioritySearchMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["wifi", "", "", ""])
    @patch("main.search_tickets")
    def test_priority_search_uses_filters_and_displays_results(
        self, mock_search, mock_input, mock_print
    ):
        mock_search.return_value = [
            {
                "id": "T002",
                "title": "Wi-Fi outage",
                "category": "Network",
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            }
        ]

        main.search_by_priority_menu()

        mock_search.assert_called_once_with(
            query="wifi",
            category=None,
            status=None,
            priority=None,
            sort_by_priority=True,
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("PRIORITY-SORTED SEARCH RESULTS", printed_output)
        self.assertIn("T002", printed_output)


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
    @patch("main.add_follow_up_note_menu")
    def test_main_menu_can_open_add_note(
        self, mock_add_note_menu, mock_input, mock_print
    ):
        main.main()
        mock_add_note_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["11", "0"])
    @patch("main.view_ticket_notes_menu")
    def test_main_menu_can_open_view_notes(
        self, mock_view_notes_menu, mock_input, mock_print
    ):
        main.main()
        mock_view_notes_menu.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["12", "0"])
    @patch("main.search_by_priority_menu")
    def test_main_menu_can_open_priority_search(
        self, mock_priority_search, mock_input, mock_print
    ):
        main.main()
        mock_priority_search.assert_called_once()

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["13", "0"])
    @patch("main.run_understanding_check")
    def test_main_menu_can_open_understanding_check(
        self, mock_understanding_check, mock_input, mock_print
    ):
        main.main()
        mock_understanding_check.assert_called_once()


if __name__ == "__main__":
    unittest.main()
