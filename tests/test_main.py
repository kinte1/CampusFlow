
import unittest
from unittest.mock import patch

import main


class TestSearchTicketsMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=[
        "wifi",
        "network",
        "in_progress",
        "critical",
    ])
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
        )

        printed_output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("T001", printed_output)
        self.assertIn("Wi-Fi connection problem", printed_output)

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
        self, mock_search, mock_input, mock_print
    ):
        mock_search.return_value = []

        main.search_tickets_menu()

        mock_search.assert_called_once_with(
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
        )

        mock_print.assert_any_call("\nNo tickets found.")


class TestMainMenu(unittest.TestCase):
    @patch("builtins.print")
    @patch("builtins.input", side_effect=["9", "0"])
    @patch("main.search_tickets_menu")
    def test_main_menu_can_open_search(
        self, mock_search_menu, mock_input, mock_print
    ):
        main.main()

        mock_search_menu.assert_called_once()


if __name__ == "__main__":
    unittest.main()
