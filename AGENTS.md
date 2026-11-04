# AGENTS.md

## Project

Flask extension library built on SQLAlchemy, WTForms, and admin views.
Supports Python 3.10+.

## Development workflow

Use the repository-local virtual environment. Developers can set it up with:

```bash
test -d venv || python3 -m venv venv
. venv/bin/activate
python -m pip install -e '.[dev,test]'
python -m pip install -r docs/requirements.txt
```

Agents must not install packages or tools; the setup commands above are for
developers. If a required dependency is missing, ask the developer to install
it.

Run the smallest relevant test target while iterating; run the full suite for
broad changes:

```bash
python -m pytest -q tests/unit/forms/fields/test_json.py
python -m pytest -q
```

Run Ruff and format only files changed for the task. Check only templates you
changed with djLint. Build docs when changing docs or public docstrings:

```bash
python -m ruff check path/to/changed_file.py
python -m ruff format path/to/changed_file.py
python -m djlint path/to/changed_template.html --check
python -m sphinx -b html docs docs/_build/html -W -n --keep-going
```

The repository has pre-existing Ruff and template-formatting issues; do not
reformat unrelated files.

## Change boundaries

Ask before:

- Adding or upgrading runtime dependencies.
- Changing public APIs, configuration keys, models, or the database schema.
- Regenerating vendored assets or restructuring docs and published pages.

Always keep changes focused and declare public re-exports in `__all__`. Never:

- Commit secrets, credentials, or local `.env` files.
- Hand-edit `src/flask_exts/static/vendor/`; use the project regeneration
  script when authorized.
- Edit files under `venv/`, `node_modules/`, `dist/`, or `docs/_build/`.
- Rewrite git history, force-push, or revert another person's work.

## Coding guidance

- Write code and documentation primarily in English. Tests may use other
  languages for i18n coverage.
- Preserve Python 3.10 compatibility; do not use syntax or standard-library
  features introduced in later Python versions.
- Prefer f-strings for string formatting; avoid `.format()` and `%` formatting.
- Add type annotations to public functions and methods, and give them concise,
  same-line Google-style docstrings with `Args:`, `Returns:`, and `Raises:`
  sections. Preserve Sphinx/reStructuredText markup.
- Use SQLAlchemy 2.0 `Mapped` annotations. Declare reverse relationships
  explicitly with `relationship(back_populates=...)`; do not use `backref`.

For test organization, naming, coverage, integration models, and validation,
see `docs/testing.rst`.

## Changelog and releases

Keep user-visible changes under `Unreleased` in `CHANGES.rst`, written in
reStructuredText. The version is maintained in `src/flask_exts/__about__.py`;
do not bump it or create release tags unless asked.

## Commits

Use Conventional Commit messages for new commits (for example,
`fix(forms): handle empty input`). Do not create commits unless asked.
