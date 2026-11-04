.PHONY: docs-build docs-serve docs-clean ruff-check ruff-format-check djlint-check djlint-format

docs-build:
	python -m sphinx -b html docs docs/_build/html -W -n --keep-going

docs-serve:
	python -m http.server -d docs/_build/html 8000

docs-clean:
	rm -rf docs/_build

docs-rebuild: docs-clean docs-build

test:
	pytest

ruff-check:
	python -m ruff check .

ruff-format-check:
	python -m ruff format --check .

djlint-check:
	python -m djlint src/flask_exts/templates --check

djlint-format:
	python -m djlint src/flask_exts/templates --reformat

pytest-last:
	pytest --lf --last-failed-no-failures=none

pytest-clean:
	rm -rf .pytest_cache

pytest-warn:
	pytest -W error

pytest-print:
	pytest -s

coverage:
	coverage run -m pytest

coverage-report:
	coverage report -m
