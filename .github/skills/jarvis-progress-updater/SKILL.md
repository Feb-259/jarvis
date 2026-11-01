---
name: jarvis-progress-updater
description: "Use at the beginning or end of a JARVIS work session to reconcile the current project status and update PROJECT_PROGRESS.md with verified progress, test results, blockers, and next steps."
argument-hint: "start or end"
---

# JARVIS Progress Updater

Update the project progress record at the beginning or end of a JARVIS work
session. This skill is on demand; invoke it with `/jarvis-progress-updater start`
when beginning work and `/jarvis-progress-updater end` before finishing. It does
not run automatically when a session starts or ends.

## Sources of truth

- Read `PROJECT_PROGRESS.md` and the relevant sections of `SPRINT_PLAN.md`.
- Verify current repository state and task outcomes from the workspace. Use
  source code, test output, and Git status as evidence; do not treat existing
  progress notes or code presence alone as proof that a feature works.
- Keep claims appropriately scoped. For example, an in-memory smoke test does
  not verify PostgreSQL persistence, and automated tests do not verify external
  services unless they explicitly exercise them.
- Do not overwrite or discard unrelated user changes.

## Beginning a session

1. Read the progress file and roadmap before starting project work.
2. Check the current branch and working-tree changes. Inspect the relevant
   changed files and run only focused checks needed to verify the existing
   status; do not run expensive suites without a reason.
3. Reconcile the current status, completed work, open blockers, and next steps
   in `PROJECT_PROGRESS.md` with the evidence found. Preserve distinctions
   between verified, unverified, and blocked work.
4. Update the `Cập nhật gần nhất` date and add a concise dated history entry
   noting that the status was checked at session start. Do not claim project
   work was completed merely because the session began.

## Ending a session

1. Review the work performed in this session and the final Git diff/status.
2. Run the smallest relevant validation for changes made, when applicable.
   Record its exact command and outcome; distinguish skipped or unavailable
   checks from passing checks.
3. Update the current status, completed and remaining work, blockers, and
   actionable next steps in `PROJECT_PROGRESS.md`. Keep the roadmap consistent
   with `SPRINT_PLAN.md` when sprint status or checklist items changed.
4. Update the `Cập nhật gần nhất` date and append a concise dated history entry
   describing only material changes and their verification.
5. Preserve the existing Vietnamese language and document structure. Do not
   create commits unless explicitly requested.

## Editing guidance

- Use the actual current date for the update.
- Keep historical entries intact; append rather than replacing them.
- If no material project progress occurred, record a brief status reconciliation
  only if needed; avoid duplicative history entries.
- If a claim cannot be verified, label it as unverified and state what would
  verify it. Never fabricate results or silently downgrade a blocker.
- Make focused edits to the progress file and, only when necessary, the
  corresponding sprint status in `SPRINT_PLAN.md`.
