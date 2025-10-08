# Contributing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## **Introduction**
This document serves as a comprehensive reference for all teams contributing to Signals code base changes. Our goal is to ensure consistency, maintainability, and quality across all components and services. This guide outlines the necessary criteria and standards that must be met.

## Development

This project uses [poetry](https://python-poetry.org/) for dependency management and package build/publishing.

You can follow [their instructions](https://python-poetry.org/docs/#installation) on installation.

### Install Dependencies & commit hooks

```bash
poetry install --with dev
poetry run pre-commit install
```

### Run Tests

```bash
poetry run pytest
```

### Run Formatter

```bash
poetry run black .

```

### Commits
- Prefix your commit with the JIRA reference, where possible
E.g. `[AISP-184] XYZ`

## PRs
- Make sure to name the PR starting with the JIRA reference:
E.g. `[AISP-184] XYZ`


## Branching Strategy

### Main branches
main: Production ready code.

### Supporting branches
feature/<name>: For new features.
fix/<name>: For fixes to production.
chore/<name>: For updates not affecting production code.
release/<name>: For release PRs.

Add the JIRA reference in the branch name, where relevant:
E.g. `feature/aisp-184-<name>`

### Rules
- Always branch off `main`.
- Keep branches short-lived and regularly rebase them onto `main` to stay up to date.

## Versioning
We follow [Semantic Versioning](https://semver.org/):
`MAJOR` version: Breaking changes
`MINOR` version: New features, backward-compatible
`PATCH` version: Bug fixes

- **Before 1.0.0:** Breaking changes may occur in minor version bumps (0.x → 0.y).
- **After 1.0.0:** Any breaking change will require incrementing the **MAJOR** version.

## Release Process
- Create a release branch from `main` (e.g. `release/0.1.0`)
- Open up a new PR against `main` on GitHub
- List all items ready to be released in the description
- Add a `Prepare for x.x.x release` commit:
	- Update the CHANGELOG.md:
		- Include relevant features and fixes
		- Exclude under-the-hood changes (renames, CI tweaks, formatting-only changes).
- Go through the `Release Checklist` making sure all items are ticked
- Merge into `main` using a merge commit
- Run the Release workflow -> it will create and push the latest tags and publishes the new version to PyPI
- Create or update the GitHub Release for the new tag and include the relevant changelog entry
- Announce the release in the `#releases` Slack channel

### Release Checklist

Before releasing a new version, ensure all items below are completed:

- [ ] All required changes/PRs merged into the release branch
- [ ] All automated tests pass
- [ ] Last commit added called `Prepare for x.x.x release`
- [ ] Changelog is updated with the latest version
- [ ] PR approved by at least one AI Team member
