# AGENTS

This repository follows the shared workflow defined in the
`ai-workflow-playbook` repository.

- Engineering baseline: `ai-workflow-playbook/docs/engineering-baseline.md`
- Workflow rules: `ai-workflow-playbook/docs/`

Use the playbook for general workflow rules. Follow this AGENTS.md for
repo-specific behavior when they differ. Repo-local rules take precedence only
for repo-specific behavior.

## File Placement

- Put implementation code under `src/ka_destinations/`.
- Put tests under `tests/`.

## Validation

- Run `make check` before opening or updating a pull request.
- `make check` is the canonical validation entrypoint.
- Do not open or update a pull request if validation fails.

## Pull Requests

- Target `main`.
- Follow the playbook default for pull request readiness: ready for review by
  default, and draft only when explicitly requested or when the work is
  incomplete.

## Destination Boundary

- `knowledge-adapters` handles acquisition and normalization.
- `ka-destinations` handles the final publish step.
- See playbook guidance for destination-boundary constraints.
