# AGENTS

- Use `feat/`, `fix/`, `docs/`, or `chore/` branch prefixes. Avoid `codex/`
  for normal work.
- Run `make check` before opening or updating a pull request.
- `make check` is the canonical validation entrypoint.
- Do not open or update a pull request if validation fails.
- Keep pull requests small, scoped, and easy to review.
- This file defines repo-local execution rules; reusable workflow rules belong
  in the playbook.

## PR Readiness

- Open pull requests as ready for review when implementation is complete,
  `make check` passes, no known follow-up work is required, and coordination
  risk is low.
- Use draft pull requests when work is incomplete, the change is part of a
  coordinated batch, reconciliation with other pull requests is expected, or
  the pull request is intentionally staged.
- Docs-only or isolated changes should default to ready when validated.

## Destination Boundary

- Keep publishing behavior explicit and scoped.
- Avoid expanding destination capabilities such as updates, sharing, or
  permissions unless the task requires it.
- Prefer opt-in flags for behavior that broadens publish scope.
