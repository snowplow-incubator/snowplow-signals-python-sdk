# Contributing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

### Release Process

To make a new release:

1. **Prepare the changelog**: Create a commit (e.g., "Prepare for release") that updates the `CHANGELOG.md` with all notable changes for the new version.
2. **Create a release PR**: Open a pull request to the `main` branch with your changelog and any other release-related changes.
3. **Merge the PR**: Merge the release PR using a merge commit. _Do not use squash or rebase._
4. **Run the Release workflow**: Trigger the "Release" workflow in GitHub Actions to publish the new version to PyPI.