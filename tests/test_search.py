import tempfile
import unittest
from pathlib import Path

from campusflow.search import search_tickets
from campusflow.storage import create_and_save_ticket
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

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_title_search_ignores_case(self):
        results = search_tickets(
            "WI-FI",
            file_path=self.file_path,
        )

        self.assertEqual(
            {ticket["id"] for ticket in results},
            {self.wifi["id"], self.software["id"]},
        )

    def test_title_search_matches_substring(self):
        results = search_tickets(
            "paper",
            file_path=self.file_path,
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.printer["id"]],
        )

    def test_combined_filters_use_and_logic(self):
        results = search_tickets(
            "wi-fi",
            category="Network",
            status="in_progress",
            priority="critical",
            file_path=self.file_path,
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.wifi["id"]],
        )

    def test_filters_work_without_title_query(self):
        results = search_tickets(
            category="Hardware",
            file_path=self.file_path,
        )

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [self.printer["id"]],
        )

    def test_no_matches_returns_empty_list(self):
        results = search_tickets(
            "missing title",
            file_path=self.file_path,
        )

        self.assertEqual(results, [])

    def test_search_does_not_modify_ticket_records(self):
        before = search_tickets(file_path=self.file_path)

        search_tickets(
            "wi-fi",
            category="Network",
            file_path=self.file_path,
        )

        after = search_tickets(file_path=self.file_path)
        self.assertEqual(after, before)

    def test_results_are_sorted_by_priority_then_ticket_id(self):
        results = search_tickets(file_path=self.file_path)

        self.assertEqual(
            [ticket["id"] for ticket in results],
            [
                self.wifi["id"],
                self.software["id"],
                self.printer["id"],
            ],
        )


if __name__ == "__main__":
    unittest.main()