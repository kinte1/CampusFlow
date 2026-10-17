
import tempfile
import unittest
from pathlib import Path

from campusflow.reports import generate_report
from campusflow.storage import create_and_save_ticket
from campusflow.workflow import assign_staff, update_ticket_status


class TestReports(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "tickets.json"

    def tearDown(self):
        self.temp_dir.cleanup()

    def create_ticket(
        self, title, urgency, affected_users, category="Network"
    ):
        return create_and_save_ticket(
            title,
            category,
            urgency,
            affected_users,
            self.file_path,
        )

    def test_empty_report_contains_all_counts(self):
        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["by_status"]["open"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)
        self.assertEqual(report["by_category"]["Network"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_pct"], 0.0)

    def test_report_counts_created_tickets(self):
        self.create_ticket("Wi-Fi problem", "high", 10)
        self.create_ticket("Printer problem", "low", 1)

        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_status"]["open"], 2)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["low"], 1)
        self.assertEqual(report["by_category"]["Network"], 2)
        self.assertEqual(report["unresolved"], 2)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_pct"], 0.0)

    def test_report_counts_resolved_tickets(self):
        ticket = self.create_ticket("Network problem", "medium", 3)
        assign_staff(ticket["id"], "Grace", self.file_path)
        update_ticket_status(
            ticket["id"], "in_progress", self.file_path
        )
        update_ticket_status(
            ticket["id"], "resolved", self.file_path
        )

        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 1)
        self.assertEqual(report["by_status"]["resolved"], 1)
        self.assertEqual(report["by_status"]["open"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["resolution_pct"], 100.0)

    def test_report_counts_tickets_by_category(self):
        self.create_ticket(
            "Wi-Fi problem", "high", 10, "Network"
        )
        self.create_ticket(
            "Laptop problem", "medium", 3, "Hardware"
        )
        self.create_ticket(
            "App problem", "low", 1, "Software"
        )
        self.create_ticket(
            "Other problem", "low", 1, "Other"
        )

        report = generate_report(self.file_path)

        self.assertEqual(report["by_category"]["Network"], 1)
        self.assertEqual(report["by_category"]["Hardware"], 1)
        self.assertEqual(report["by_category"]["Software"], 1)
        self.assertEqual(report["by_category"]["Other"], 1)

    def test_report_calculates_partial_resolution_percentage(self):
        first = self.create_ticket("First problem", "medium", 3)
        second = self.create_ticket("Second problem", "low", 1)
        self.create_ticket("Third problem", "high", 10)

        assign_staff(first["id"], "Grace", self.file_path)
        update_ticket_status(
            first["id"], "in_progress", self.file_path
        )
        update_ticket_status(
            first["id"], "resolved", self.file_path
        )

        assign_staff(second["id"], "Alex", self.file_path)
        update_ticket_status(
            second["id"], "in_progress", self.file_path
        )

        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 3)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["unresolved"], 2)
        self.assertAlmostEqual(report["resolution_pct"], 33.33, places=2)


if __name__ == "__main__":
    unittest.main()
