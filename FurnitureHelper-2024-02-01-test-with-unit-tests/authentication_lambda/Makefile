help: ## print this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "%-30s %s\n", $$1, $$2}'

.PHONY: lint
lint: ## run linting and checks (black, flake8, isort, mypy)
	poetry run black --check .
	poetry run flake8 .
	poetry run isort --check .
	poetry run mypy lambda

format: ## format code (with black & isort)
	poetry run black .
	poetry run isort .

.PHONY: test
test:  ## Run pytest
	poetry run pytest -vv tests \
		--cov=lambda_project \
		--cov-fail-under=80 \
		--cov-report term-missing

clean: clean-build clean-pyc clean-test clean-venv clean-codebraid ## remove python files, env, and build artifacts

clean-build:
		rm -fr build/
		rm -fr dist/
		rm -fr .eggs/
		find . -name '*.egg-info' -exec rm -fr {} +
		find . -name '*.egg' -exec rm -f {} +

clean-codebraid:
		@echo 'Clearing codebraid cache'
		rm -rf _codebraid

clean-pyc:
		find . -name '*.pyc' -exec rm -f {} +
		find . -name '*.pyo' -exec rm -f {} +
		find . -name '*~' -exec rm -f {} +
		find . -name '__pycache__' -exec rm -fr {} +

clean-test:
		rm -f .coverage
		rm -fr htmlcov/

clean-venv:
		rm -fr .venv/


build-readme: init clean-codebraid ## Generate GitHub flavoured README.md from template (README.codebraid.md)
	@echo 'Building README.md'
	poetry run \
		codebraid pandoc\
		--from markdown \
		--to gfm \
		README.codebraid.md > README.md
