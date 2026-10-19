import copy
import tempfile
import unittest
from pathlib import Path

from campusflow.search import search_tickets, sort_by_priority_then_id
from campusflow.storage import create_and_save_ticket, load_tickets
from campusflow.workflow import assign_staff, update_ticket_status


class TestTicketSearch(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

        self.wifi = create_and_save_ticket(
            "Campus Wi-Fi connection problem",
            "Network",
            "high",
            12,
            self.file_path,
        )
        self.printer = create_and_save_ticket(
            "Printer paper jam",
            "Hardware",
            "low",
            1,
            self.file_path,
        )
        self.software = create_and_save_ticket(
            "Wi-Fi settings application bug",
            "Software",
            "medium",
            3,
            self.file_path,
        )

        assign_staff(self.wifi["id"], "Alex", self.file_path)
        update_ticket_status(
            self.wifi["id"], "in_progress", self.file_path
        )

        self.tickets = load_tickets(self.file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_title_search_ignores_case(self):
        results = search_tickets(self.tickets, "WI-FI")

        self.assertEqual(
            {ticket["id"] for ticket in results},
            {self.wifi["id"], self.software["id"]},
        )

    def test_title_search_matches_substring(self):
        results = search_tickets(self.tickets, "paper")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.printer["id"]],
        )

    def test_combined_filters_use_and_logic(self):
        results = search_tickets(
            self.tickets,
            "wi-fi",
            category="Network",
            status="in_progress",
            priority="critical",
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.wifi["id"]],
        )

    def test_filters_work_without_title_query(self):
        results = search_tickets(self.tickets, category="Hardware")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.printer["id"]],
        )

    def test_query_none_means_no_title_filter(self):
        results = search_tickets(self.tickets, query=None)

        self.assertEqual(len(results), len(self.tickets))

    def test_filters_ignore_case(self):
        results = search_tickets(self.tickets, category="network")

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.wifi["id"]],
        )

    def test_rejects_an_unknown_filter_value(self):
        with self.assertRaisesRegex(ValueError, "Unknown category"):
            search_tickets(self.tickets, category="Kitchen")

    def test_no_matches_returns_empty_list(self):
        results = search_tickets(self.tickets, "missing title")

        self.assertEqual(results, [])

    def test_search_does_not_modify_the_input_list(self):
        before = copy.deepcopy(self.tickets)

        search_tickets(
            self.tickets,
            "wi-fi",
            category="network",
            status="in_progress",
        )

        self.assertEqual(self.tickets, before)

    def test_results_are_sorted_by_priority_then_ticket_id(self):
        results = search_tickets(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [
                self.wifi["id"],
                self.software["id"],
                self.printer["id"],
            ],
        )


class TestSortByPriorityThenId(unittest.TestCase):
    def test_compares_ticket_ids_numerically(self):
        tickets = [
            {"id": "T010", "priority": "low"},
            {"id": "T2", "priority": "low"},
            {"id": "T001", "priority": "critical"},
        ]

        ordered = sort_by_priority_then_id(tickets)

        self.assertEqual(
            [ticket["id"] for ticket in ordered],
            ["T001", "T2", "T010"],
        )

    def test_returns_a_new_list(self):
        tickets = [{"id": "T001", "priority": "critical"}]

        ordered = sort_by_priority_then_id(tickets)

        self.assertIsNot(ordered, tickets)


if __name__ == "__main__":
    unittest.main()
