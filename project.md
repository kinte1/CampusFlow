CAMPUSFLOW NEXT
Guided Reliability, Search & Engineering Quality Sprint
ENGINEER A + ENGINEER B
You built a first version of CampusFlow and received a progressing audit assessment. Your next challenge is not to start over or generate a bigger app with AI. It is to turn your EXISTING Python command-line project into software that another engineer can trust, test, understand, and maintain.
This guide is appropriate for the progressing audit band (70–84/100). Audit observations are preliminary peer feedback, not proof of individual inability. Every pair must inspect their own repository first and choose improvement tasks supported by evidence. Your mentors will judge what you can now demonstrate.
01 | THE REAL-WORLD MISSION
Campus support staff use CampusFlow to register problems with Wi-Fi, laptops, software installations and learning tools. The first version tracked tickets, urgency, priority, status, assignment and basic reports. Now the campus has new needs: staff must find tickets quickly, leave structured follow-up notes, prevent invalid ticket changes, load records safely and provide clear reports for the Head of Campus.
Your engineering goal
Upgrade the EXISTING CampusFlow repository into CampusFlow Next, a reliable Python CLI with stronger validation, controlled ticket notes, multi-filter search, trustworthy reports, safe JSON persistence, tests, and thoughtful peer review. Keep the application within the original learning boundaries: Python standard library, functions, dictionaries/lists, JSON, exception handling, unittest, command-line interaction, AI-supported study and GitHub.
Do NOT introduce Django, React, external databases, web APIs, authentication systems, cloud infrastructure or paid AI integrations. Those are outside this exercise. This is a quality-and-reliability upgrade, not a new product stack.
Features from the original project you MUST preserve
Keep: ticket creation; priority based on urgency and affected users; assignment; status transitions (open → in_progress → resolved; reopening resolved → open); Open Work Queue; status/priority analytics; JSON save/load; CLI and tests. Preserve priority rule order: critical when high urgency AND affected_users >=10; otherwise high when high urgency OR affected_users >=10; otherwise medium when medium urgency OR affected_users >=3; otherwise low.
Original Open Work Queue must show only OPEN tickets, priority order critical > high > medium > low, with earlier numeric ticket IDs first for ties. An in_progress or resolved ticket must not appear in this original queue.
02 | DIAGNOSTIC: WHAT TO REVISIT BEFORE CODING
Before building anything new, run the old application at its audited commit and execute its tests. Write a short 'baseline-check.md' with the run command, passing/failing results, three inputs you tested, and what your audit said needed improvement. Do not label a peer-reported bug as confirmed until you reproduce it.
Concept 1 — Python functions and contracts
REVISIT: parameters, return values, None, dictionaries, modular design, separation of input/output from business rules. LEARN NEXT: function contracts and invariants (what must be true before and after a function executes). PRACTICE: on paper describe a function's valid inputs, outputs, failure mode and side effects.
CHECK YOURSELF: What is easier to test—one function that reads input, edits a dictionary, prints text and saves JSON, or four small functions with separate jobs? Why?
Concept 2 — conditions, types and validation
REVISIT: if/elif/else ordering, booleans, equality vs identity, positive integers, string strip/casefold, ValueError and TypeError. LEARN NEXT: validate-before-mutate and defensive programming. PRACTICE: explain why isinstance(True, int) is true in Python and how to disallow booleans for affected_users.
CHECK YOURSELF: If an invalid action returns an error, how will you prove the ticket dictionary did not change at all?
Concept 3 — lists, dictionaries, iteration, sorting
REVISIT: loops, comprehensions, dictionary get, sorting with key functions. LEARN NEXT: composing multiple filters, stable/deterministic ordering, and counting without double-counting. PRACTICE: filter a three-ticket unrelated sample by two conditions and compare expected order with Python output.
CHECK YOURSELF: Why might sorting by the text ID 'T10' before 'T2' give a wrong tie-breaker? How will your program handle it?
Concept 4 — files and error handling
REVISIT: json.dump, json.load, with open(), try/except, file paths. LEARN NEXT: parse-and-validate-before-replacing memory, rejecting duplicate IDs and malformed records, and ensuring reload continues ID generation. PRACTICE: create a small book JSON file, corrupt it on purpose and observe JSONDecodeError.
CHECK YOURSELF: If loading a file fails halfway, should a previously valid in-memory collection be partly overwritten?
Concept 5 — unittest and bug investigation
REVISIT: test cases, assertEqual, assertRaises, setUp, running unittest discovery. LEARN NEXT: regression testing, boundary inputs, negative tests, temporary files and checking state before/after failure. PRACTICE: make a failing test for a simple unrelated function and use the failure to find the bug.
CHECK YOURSELF: Could a suite of 30 tests pass while a crucial business rule is never tested? Explain.
Concept 6 — Git collaboration and engineering communication
REVISIT: branch, staging, commit, remote, merge, PR reviews. LEARN NEXT: changes scoped to a task, objective acceptance criteria, review chronology, helpful feedback and reproducibility from a fresh clone. PRACTICE: review a short diff and identify one missing test or incorrect assumption.
CHECK YOURSELF: How does 'LGTM' differ from a review comment that names a specific edge case and requests a test?
Concept 7 — using AI like an engineer
REVISIT: prompting for explanations, examples, debugging, not blindly copying output. LEARN NEXT: challenging suggestions against documentation and tests, comparing two designs, documenting decisions. PRACTICE: ask AI to explain casefold versus lower on a small unrelated example; inspect its answer with your own test.
CHECK YOURSELF: What evidence would convince you an AI suggestion is wrong or unsafe?
03 | PROJECT DESIGN AND ACCEPTANCE CONTRACT
Ticket schema
Keep the original fields id, title, category, urgency, affected_users, priority, status and assigned_to. ADD one field: notes, initially an empty list. Each note is a dictionary with note_id, author and message. Use simple per-ticket note IDs N001, N002, etc.; identify a note by its ticket ID plus note ID.
A new note may be added only when ticket status is open or in_progress. A resolved ticket cannot accept notes or assignment changes unless it is reopened through the original valid workflow. Notes are preserved through resolve and reopen.
Requirement A — Correct validation and status safety
Use centralized validation helpers. Category must be Network, Hardware, Software or Other (you may normalize input before storing these canonical values). Urgency must be low, medium or high. Title is not blank after trimming. affected_users must be a strictly positive integer; reject floats, strings and bools masquerading as integers. A ticket ID must be unique and valid. Assignment requires a nonempty staff label. Do not let an unassigned open ticket move to in_progress.
Invalid create, assignment, status or note actions must leave the entire ticket collection unchanged. The CLI should show friendly feedback instead of crashing. Resolve and reopen should obey the old workflow; failed operations must not silently change data.
Requirement B — Structured follow-up notes
Add 'Add Follow-up Note' and 'View Ticket Notes' to the CLI. Only open or in_progress tickets accept a new note. The author label cannot be blank. Message length must be 5–300 characters after trimming. A rejected note must not consume a note ID. The user can read all notes for a ticket in ID order. Saving and reloading must preserve all notes and the next note ID.
Example: open T001 → add N001 author 'Mentor A', message 'Wi-Fi router reboot attempted' → add N002 'Mentor B', 'Investigating switch ports' → resolve T001 → attempt N003 (reject) → reopen T001 → N003 may now be created. Resolved tickets retain earlier notes.
Requirement C — Search and combined filtering
Implement a read-only Search Tickets CLI view. User may search titles with case-insensitive substring matching and optional filters for category, status and priority. Filters must work together: if supplied, ALL must match. Empty filters mean 'do not filter by that field'. Invalid filter options should re-prompt. Search must not modify ticket records. Display ID, title, category, priority, status and assigned_to.
Example: search 'wifi' + category Network + status open returns matching open network tickets only. 'WI-FI' and 'wi-fi' match each other, assuming the same punctuation. Do not promise fuzzy spelling correction; substring matching is enough.
Requirement D — Trustworthy quality insights
Enhance Reports with: total tickets; counts by status; counts by priority; counts by category; unresolved count (open + in_progress); resolved count; and resolution percentage (resolved / total * 100). An empty dataset must report 0% without division errors. Reopened tickets count according to their CURRENT status. Do not double-count across statuses.
The current version's original Open Work Queue remains unchanged. Add one separate optional view that sorts ticket-search results by priority then ticket ID. Never silently replace the existing Open Work Queue with a different status filter.
Requirement E — Safe and reproducible JSON
Your extended data file must save all ticket fields including notes. On loading, validate the full collection first: structure, required keys, ID uniqueness, category/urgency/priority consistency, legal statuses, note shapes and uniqueness per ticket. If any record is invalid, clearly reject the load and keep current memory unchanged. After a successful reload, the next ticket/note IDs must not collide.
Maintain whichever existing JSON envelope or list format your project uses; describe the format in README. You may refactor internally, but do not discard old working tickets. If you change file format incompatibly, include a small documented migration or clearly explain supported versions and protect source data. No actual personal information or passwords are needed—use dummy fellow/operator labels.
04 | TWO ENGINEERS: SEPARATE RESPONSIBILITIES
ENGINEER A — Ticket Safety and Storage Engineer
You OWN: common validation helpers; protections around assignment/status mutations; note data validation; JSON save/load/reload and ID continuity. Suggested functions: validate_ticket(...), can_transition(...), load_tickets(path), save_tickets(path), next_ticket_id(...), next_note_id(ticket). Coordinate interfaces with Engineer B before coding.
A must implement the business/data layer for notes and expose a documented add_note(ticket_id, author, message) function. Engineer B owns the CLI interaction and display for these functions. Agree on error response conventions (exceptions or explicit results); do not combine inconsistent patterns.
Engineer A milestones
A1. Run and document old tests. A2. Write a test proving unassigned ticket cannot enter In Progress. A3. Reject invalid affected_users, invalid categories and mutation of resolved tickets. A4. Add an open-ticket note, reject a resolved-ticket note and prove invalid actions change nothing. A5. Load corrupted/duplicate-ID JSON without erasing memory. A6. Restart and generate the correct next IDs.
Questions for Engineer A
1. What data is validated before any mutation? 2. What is a ticket invariant? 3. Why doesn't a successful print statement prove data integrity? 4. Why do you validate JSON after decoding? 5. How do you prevent partial changes if one entry is invalid? 6. How do you test both a thrown error and unchanged state? 7. Which AI recommendation did you accept only after verification?
ENGINEER B — Search, Reporting and CLI Engineer
You OWN: the user-facing search/filter interface, analytics, note-entry and note-view menus using A's APIs, clear input/retry loops, and a small CLI Engineering Understanding Check. Separate business logic from print/input where practical so search and quiz functions are independently testable.
Engineer B milestones
B1. Build title substring search with casefold. B2. Combine category/status/priority filters correctly. B3. Display reports and handle no tickets. B4. Create CLI menu for add/view notes using A's functions and helpful failure messages. B5. Build the interactive understanding check. B6. Write tests for combined filters, report totals, invalid CLI choices and quiz scoring.
Questions for Engineer B
1. Why should search not edit the collection? 2. When combining filters, should you use AND or OR? 3. Why does an empty report need special handling? 4. How does an in_progress ticket affect unresolved count? 5. Why is a resolved ticket forbidden from receiving new notes? 6. How do you test CLI behavior without repeatedly typing manually? 7. Which change from your partner's PR review improved your work?
Shared responsibilities and pair working agreement
Both engineers must agree on function contracts; author real source code and tests; document their learning; review the other engineer's code; and understand how the modules integrate. Engineer A is not the team lead by default. Engineer B is not just a presentation assistant. Responsibility is individual, delivery is shared.
05 | CLI UNDERSTANDING CHECK — BUILD AND ANSWER IT
Implement an interactive menu called 'Engineering Understanding Check' containing SIX short multiple-choice scenario questions on your own application's behaviour. Inputs must be A/B/C/D (invalid choices trigger retry). Keep the question bank separate from the scoring logic. Award one point per correct response (0–6) and show a final score. Ask for a short explanation of at least TWO answers, saved in a local learning note or displayed for mentor discussion. Do not auto-grade explanations as correct just because a keyword matches.
Question bank to implement — do not hard-code scoring into the menu loop
Q1. Ticket T001 is open and unassigned. A user tries to move it to in_progress. A Accept | B Reject and preserve all data | C Resolve it automatically | D Remove ticket.
Q2. The app has zero tickets. What should resolution percentage display? A Crash | B 100% | C 0% | D Divide by one without explanation.
Q3. Filter title='wifi', category='Network', status='open'. Which records should match? A Any record matching one filter | B Only records matching all supplied filters | C All network records | D All open records.
Q4. A resolved ticket receives 'Add note'. What should happen? A Append anyway | B Delete old notes | C Reject until reopened | D Change status silently.
Q5. The JSON file includes two tickets with the same ID. What should load do? A Keep both | B Replace memory with duplicates | C Reject the load without changing current memory | D Rename IDs silently.
Q6. A PR changes validation but has no negative-case tests. Best review action? A Approve because it runs | B Request focused tests and reasoning | C Merge immediately | D Ask AI to approve it.
The CLI may give learners post-question feedback after recording their first choice, but the score must reflect their actual submitted answers. Each engineer must take the quiz independently during demonstration and explain why two answers are correct using examples from their code.
06 | THE TEST LAB: PROVE IT WORKS
Write at least FOURTEEN meaningful automated unittest tests for the integrated application, with AT LEAST FIVE authored by each engineer. Include original CampusFlow regression tests and these targeted scenarios. Tests must run in a fresh clone using python -m unittest discover -s tests -v.
Required acceptance cases
01. Original priority calculation still respects rule precedence. 02. Unassigned open → in_progress rejected with unchanged data. 03. Resolved ticket assignment mutation rejected. 04. Invalid affected_users (0, negative, float, boolean) rejected. 05. Valid note added and note ID correct. 06. Blank/too-short note rejected without consuming ID. 07. Note on resolved ticket rejected; note after reopen accepted. 08. Search title ignores case, matching substring. 09. Combined search filters use AND. 10. Empty report returns 0%, no crash. 11. Report counts agree with known fixture after resolve/reopen. 12. Saving/loading preserves notes and next IDs. 13. Corrupt JSON or duplicated ticket ID rejected without state loss. 14. CLI understanding check rejects invalid answer and scores correctly.
Invent two extra bug-hunter tests
Each engineer must devise one previously unlisted edge case for the other's module. Write: initial state; input; expected result; actual result; test name; any code change made. The best test makes an important invariant visible.
07 | AI LEARNING: NOT JUST GENERATING CODE
Each engineer documents at least TWO meaningful AI learning cycles in docs/ai-learning-log.md. Every cycle must include the original concept gap, exact question asked, summary of AI guidance, a tiny unrelated experiment, independent verification through tests/docs, and the final engineering decision. At least ONE cycle per TEAM must document a changed/rejected AI suggestion after evidence review; do not invent a 'hallucination' just to fill the field.
Useful learning questions to ask AI
'Explain how to validate a dictionary BEFORE mutating it, using a book library example, then quiz me.' 'Compare casefold and lower for search; suggest test cases but do not implement my project.' 'Here is my failing unittest assertion; help me identify two possible causes without rewriting the function.' 'Why might json.load succeed but return unsafe or inconsistent business data?' 'Read this small PR diff and propose overlooked edge-case tests; I will independently verify each suggestion.'
Personal reflection to write after using AI
What did I believe before? What did AI explain? Which claim did I test? What did the test show? What did I change in MY code? Which test guards that learning against future regression? Could I explain this choice without AI in the room?
08 | PROFESSIONAL GIT AND PR WORKFLOW
Use the existing GitHub repository and continue from the old main branch. First open GitHub Issues for A: ticket validation/notes/storage; and B: combined search/reports/CLI knowledge. Branches can be feat/21-validation-and-notes and feat/22-search-and-insights; use real issue IDs where possible. Each engineer authors at least ONE substantial PR, with code and tests, and REVIEWS the other's PR before merge.
Commit examples: fix: reject illegal ticket assignment; feat: add structured follow-up notes; feat: combine search filters; test: cover invalid JSON reload; docs: explain fresh-clone setup. Make at least TWO focused commits per engineer. No direct feature commits to main and no approving your own PR.
Mandatory peer review evidence
Both partners must read the other's diff; run relevant tests; leave at least TWO specific review observations or questions; address blocking feedback; rerun tests; and record approval BEFORE merge. Review comments should cite a particular file, behaviour, or test. 'LGTM' alone is not meaningful review evidence.
If branch protection is available, set main to require PR approval. If not available, retain the PR timeline showing partner reviews and mentor-verified merges. After each merge, synchronize branches and run the integrated suite again.
09 | EIGHT-HOUR GUIDED WORK PLAN
SESSION 1 — Diagnose, learn and build (4 hours)
00:00–00:30: inspect audit findings and run old tests; record baseline. 00:30–01:10: revisit Python validation, JSON and search using AI + personal mini-experiments. 01:10–01:30: define contracts and GitHub issues; create branches. 01:30–04:00: Engineer A and B implement core tasks and initial tests independently, coordinating shared interfaces.
SESSION 2 — Test, review and defend (4 hours)
00:00–01:20: finish notes, search, reports and CLI check; add negative tests. 01:20–02:20: open cross-reviewed PRs, request changes, improve implementations and obtain approval. 02:20–03:10: integrate, test from latest main, repair regressions and document README and learning logs. 03:10–04:00: demo, peer bug-hunter challenge, individual explanation and mentor feedback.
Time is a planning guide, not a speed race. If unresolved test failures remain, document them explicitly and request mentor support instead of claiming completion.
Live defence prompts — each engineer answers independently
1. What important invariant can your function guarantee? 2. Which test failed before you corrected a bug? 3. How does your code avoid modifying state on a rejected action? 4. Demonstrate what happens when JSON loads duplicate IDs. 5. Why do multiple filters use logical AND? 6. How did you check an AI recommendation? 7. Show your PR and a substantive review you gave your partner. 8. If the mentor changes one business rule, identify the function and test to update.
10 | PROJECT SCORING (100)
Original CampusFlow preserved and baseline regression evidence — 10 points.
Validation and correct ticket lifecycle invariants — 15 points.
Follow-up notes and note-state safety — 10 points.
Search/filtering and analytics accuracy — 15 points.
Safe JSON validation, reload and ID continuity — 10 points.
Meaningful automated tests and edge cases — 15 points.
Git branches, PR authorship, reciprocal review and approved merges — 15 points.
Verified AI learning, CLI understanding check, documentation and individual defence — 10 points.
What counts as completion?
A working application and explanation are BOTH necessary. Original features still work; required cases pass; tests run on merged main; rejected actions preserve data; JSON errors do not wipe state; both engineers have code and review contributions; AI logs show independent verification; both engineers can defend their own logic and complete the CLI check.
11 | SUBMISSION REQUIREMENTS
Submit Engineer A and Engineer B full names, existing CampusFlow repo URL, final main commit SHA, Engineer A feature PR URL, Engineer B feature PR URL, unittest command and output, README, baseline-check.md, docs/ai-learning-log.md, and final CLI demonstration. Each engineer submits a short reflection describing one verified mistake, one learning gain, and one improvement received through code review.
Recommended repository organisation
Keep your existing structure where possible. Suggested additions: campusflow/validation.py, notes.py, search.py, reports.py, storage.py and understanding_check.py; tests/test_validation.py, test_notes.py, test_search.py, test_storage.py, test_understanding.py; docs/baseline-check.md, ai-learning-log.md, design-decisions.md. Do not reorganize the whole repository merely to match this example.
12 | OPTIONAL PERSONAL GROWTH ROUTES
If your audit mentioned FAILED TESTS: prioritize explaining test failures and run-from-clean-clone; create new negative tests. If it mentioned INVALID TRANSITIONS: strengthen status validation before notes. If it mentioned UNREVIEWED PRs: focus on real review comments and approval chronology. If it mentioned UNCLEAR AI LEARNING: bring small experiments and independent justifications. If it mentioned README/CLI issues: request a partner fresh-clone walkthrough. Your mentor chooses ONE priority focus, not a new unrelated project.
FINAL CHALLENGE
The difference between a working beginner project and a dependable engineering project is evidence. Can you show WHY your code is correct, WHAT happens when inputs are wrong, HOW another engineer reviewed your changes, and WHICH concepts you now understand without AI? Build something the next fellow can safely use and maintain.

