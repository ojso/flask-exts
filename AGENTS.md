# AGENTS.md

## Language

Code and documentation are primarily in English. Tests may include Chinese comments for internationalization (i18n) scenarios.

## Project overview

Flask extension library built on SQLAlchemy, WTForms, and admin views.
Requires Python 3.10+.

## Environment setup

Use the repository-local virtual environment instead of the system Python.

```bash
# Run from the repo root
test -d venv || python3 -m venv venv
. venv/bin/activate
python -m pip install -e '.[dev,test]'
```

If the environment already exists, activate it with:

```bash
. venv/bin/activate
```

Re-run the `pip install -e '.[dev,test]'` command after pulling changes to
`pyproject.toml`, so optional dependencies stay in sync.

## Common development commands

All commands below assume the venv is activated. If you use `make` targets such as
`make test` or `make coverage`, activate the venv first: the Makefile calls bare
`pytest` and `coverage`, which are not available system-wide.

Run the full test suite when needed:

```bash
# Run from the repo root
. venv/bin/activate
python -m pytest -q
```

Run the smallest relevant test target while iterating:

```bash
python -m pytest -q tests/forms/fields/test_json.py
```

Lint and format:

```bash
python -m ruff check .
python -m ruff format .
# Check only the templates you changed; the whole tree currently has
# pre-existing formatting issues.
python -m djlint src/flask_exts/templates/layout.html --check
```

Refresh vendored front-end assets (only when changing files under
`src/flask_exts/static`):

```bash
npm install
npm run copy:vendor
```

## Documentation

Install the documentation dependencies and build the HTML docs:

```bash
python -m pip install -r docs/requirements.txt
make docs-build
```

`make docs-build` treats Sphinx warnings as errors; only address warnings
introduced by your change, not pre-existing ones.

## Build package

Building distributions is independent of the development environment. Install
the packaging tools and build the wheel and source distribution:

```bash
python -m pip install -e '.[build]'
python -m build
```

Artifacts are written to `dist/`.

## Coding guidance

- Prefer the project-local venv for all Python commands.
- Validate with the smallest relevant test target before broad test runs.
- Avoid using system `python` or `pytest` directly when a repo-local venv is available.
- Run ruff and djlint checks on files you touch before finishing.
- Code and documentation are in English. Tests may use other languages for internationalization (i18n) scenarios.

## Notes

- This project is configured for Python 3.10+; the local venv currently uses 3.13.
