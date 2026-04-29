# AGENTS

This repository follows the shared workflow defined in the
`ai-workflow-playbook` repository.

- Engineering baseline: `ai-workflow-playbook/docs/engineering-baseline.md`
- Workflow rules: `ai-workflow-playbook/docs/`
- Start here: `ai-workflow-playbook/docs/start-here.md`

Use the playbook for general workflow rules. Follow this AGENTS.md for
repo-specific behavior when they differ. Repo-local rules take precedence only
for repo-specific behavior.

## File Placement

- Put implementation code under `src/ka_destinations/`.
- Put tests under `tests/`.
- Do not commit generated `build/` artifacts unless the task explicitly
  requires it.

## Branches

- Use `feat/`, `fix/`, `docs/`, or `chore/` prefixes.
- Avoid `codex/` for normal work.

## Validation

- Run `make check` before opening or updating a pull request.
- `make check` is the canonical validation entrypoint.
- Do not open or update a pull request if validation fails.

## Pull Requests

- Target `main`.
- Include a clear summary.
- Include validation or testing notes.
- Include risks or follow-up notes when relevant.
- Add `Closes #[issue number]` for issue-driven work.
- Open pull requests ready for review by default.
- Draft pull requests are not part of the normal workflow for this repository.
  Use a draft only when explicitly requested or when the work is incomplete and
  early feedback is the goal.

## Destination Boundary

- `knowledge-adapters` handles acquisition and normalization.
- `ka-destinations` handles final publish behavior.
- Keep publish behavior explicit and scoped.
- Do not add update, sharing, permission, or lifecycle-management behavior
  unless the task explicitly requires it.
