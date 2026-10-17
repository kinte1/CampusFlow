# CampusFlow Baseline Check

## Baseline version

- **Commit tested:** `a2080ba`
- **Version:** Original CampusFlow workflow and CLI
- **Test command:** `python3 -m unittest discover -s tests -v`
- **Automated test result:** 53 tests passed in 0.397 seconds

The baseline tests completed successfully. Manual checks were also performed against the original CLI at commit `a2080ba`.

## Manual checks

### 1. Create a valid ticket

**Input**
- Title: `Baseline Wifi issue`
- Category: `Network`
- Urgency: `high`
- Affected users: `12`

**Observed result**

The application accepted the ticket and displayed `Created ticket T002.` The work queue displayed the ticket with `critical` priority, `open` status, and `Unassigned` staff.

### 2. Reject invalid affected-user input

**Input**
- Title: `Baseline Wifi invalid test`
- Category: `Network`
- Urgency: `high`
- Affected users: `0`

**Observed result**

The application rejected the input and displayed:

`Error: Affected users must be a positive integer.`

No ticket-creation success message appeared for this invalid input.

### 3. Inspect the work queue

**Observed result**

The work queue displayed:

- `T001 - Baseline Wifi issue`
- `T002 - Baseline Wifi issue`

Both were displayed as `Network` tickets with `critical` priority, `open` status, and `Unassigned` staff.

The presence of `T001` before the latest ticket creation indicates that the baseline data already contained a ticket from an earlier run.

## Baseline limitations and follow-up

These checks establish that the tested baseline could run its automated test suite, create a valid ticket, reject zero affected users, and display open tickets in the work queue.

They do not establish that every requirement was satisfied. CampusFlow Next will strengthen validation, storage integrity, notes and lifecycle rules, search, reporting, and the engineering understanding check.

The commit tested here is `a2080ba`. Confirm with the mentor whether this is the exact commit they intended as the audited baseline before describing it as the mentor-audited commit.