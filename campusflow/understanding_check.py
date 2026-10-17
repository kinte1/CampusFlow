
"""Engineering Understanding Check for CampusFlow."""


QUESTION_BANK = [
    {
        "question": (
            "T001 is open and unassigned. Someone tries to move it "
            "to in_progress. What should happen?"
        ),
        "options": {
            "A": "Accept the change.",
            "B": "Reject it and preserve all data.",
            "C": "Resolve the ticket automatically.",
            "D": "Remove the ticket.",
        },
        "answer": "B",
    },
    {
        "question": (
            "The application has zero tickets. What should the "
            "resolution percentage display?"
        ),
        "options": {
            "A": "Crash.",
            "B": "100%.",
            "C": "0%.",
            "D": "Divide by one without explanation.",
        },
        "answer": "C",
    },
    {
        "question": (
            "You filter by title='wifi', category='Network', "
            "and status='open'. Which records should match?"
        ),
        "options": {
            "A": "Records matching any one filter.",
            "B": "Records matching all supplied filters.",
            "C": "All Network records.",
            "D": "All open records.",
        },
        "answer": "B",
    },
    {
        "question": (
            "A resolved ticket receives an Add note request. "
            "What should happen?"
        ),
        "options": {
            "A": "Append the note anyway.",
            "B": "Delete the old notes.",
            "C": "Reject the request until the ticket is reopened.",
            "D": "Change the status silently.",
        },
        "answer": "C",
    },
    {
        "question": (
            "The JSON file contains two tickets with the same ID. "
            "What should loading do?"
        ),
        "options": {
            "A": "Keep both tickets.",
            "B": "Replace memory with the duplicates.",
            "C": "Reject the load without changing current memory.",
            "D": "Rename the IDs silently.",
        },
        "answer": "C",
    },
    {
        "question": (
            "A pull request changes validation but has no negative-case "
            "tests. What is the best review action?"
        ),
        "options": {
            "A": "Approve because the code runs.",
            "B": "Request focused tests and reasoning.",
            "C": "Merge immediately.",
            "D": "Ask AI to approve it.",
        },
        "answer": "B",
    },
]


def score_answers(bank, answers):
    """Return the score when one answer is provided per question."""
    if len(bank) != len(answers):
        raise ValueError("Provide one answer for every question.")

    score = 0

    for question, answer in zip(bank, answers):
        if answer.strip().upper() == question["answer"]:
            score += 1

    return score


def run():
    """Run the quiz, retry invalid choices, and collect two explanations."""
    answers = []

    print("\n=== Engineering Understanding Check ===")
    print("Choose A, B, C, or D for each question.\n")

    for number, question in enumerate(QUESTION_BANK, start=1):
        print(f"Q{number}. {question['question']}")

        for letter, option in question["options"].items():
            print(f"  {letter}. {option}")

        while True:
            answer = input("Your answer: ").strip().upper()

            if answer in {"A", "B", "C", "D"}:
                answers.append(answer)
                break

            print("Invalid choice. Please enter A, B, C, or D.")

        if answers[-1] == question["answer"]:
            print("Correct!\n")
        else:
            print(
                f"Not quite. The correct answer is "
                f"{question['answer']}.\n"
            )

    score = score_answers(QUESTION_BANK, answers)
    print(f"Final score: {score}/{len(QUESTION_BANK)}")

    print("\nExplain your reasoning for at least two answers.")
    explanations = []

    for number in (1, 2):
        explanation = input(
            f"Explanation for Q{number}: "
        ).strip()

        while not explanation:
            print("Please enter a short explanation.")
            explanation = input(
                f"Explanation for Q{number}: "
            ).strip()

        explanations.append(
            {
                "question_number": number,
                "answer": answers[number - 1],
                "explanation": explanation,
            }
        )

    print("\nYour explanations for mentor discussion:")
    for item in explanations:
        print(
            f"Q{item['question_number']} "
            f"(your answer: {item['answer']}): "
            f"{item['explanation']}"
        )

    return score


if __name__ == "__main__":
    run()
