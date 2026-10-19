import unittest
from unittest.mock import patch

import main


class TestUnderstandingCheckCLI(unittest.TestCase):
    @patch("builtins.input", side_effect=["13", "0"])
    @patch("main.run_understanding_check")
    def test_menu_opens_understanding_check(
        self, mock_quiz, mock_input
    ):
        main.main()
        mock_quiz.assert_called_once()


if __name__ == "__main__":
    unittest.main()
