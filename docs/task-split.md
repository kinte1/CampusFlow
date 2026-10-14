# CampusFlow Next — Engineer A / Engineer B Task Split

Working plan for the progress-band sprint described in [`project.md`](../project.md).
Milestone IDs (A1–A6, B1–B6) refer to the milestones in section 04 of that brief.

Status legend: `[ ]` not started · `[~]` in progress · `[x]` done

---

## 0. Decisions locked before coding

These four were resolved from evidence in the existing code, not by preference.
Record each in [`design-decisions.md`](design-decisions.md) with its evidence.

| # | Decision | Evidence | Consequence |
|---|---|---|---|
| D1 | Open Work Queue becomes **open-only** | [project.md:13](../project.md#L13) requires it; `get_work_queue` currently filters `status != "resolved"` and returns `in_progress` tickets (verified by running it) | Code change in `workflow.py`, README + docstring update, new negative test |
| D2 | Legacy JSON with **no `notes` key migrates** to `notes: []` | [project.md:55](../project.md#L55) forbids discarding old working tickets | Lenient load for that one field; format documented in README |
| D3 | `save_tickets()` **validates before writing** | Makes save/load symmetric; catches programmer error at the boundary | `tests/test_storage.py` minimal-fixture test must be updated |
| D4 | `resolution_percentage` reported as **`round(x, 1)`** | `66.7` reads better than `66.66666666666667`; `0.0` when total is 0 | Report contract, no division by zero |

**Error convention — one pattern, no mixing.** Every rejection raises `ValueError`
with a human-readable message. Nothing returns `None` or `False` to mean "invalid".
The CLI catches `(ValueError, OSError)` as it already does in
[`main.py:93`](../main.py#L93).

---

## 1. Module layout

Additive. No renames, no reshuffling of existing files.

```
campusflow/
  validation.py           NEW   (A)  constants, validators, validate_ticket, can_transition
  tickets.py              edit  (A)  create_ticket gains notes:[]; calculate_priority unchanged
  notes.py                NEW   (A)  next_note_id, add_note, get_notes
  storage.py              edit  (A)  notes validation, migration, validate-before-save
  workflow.py             edit  (B)  open-only queue, calls can_transition
  search.py               NEW   (B)  search_tickets, sort_by_priority_then_id
  reports.py              edit  (B)  by_category, unresolved, resolved, resolution_percentage
  understanding_check.py  NEW   (B)  QUESTION_BANK data + score_answers + run
main.py                   edit  (B)  menus 9-13 appended; 1-8 keep their numbers

tests/  test_validation.py      NEW  (A)      test_search.py         NEW  (B)
        test_notes.py           NEW  (A)      test_understanding.py  NEW  (B)
        test_storage.py         edit (A)      test_reports.py        edit (B)
        test_tickets.py         edit (A)      test_workflow.py       edit (B)

docs/   baseline-check.md  NEW (shared)      task-split.md  THIS FILE
        design-decisions.md, ai-learning-log.md  edit (both)
```

Menu numbers are **appended, never renumbered** — [`README.md:645`](../README.md#L645)
documents options 1–8 by number.

---

## 2. Interface contract

Agree this before either engineer writes an implementation. This is the coordination
step [`project.md:59`](../project.md#L59) calls for.

### Ticket schema — exactly one new key

```python
"notes": [{"note_id": "N001", "author": "Mentor A", "message": "Investigating switch ports"}]
```

### Engineer A exposes (B consumes)

| Function | Signature | Returns |
|---|---|---|
| `can_transition` | `(current: str, new: str) -> bool` | predicate only; pure, no I/O |
| `validate_ticket` | `(ticket: dict) -> dict` | normalized copy; raises on any broken invariant |
| `add_note` | `(ticket_id, author, message, file_path=DEFAULT_STORAGE_PATH)` | the new note dict |
| `get_notes` | `(ticket_id, file_path=DEFAULT_STORAGE_PATH)` | list ordered by `note_id` |
| `next_note_id` | `(ticket: dict) -> str` | `"N003"`, derived from existing notes |
| `next_ticket_id` | `(tickets: list) -> str` | replaces `generate_ticket_id`; old name kept as alias |
| `validate_author` | `(str) -> str` | trimmed; blank rejected |
| `validate_message` | `(str) -> str` | trimmed; 5–300 chars |

Shared constants live in `validation.py` (`CATEGORIES`, `URGENCIES`, `STATUSES`,
`PRIORITY_ORDER`) so `workflow.py` and `search.py` both import one definition
instead of keeping copies.

### Engineer B exposes

| Function | Signature | Returns |
|---|---|---|
| `search_tickets` | `(tickets, query=None, category=None, status=None, priority=None)` | list; pure, takes a list not a path, never mutates |
| `sort_by_priority_then_id` | `(tickets) -> list` | new list, priority then numeric ticket ID |
| `generate_report` | `(file_path=DEFAULT_STORAGE_PATH) -> dict` | keys below |
| `score_answers` | `(bank, answers) -> int` | 0–6 |

`generate_report` keys: `total`, `by_status`, `by_priority`, `by_category`,
`unresolved`, `resolved`, `resolution_percentage`.

### Two design points to hold to

1. **`next_note_id` derives from existing notes** rather than storing a counter.
   A counter can drift; a derived ID cannot. It also makes
   [`project.md:45`](../project.md#L45) ("a rejected note must not consume a note ID")
   true by construction — validation runs before any ID is computed.
2. **`search_tickets` takes a list and has no file path and no save call in its body.**
   That is what makes [`project.md:68`](../project.md#L68) answerable from the code.

---

## 3. Engineer A — Ticket Safety and Storage

**Branch:** `feat/<issue>-validation-and-notes`  **Owns:** validation.py, notes.py, storage.py, tickets.py

### Foundation

- [ ] A-1 Create `campusflow/validation.py`; move `validate_title`, `validate_category`,
      `validate_urgency`, `validate_affected_users` out of `tickets.py`. Add constants
      `CATEGORIES`, `URGENCIES`, `STATUSES`, `PRIORITY_ORDER` (moved from `workflow.py`).
      `tickets.py` re-imports them so existing imports keep working.
- [ ] A-2 Extract ticket-ID format validation into `validate_ticket_id(ticket_id)`.
- [ ] A-3 Write `validate_ticket(ticket: dict) -> dict` — the full-record invariant check
      (all fields, legal status, `in_progress` implies assigned, `notes` shape).
- [ ] A-4 Write `can_transition(current, new) -> bool` as a pure predicate.
      No I/O, no exceptions — it answers a question, it does not enforce anything.
- [ ] A-5 Write `validate_author` (non-blank) and `validate_message` (5–300 after trim).

### Notes data layer (Requirement B, business side)

- [ ] A-6 Write `next_note_id(ticket) -> str`, derived from the highest existing note ID.
- [ ] A-7 Write `add_note(ticket_id, author, message, file_path)` in `notes.py`.
      Load → validate author/message → check status in `{open, in_progress}` → compute ID
      → append → save. Raise before mutating anything.
- [ ] A-8 Write `get_notes(ticket_id, file_path)`, ordered by `note_id`.
- [ ] A-9 Add `"notes": []` to `create_ticket`'s returned dict.

### Storage (Requirement E)

- [ ] A-10 Extend `load_tickets`: validate note shape and per-ticket note-ID uniqueness;
      accept a missing `notes` key and normalize it to `[]` (D2).
- [ ] A-11 Make `save_tickets` validate every ticket before touching disk (D3).
- [ ] A-12 Add `next_ticket_id` as the name in the contract; keep `generate_ticket_id`
      as an alias so nothing breaks mid-branch.
- [ ] A-13 Enforce ticket-ID uniqueness on the create path, not only on load.
      `create_ticket` never sees the collection today, so this check belongs in
      `create_and_save_ticket`.

### Engineer A tests — milestones A1–A6

- [ ] A1 ⭐ Run and document the old tests → feeds `docs/baseline-check.md`.
- [ ] A2 Test proving an unassigned ticket cannot enter `in_progress`.
- [ ] A3 Reject invalid `affected_users` (0, negative, float, bool), invalid categories,
      and mutation of resolved tickets.
- [ ] A4 Add a note to an open ticket; reject a note on a resolved ticket; prove
      **both** the raise and the unchanged data.
- [ ] A5 Load corrupt and duplicate-ID JSON without erasing memory.
- [ ] A6 Restart and generate the correct next ticket and note IDs.

### Engineer A's bug-hunter test (against B's module)

- [ ] Write one unlisted edge case for `reports.py` or `search.py`. See §6 for the
      candidate I already have evidence for.

---

## 4. Engineer B — Search, Reporting and CLI

**Branch:** `feat/<issue>-search-and-insights`  **Owns:** search.py, reports.py, workflow.py, understanding_check.py, main.py

### Search (Requirement C)

- [ ] B-1 Write `search_tickets(...)` in `search.py` — `casefold()` substring match on
      title, plus optional `category` / `status` / `priority`. Supplied filters combine
      with **AND**; an unsupplied filter does not filter. Pure over a list, no mutation.
      `"WI-FI"` matches `"wi-fi"` — do not add punctuation normalization or fuzzy matching.
- [ ] B-2 Write `sort_by_priority_then_id(tickets)` using `PRIORITY_ORDER` from
      `validation.py` and `int(ticket["id"][1:])` for the tie-break.
      **Never sort by the text ID** — `"T10" < "T2"` is why [`project.md:24`](../project.md#L24) asks.

### Workflow

- [ ] B-3 Make the work queue open-only (D1) and have `update_ticket_status` call
      `can_transition` instead of inlining the rules. Keep the function's existing
      name and error messages so current tests still read correctly.

### Reports (Requirement D)

- [ ] B-4 Extend `generate_report` with `by_category`, `unresolved` (open + in_progress),
      `resolved`, and `resolution_percentage` (D4). Empty dataset returns `0.0`
      with no division. Counts derive from the current `status` field, so a reopened
      ticket counts as open — no double counting.
- [ ] B-5 Update `print_report` to display the new figures.

### CLI Understanding Check

- [ ] B-6 Write `understanding_check.py` with the six questions from
      [`project.md:75-80`](../project.md#L75-L80) as a `QUESTION_BANK` **data** structure,
      a pure `score_answers(bank, answers)`, and a thin `run()` loop.
      Scoring logic must not live in the menu loop. Inputs A/B/C/D; invalid → retry.
      Collect a short written explanation for at least two answers and display it;
      do not keyword-match it into the score.

### CLI (Requirement B + C user-facing side)

- [ ] B-7 Add menus for search, add note, view notes, sorted search results, and the
      understanding check — using A's functions, with helpful failure messages.
      Proposed numbering (B confirms; 1–8 do not move):

      ```
      9. Search tickets
      10. Add follow-up note
      11. View ticket notes
      12. Search results sorted by priority
      13. Engineering Understanding Check
      ```
- [ ] B-8 Keep `print`/`input` out of search, reports and scoring so those functions
      stay testable. Test CLI loops with `unittest.mock.patch("builtins.input")` —
      `unittest.mock` is standard library.

### Engineer B tests — milestones B1–B6

- [ ] B1 Title substring search with `casefold`.
- [ ] B2 Combined category/status/priority filters.
- [ ] B3 Report totals, including the no-tickets case.
- [ ] B4 Note CLI behaviours and failure messages.
- [ ] B5 The understanding check.
- [ ] B6 Tests for combined filters, report totals, invalid CLI choices, quiz scoring.

### Engineer B's bug-hunter test (against A's module)

- [ ] Write one unlisted edge case for `notes.py` or `storage.py`.

---

## 5. Test ownership — all 14 required acceptance cases

Required by [`project.md:85`](../project.md#L85). Cases 02 and 03 need a
**snapshot-before/after** assertion (read the file bytes, attempt the action, assert the
bytes are identical), not just `assertRaises` — `assertRaises` alone does not prove
[`project.md:21`](../project.md#L21).

| Case | Scenario | File | Owner |
|---|---|---|---|
| 01 | Priority rule precedence | `test_tickets.py` | A |
| 02 | Unassigned open → `in_progress` rejected, data unchanged | `test_validation.py` | A |
| 03 | Resolved ticket assignment rejected | `test_workflow.py` | A |
| 04 | Invalid `affected_users` (0, neg, float, bool) | `test_validation.py` | A |
| 05 | Valid note added, note ID correct | `test_notes.py` | A |
| 06 | Blank/too-short note rejected, ID not consumed | `test_notes.py` | A |
| 07 | Note on resolved rejected; after reopen accepted | `test_notes.py` | A |
| 12 | Save/load preserves notes and next IDs | `test_storage.py` | A |
| 13 | Corrupt or duplicate-ID JSON rejected, no state loss | `test_storage.py` | A |
| 08 | Search ignores case, matches substring | `test_search.py` | B |
| 09 | Combined filters use AND | `test_search.py` | B |
| 10 | Empty report → 0.0, no crash | `test_reports.py` | B |
| 11 | Counts correct after resolve/reopen | `test_reports.py` | B |
| 14 | Check rejects invalid answer, scores correctly | `test_understanding.py` | B |

**9 for A, 5 for B** — both clear the "at least five each" bar. Plus one bug-hunter test
each, written against the *other* engineer's module.

---

## 6. Bug-hunter candidates (evidence already gathered)

**B → A, work queue:** I confirmed by running it that `get_work_queue` returns
`in_progress` tickets today:

```
queue statuses: ['in_progress']
after 2nd ticket: [('T001', 'in_progress'), ('T002', 'open')]
```

The suite only tests resolved-exclusion, so nothing catches it. This is the regression
test that pins the D1 fix. Required format: initial state; input; expected result;
actual result; test name; code change made.

**A → B, reports:** `generate_report` pre-seeds its count dictionaries, so it survives an
unknown status today — but a naively built `by_category` would `KeyError` on a category
that is not seeded. Fixture idea: a ticket whose category is valid but not in the seeded
tuple.

---

## 7. Existing tests that must change

Budget these into Session 1 — a `notes` field is not a one-line change.

| Location | Why it breaks |
|---|---|
| [`test_tickets.py:109`](../tests/test_tickets.py#L109) | Exact-dict equality; needs `notes: []` |
| [`test_storage.py:27`](../tests/test_storage.py#L27) | `assertEqual(loaded, tickets)`; load now normalizes |
| [`test_storage.py:46`](../tests/test_storage.py#L46) | Saves a minimal `{id, title}` dict; fails once save validates (D3) |
| [`test_storage.py:104`](../tests/test_storage.py#L104), [:126](../tests/test_storage.py#L126), [:150](../tests/test_storage.py#L150) | Fixtures need `notes` |
| [`README.md:94`](../README.md#L94) | Queue described as "unresolved"; becomes open-only. Also needs a JSON format section |
| [`workflow.py:110`](../campusflow/workflow.py#L110) | Docstring says "unresolved" |

`test_reports.py` and the other queue tests in `test_workflow.py` survive unchanged —
every ticket in them is open. Verified.

---

## 8. Shared tasks

- [ ] S-1 📄 `docs/baseline-check.md` — run command, pass/fail results, three inputs tested,
      audit findings. Do this **first**, at the audited commit.
- [ ] S-2 📄 `docs/design-decisions.md` — record D1–D4 with their evidence.
- [ ] S-3 📄 `README.md` — JSON format and supported versions, open-only queue,
      new menu numbers, fresh-clone test command.
- [ ] S-4 📄 `docs/ai-learning-log.md` — two cycles each: concept gap, exact question,
      AI guidance summary, tiny unrelated experiment, independent verification, decision.
      At least one cycle for the team must document a **changed or rejected** AI suggestion.
- [ ] S-5 🐙 Open GitHub issues (A: validation/notes/storage; B: search/reports/CLI knowledge).
      Note: `gh` is not installed in this environment — use the web UI, or install it.
      Branch names should reference the real issue IDs.
- [ ] S-6 🐙 Two focused commits minimum per engineer. No direct feature commits to `main`.
- [ ] S-7 🔍 Each reviews the other's PR before merge: read the diff, run the tests,
      leave **at least two** specific observations citing file/behaviour/test.
      `LGTM` alone is not review evidence.
- [ ] S-8 🔁 After each merge: sync branches, rerun
      `python -m unittest discover -s tests -v` from the merged main.

---

## 9. Suggested sequencing

| When | A | B |
|---|---|---|
| Session 1, first | S-1 baseline at the audited commit | S-1 alongside |
| Session 1, contract | Publish `validation.py` signatures first — B is blocked on `can_transition`, `add_note`, `get_notes` | Build `search.py` + `reports.py` (no A dependency), then CLI screens once A lands |
| Session 1, build | validation → notes → storage | search → reports → workflow queue → understanding check |
| Session 1, tail | Update the six existing tests from §7 | Wire menus 9–13 |
| Session 2 | Cross-review B's PR; bug-hunter test for B's module | Cross-review A's PR; bug-hunter test for A's module |

**Blocking edge:** B's menu items 10 and 11 call A's `add_note` / `get_notes`. Unblock B by
having A commit the **signatures** (raising `NotImplementedError`) early, so B can build
the CLI against the real names rather than a guess.

---

## 10. Definition of done

- [ ] Original features and the priority rule order still work; baseline evidence recorded.
- [ ] All 14 required cases pass, plus two bug-hunter tests.
- [ ] Invalid actions leave the ticket collection byte-identical on disk.
- [ ] A corrupt or duplicate-ID JSON load leaves in-memory state untouched.
- [ ] Both engineers have authored code **and** substantive reviews.
- [ ] AI logs show independent verification, not just generation.
- [ ] Both engineers can defend their own logic and complete the understanding check
      without assistance.
- [ ] Any unresolved test failure is documented explicitly and raised with a mentor —
      not claimed as complete.
