.PHONY: docs-build docs-serve docs-clean

docs-build:
	python -m sphinx -b html docs docs/_build/html -W -n --keep-going

docs-serve:
	python -m http.server -d docs/_build/html 8000

docs-clean:
	rm -rf docs/_build

pytest:
	pytest

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
