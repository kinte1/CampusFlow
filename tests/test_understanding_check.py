
import unittest
from unittest.mock import patch

from campusflow.understanding_check import (
    QUESTION_BANK,
    run,
    score_answers,
)


class TestUnderstandingCheck(unittest.TestCase):
    def test_question_bank_contains_six_questions(self):
        self.assertEqual(len(QUESTION_BANK), 6)

    def test_all_correct_answers_score_six(self):
        answers = [
            question["answer"] for question in QUESTION_BANK
        ]

        self.assertEqual(score_answers(QUESTION_BANK, answers), 6)

    def test_all_wrong_answers_score_zero(self):
        answers = ["A", "A", "A", "A", "A", "A"]

        self.assertEqual(score_answers(QUESTION_BANK, answers), 0)

    def test_mixed_answers_score_correctly(self):
        answers = ["B", "C", "A", "C", "C", "B"]

        self.assertEqual(score_answers(QUESTION_BANK, answers), 5)

    def test_answers_are_case_insensitive(self):
        answers = ["b", "c", "b", "c", "c", "b"]

        self.assertEqual(score_answers(QUESTION_BANK, answers), 6)

    def test_rejects_incomplete_answer_list(self):
        with self.assertRaises(ValueError):
            score_answers(QUESTION_BANK, ["B", "C"])

    def test_invalid_choice_retries_until_valid(self):
        user_inputs = [
            "X",
            "B",
            "C",
            "B",
            "C",
            "C",
            "B",
            "First explanation",
            "Second explanation",
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with patch("builtins.print") as mocked_print:
                score = run()

        self.assertEqual(score, 6)

        printed_text = " ".join(
            str(call) for call in mocked_print.call_args_list
        )
        self.assertIn("Invalid choice", printed_text)

    def test_empty_explanation_is_rejected(self):
        user_inputs = [
            "B",
            "C",
            "B",
            "C",
            "C",
            "B",
            "",
            "First explanation",
            "Second explanation",
        ]

        with patch("builtins.input", side_effect=user_inputs):
            with patch("builtins.print") as mocked_print:
                score = run()

        self.assertEqual(score, 6)

        printed_text = " ".join(
            str(call) for call in mocked_print.call_args_list
        )
        self.assertIn(
            "Please enter a short explanation",
            printed_text,
        )


if __name__ == "__main__":
    unittest.main()
