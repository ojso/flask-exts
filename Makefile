.PHONY: docs-build docs-serve docs-clean ruff-check ruff-format-check djlint-check djlint-format dist

docs-build:
	uv run python -m sphinx -b html docs docs/_build/html -W -n --keep-going

docs-serve:
	uv run python -m http.server -d docs/_build/html 8000

docs-clean:
	rm -rf docs/_build

docs-rebuild: docs-clean docs-build

test:
	uv run pytest

ruff-check:
	uv run python -m ruff check .

ruff-format-check:
	uv run python -m ruff format --check .

djlint-check:
	uv run python -m djlint src/flask_exts/templates --check

djlint-format:
	uv run python -m djlint src/flask_exts/templates --reformat

pytest-last:
	uv run pytest --lf --last-failed-no-failures=none

pytest-clean:
	rm -rf .pytest_cache

pytest-warn:
	uv run pytest -W error

pytest-print:
	uv run pytest -s

coverage:
	uv run coverage run -m pytest

coverage-report:
	uv run coverage report -m

dist:
	uv build
