.PHONY: all_checks static_analysis type_check coverage run_tests

all_checks: type_check static_analysis coverage

static_analysis:
	flake8

type_check:
	mypy --ignore-missing-imports gitanalyzer/ tests/

coverage:
	pytest --cov-report term --cov=gitanalyzer tests/

run_tests:
	pytest