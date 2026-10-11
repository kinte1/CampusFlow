# AI Learning Log — CampusFlow

## Interaction 1: Choosing the correct module for ticket data

- **Problem:** Deciding where the workflow should get existing tickets.
- **AI suggestion:** Use `load_tickets()` and `save_tickets()` from `campusflow.storage`.
- **What I learned:** A module's responsibility is different from where its data is stored. The workflow module manages ticket operations, while the storage module handles JSON persistence.
- **My contribution:** I initially suggested keeping the ticket list inside `workflow.py`. I learned why loading the existing records is necessary to preserve data.

## Interaction 2: Importing storage functions

- **Problem:** Importing the functions needed for ticket assignment.
- **AI suggestion:** `from campusflow.storage import load_tickets, save_tickets`
- **What I learned:** Python imports let one module reuse functions from another module without duplicating their implementation.

## Interaction 3: Improving the learning approach

- **Problem:** Completing the project within a limited submission window.
- **AI suggestion:** Learn through short questions and incremental implementation.
- **My correction:** I asked to stop the question-and-answer approach and prioritize completing the required implementation because I had only one hour remaining.
- **Outcome:** The approach changed to implementing workflow management, reports, CLI integration, and tests, followed by documentation and Git collaboration.

## Reflection

AI helped explain module responsibilities, imports, persistence, and workflow design. I should review the generated code, run the tests, understand failures, and make corrections before submitting. I remain responsible for verifying that the implementation meets the project requirements.
