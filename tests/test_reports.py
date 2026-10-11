
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

    def create_ticket(self, title, urgency, affected_users):
        return create_and_save_ticket(
            title, "Network", urgency, affected_users, self.file_path
        )

    def test_empty_report_contains_all_counts(self):
        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["by_status"]["open"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)

    def test_report_counts_created_tickets(self):
        self.create_ticket("Wi-Fi problem", "high", 10)
        self.create_ticket("Printer problem", "low", 1)

        report = generate_report(self.file_path)

        self.assertEqual(report["total"], 2)
        self.assertEqual(report["by_status"]["open"], 2)
        self.assertEqual(report["by_priority"]["critical"], 1)
        self.assertEqual(report["by_priority"]["low"], 1)

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


if __name__ == "__main__":
    unittest.main()
