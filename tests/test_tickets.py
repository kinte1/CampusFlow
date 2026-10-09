import unittest

from campusflow.tickets import (
    validate_title,
    validate_category,
    validate_urgency,
    validate_affected_users,
    calculate_priority,
    create_ticket,
)


class TestValidateTitle(unittest.TestCase):
    def test_trims_extra_spaces(self):
        self.assertEqual(
            validate_title("  Wi-Fi is not working  "),
            "Wi-Fi is not working",
        )

    def test_rejects_empty_title(self):
        with self.assertRaises(ValueError):
            validate_title("   ")

    def test_rejects_non_text_title(self):
        with self.assertRaises(ValueError):
            validate_title(123)


class TestValidateCategory(unittest.TestCase):
    def test_normalizes_category(self):
        self.assertEqual(validate_category("network"), "Network")

    def test_accepts_all_categories(self):
        for category in ["Network", "Hardware", "Software", "Other"]:
            with self.subTest(category=category):
                self.assertEqual(validate_category(category), category)

    def test_rejects_invalid_category(self):
        with self.assertRaises(ValueError):
            validate_category("Electricity")


class TestValidateUrgency(unittest.TestCase):
    def test_normalizes_urgency(self):
        self.assertEqual(validate_urgency("HIGH"), "high")

    def test_accepts_all_urgency_levels(self):
        for urgency in ["low", "medium", "high"]:
            with self.subTest(urgency=urgency):
                self.assertEqual(validate_urgency(urgency), urgency)

    def test_rejects_invalid_urgency(self):
        with self.assertRaises(ValueError):
            validate_urgency("urgent")


class TestValidateAffectedUsers(unittest.TestCase):
    def test_accepts_positive_integer(self):
        self.assertEqual(validate_affected_users(10), 10)

    def test_rejects_zero(self):
        with self.assertRaises(ValueError):
            validate_affected_users(0)

    def test_rejects_negative_integer(self):
        with self.assertRaises(ValueError):
            validate_affected_users(-3)

    def test_rejects_text(self):
        with self.assertRaises(ValueError):
            validate_affected_users("10")

    def test_rejects_boolean(self):
        with self.assertRaises(ValueError):
            validate_affected_users(True)


class TestCalculatePriority(unittest.TestCase):
    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_high_priority_from_urgency(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_high_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_medium_priority_from_urgency(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")

    def test_medium_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 1), "low")


class TestCreateTicket(unittest.TestCase):
    def test_creates_valid_ticket(self):
        ticket = create_ticket(
            "T001",
            "Wi-Fi is not working",
            "network",
            "high",
            12,
        )

        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["title"], "Wi-Fi is not working")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["affected_users"], 12)
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_rejects_invalid_category(self):
        with self.assertRaises(ValueError):
            create_ticket(
                "T002",
                "Printer problem",
                "Electricity",
                "medium",
                3,
            )

    def test_rejects_blank_ticket_id(self):
        with self.assertRaises(ValueError):
            create_ticket(
                "   ",
                "Printer problem",
                "Hardware",
                "low",
                1,
            )


if __name__ == "__main__":
    unittest.main()
