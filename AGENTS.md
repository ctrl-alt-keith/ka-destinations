# AGENTS

This repository follows the shared workflow defined in the
`ai-workflow-playbook` repository.

- Engineering baseline: `ai-workflow-playbook/docs/engineering-baseline.md`
- Workflow rules: `ai-workflow-playbook/docs/`
- Start here: `ai-workflow-playbook/docs/start-here.md`

Use the playbook for general workflow rules. Follow this AGENTS.md for
repo-specific behavior when they differ. Repo-local rules take precedence only
for repo-specific behavior.

## Startup And Interaction Mode

- Start with `ai-workflow-playbook/docs/start-here.md` before repository or
  software work.
- Before acting, select the interaction mode from
  `ai-workflow-playbook/docs/repo-readiness.md`: implementation, review/audit,
  or orchestration/prompt-authoring.
- Implementation agents make explicit repo changes and carry them through
  validation, commit, push, and PR delivery.
- Review/audit agents inspect and report findings without mutating the repo.
- Orchestration/prompt-authoring agents produce complete, self-contained
  handoffs or prompts unless explicitly asked to implement.

## File Placement

- Put implementation code under `src/ka_destinations/`.
- Put tests under `tests/`.
- Do not commit generated `build/` artifacts unless the task explicitly
  requires it.

## Local Execution

- Run commands from this repository working directory by default.
- Keep temporary workflow state repo-local, for example `.worktrees/`.
- Use direct command execution for ordinary repo commands such as `git ...`,
  `gh ...`, `make ...`, `python ...`, and repo-local scripts or tools.
- Before using `zsh`, `bash`, `sh`, `zsh -lc`, `bash -lc`, `sh -c`, aliases, or
  equivalent wrapper shells, check whether the command has a direct form and
  use that direct form when it does.
- Use shell wrappers only when shell syntax is genuinely required, such as
  pipelines, redirection, glob expansion, command chaining, scoped environment
  assignment, compound commands, or shell builtins.

## Branches

- Use `feat/`, `fix/`, `docs/`, or `chore/` prefixes.
- Avoid `codex/` for normal work.

## Validation

- Run `make check` before opening or updating a pull request.
- `make check` is the canonical local blocking validation entrypoint.
- `make check` runs `make lint`, `make typecheck`, and `make test`.
- Do not open or update a pull request if validation fails.
- Live Google Docs or Drive publishing and credentialed Google validation are
  outside normal local PR validation unless explicitly requested and reported
  separately.

## Pull Requests

- For shared PR lifecycle behavior, use `ai-workflow-playbook/docs/start-here.md`
  and the referenced workflow docs.
- In this repository, target `main` and include validation or testing notes.

## Destination Boundary

- `knowledge-adapters` handles acquisition and normalization.
- `ka-destinations` handles final publish behavior.
- Keep publish behavior explicit and scoped.
- Do not add update, sharing, permission, or lifecycle-management behavior
  unless the task explicitly requires it.
