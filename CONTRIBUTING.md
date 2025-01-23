# Contributing

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Development

This project uses [poetry](https://python-poetry.org/) for dependency management and package build/publishing.

You can follow [their instructions](https://python-poetry.org/docs/#installation) on installation.

### Install Dependencies

```bash
poetry install --with dev
```

### Run Tests

```bash
poetry run pytest
```

### Run Formatter

```bash
poetry run black .
```
