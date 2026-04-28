# AGENTS

- Use `feat/`, `fix/`, `docs/`, or `chore/` branch prefixes. Avoid `codex/`
  for normal work.
- Run `make check` before opening or updating a pull request.
- `make check` is the canonical validation entrypoint.
- Do not open or update a pull request if validation fails.
- Keep pull requests small, scoped, and easy to review.
- This repository is part of a multi-repo workspace. Changes must be scoped to
  this repository only. Do not stage or commit files from other repositories;
  open separate PRs per repository.

This repository follows the shared workflow defined in the
`ai-workflow-playbook` repository.

- Engineering baseline: `ai-workflow-playbook/docs/engineering-baseline.md`
- Workflow rules: `ai-workflow-playbook/docs/`

Use the playbook for general workflow rules. Follow this AGENTS.md for
repo-specific behavior when they differ.

## Completion

- For repo changes, do not treat local edits or passing `make check` alone as
  done.
- The task is complete only after the change is committed, pushed, and opened
  as a pull request targeting `main`.

## PR Readiness

- Open pull requests as ready for review when implementation is complete,
  `make check` passes, no known follow-up work is required, and coordination
  risk is low.
- Use draft pull requests when work is incomplete, the change is part of a
  coordinated batch, reconciliation with other pull requests is expected, or
  the pull request is intentionally staged.
- Docs-only or isolated changes should default to ready when validated.

## Destination Boundary

- See playbook guidance for destination-boundary constraints.
