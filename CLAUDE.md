# Snowplow Signals Python SDK — Agent Entry Point

This is the Python SDK for Snowplow Signals — a client library for defining attribute groups, registering them with the Signals API, and reading attributes / interventions at inference time.

## Components at a glance

| Path | Purpose |
|---|---|
| `src/snowplow_signals/` | The SDK package — public API, models, batch + online clients |
| `src/snowplow_signals/models/` | Pydantic models generated from the Signals OpenAPI |
| `test/` | Unit tests (pytest) |
| `integration_tests/` | End-to-end tests against a live Signals API |
| `local_testing/` | Local-dev fixtures and scripts |

## Build system — Poetry

```bash
# Setup
poetry install --with dev
poetry run pre-commit install

# Tests
poetry run pytest                   # all
poetry run pytest test/<file>       # subset

# Format + lint
poetry run black .
poetry run isort .

# Build
poetry build
```

Python ≥ 3.11. Code style: [black](https://github.com/psf/black). Tests: pytest.

## What Claude must never do

1. **Never modify existing test assertions** — assertions express human-defined correctness; only the developer changes them.
2. **Never change public API shape** implicitly — class signatures, method names, parameter types, and return types are contracts with SDK users.
3. **Never edit `src/snowplow_signals/models/model.py` by hand** — it's generated from the Signals API's OpenAPI spec; regenerate via the documented tooling instead.
4. **Never commit secrets** — no API keys, tokens, or credentials in any file.
5. **Never keep unused or dead code** unless explicitly instructed.

## Implementing tickets

When you're triggered by the `implement` label on a GitHub issue (or asked to implement an issue / Jira ticket locally), the issue body is the spec — read it carefully before anything else.

Then:

1. Read this file. If the change touches a specific area (models, batch client, online client), skim that area's existing code to match its patterns before editing.
2. Implement the change as described in the issue body. Don't deviate from its file-level intent. If you find an error in it, note the deviation in the PR description.
3. Keep changes minimal and focused. Don't refactor unrelated code.
4. Add or modify tests for every new feature or bug fix. Tests live in `test/` (unit) and `integration_tests/` (e2e).
5. If you discover a real architectural blocker the spec didn't anticipate, stop and post a comment on the issue. Don't guess.

Before opening the PR:

- `poetry run black .` — formatting
- `poetry run isort .` — import order
- `poetry run pytest` — tests pass

PR shape (matches this repo's `CONTRIBUTING.md`):

- **Branch**: `feature/aisp-<key>-<short-description>` (lowercase, e.g. `feature/aisp-1234-add-foo`). Use `fix/`, `chore/`, etc. as appropriate.
- **Commits**: prefix with the Jira key in brackets, e.g. `[AISP-123] Add foo support`.
- **PR title**: same `[AISP-XXX] Description` prefix. If a GitHub issue number is provided, append `(closes #NNN)`.
- **PR body**: Summary, `Closes #NNN`, Changes, Testing.

See `CONTRIBUTING.md` for the broader workflow (versioning, release process, etc.).
