# AGENTS.md

## Project

Flask extension library built on SQLAlchemy, WTForms, and admin views.
Supports Python 3.11+; the primary development version is Python 3.13 (Debian 13
stable), and 3.11 is kept as the minimum supported version.

## Development workflow

Use the repository-local virtual environment managed by uv. Developers can set
it up with:

```bash
uv sync
```

The `dev` dependency group includes the linting, testing, and documentation
tools. Activate `.venv` or prefix commands with `uv run`.

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

- Write code and documentation primarily in English. Use non-English strings
  in tests only for i18n or non-ASCII encoding coverage.
- Preserve Python 3.11 compatibility; do not use syntax or standard-library
  features introduced in later Python versions.
- Prefer f-strings for string formatting; avoid `.format()` and `%` formatting.
- Add type annotations to public functions and methods, and give them concise,
  same-line Google-style docstrings with `Args:`, `Returns:`, and `Raises:`
  sections. Preserve Sphinx/reStructuredText markup.
- Use SQLAlchemy 2.0 `Mapped` annotations. Declare reverse relationships
  explicitly with `relationship(back_populates=...)`; do not use `backref`.

For test organization, naming, coverage, integration models, and validation,
see `docs/testing.rst`.

## Dependency upgrades and compatibility

Support only the single dependency baseline declared in `pyproject.toml`. When
a dependency upgrade breaks behavior, fix the code for the declared version and
raise the lower bound if needed; do not keep runtime branches for older
versions.

Do not add version-conditional shims: `try/except ImportError` fallbacks,
`hasattr`/`getattr` probing, `sys.version_info` checks, or version comparisons
for versions outside the declared range. Let missing imports fail; install the
missing dependency with the developer instead. If an upgrade cannot be handled
without a fallback, raise the lower bound and add a `CHANGES.rst` entry.

Tests must not suppress deprecation warnings locally:

```python
with warnings.catch_warnings():
    warnings.simplefilter("error", DeprecationWarning)
```

Assert the supported behavior directly instead. Deprecation handling belongs in
the project-level pytest configuration, not in individual tests.

## AI-assisted changes

Keep changes minimal and evidence-based.

- Do not hide failures with `except Exception: pass`, default-value fallbacks, or
  `skip`/`xfail` added to make checks pass.
- Do not weaken assertions or delete tests to fix a failure. A regression test
  must fail before the fix and pass after it.
- Mock only boundaries such as network, time, and external services; never mock
  the logic under test.
- Do not add speculative abstractions, flags, or compatibility paths for
  hypothetical versions or backends.
- Do not refactor or reformat unrelated code, and do not invent APIs or
  configuration.
- Do not add "AI generated" markers or comments that narrate the change.

## Changelog and releases

Keep user-visible changes under `Unreleased` in `CHANGES.rst`, written in
reStructuredText. The version is maintained in `src/flask_exts/__about__.py`;
do not bump it or create release tags unless asked.

## Commits

Use Conventional Commit messages for new commits (for example,
`fix(forms): handle empty input`). Do not create commits unless asked.
