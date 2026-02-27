.PHONY: help
.PHONY: clean clean-build clean-pyc clean-test clean-dev
.PHONY: poetry-init poetry-requirements-txt poetry-requirements-dev-txt
.PHONY: version-bump-major version-bump-minor version-bump-patch
.PHONY: lint test test-all check install-all
.PHONY: build publish install
.PHONY: docker-build docker-rm docker-run
.PHONY: deploy deploy-ui
.SILENT: publish docker-run
.DEFAULT_GOAL := help

########
# help #
########
help: ## Prints all available targets w/ descriptions (Default Target)
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

#########
# clean #
#########
clean: clean-build clean-pyc clean-test clean-dev ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

clean-dev: ## remove development artifacts
	rm -f requirements.txt
	rm -f requirements_dev.txt
	rm -f poetry.lock


##########
# poetry #
##########
poetry-init: ## install poetry
	@echo 'Installing poetry...'
	./scripts/install-poetry.sh
	poetry --version

poetry-install: poetry-init
	poetry install

poetry-requirements-txt: ## export dependencies to requirements.txt
	poetry export --without-hashes -f requirements.txt | sed -e 's/;.*//g' > requirements.txt

###########
# version #
###########
version-bump-major: ## bump major version
	bump2version major
version-bump-minor: ## bump minor version
	bump2version minor
version-bump-patch: ## bump patch version
	bump2version patch

###############
# lint & test #
###############
lint: ## check style with flake8
	flake8 esm_fullstack_challenge tests

test: ## run tests quickly with the default Python
	pytest

test-all: ## run tests on every Python version with tox
	tox

coverage: ## check code coverage quickly with the default Python
	coverage run --source esm_fullstack_challenge -m pytest
	coverage report -m

#########
# build #
#########
build: clean ## builds source and wheel package
	poetry build

###########
# install #
###########
ENVIRONMENT ?= development

install:  clean ## install the package to the active Python's site-packages
ifeq ($(ENVIRONMENT), development)
	$(MAKE) poetry-install
else
	pip install .
endif

##########
# docker #
##########
PROJECT_NAME = $(shell ./scripts/get-project-name.sh)
GIT_SHORT_HASH = $(shell git rev-parse --short HEAD)
DOCKER_RUN_CMD ?= help

docker-build:  ## build docker container
	docker build -t $(PROJECT_NAME) .

docker-rm: ## delete previously named docker container
	@echo 'Removing previous containers...'
	docker rm $(GIT_SHORT_HASH) &>/dev/null || echo 'No previous containers found.'

docker-run: docker-build docker-rm  ## runs named docker container
	docker run --name $(GIT_SHORT_HASH) \
		-i $(PROJECT_NAME) $(DOCKER_RUN_CMD)

#######
# Run #
#######
init-db:
	./scripts/initiate_db.py
api:
	./scripts/entrypoint.sh

api-prod:
	fastapi run esm_fullstack_challenge/main.py --host 0.0.0.0 --port $${PORT:-9000}

ui:
	cd dashboard && make start

dev:
	@echo 'COMMAND FOR LOCAL DEV'
run: clean
	docker-compose up --build

check: lint test ## run all linting and tests (backend + frontend)
	cd dashboard && make lint

deploy: infra/.venv ## deploy infrastructure to AWS via CDK
	cd infra && npx aws-cdk@latest deploy --require-approval never

deploy-ui: ## build frontend and deploy to S3, invalidate CloudFront
	$(eval STACK_OUTPUT = $(shell aws cloudformation describe-stacks --stack-name F1DashboardStack --query 'Stacks[0].Outputs' --output json))
	$(eval BUCKET = $(shell echo '$(STACK_OUTPUT)' | python3 -c "import sys,json;o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)};print(o['SiteBucketName'])"))
	$(eval DIST_ID = $(shell echo '$(STACK_OUTPUT)' | python3 -c "import sys,json;o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)};print(o['DistributionId'])"))
	$(eval API_URL = $(shell echo '$(STACK_OUTPUT)' | python3 -c "import sys,json;o={x['OutputKey']:x['OutputValue'] for x in json.load(sys.stdin)};print(o['ApiUrl'])"))
	cd dashboard && yarn install && VITE_REACT_APP_API_URL=$(API_URL) yarn build
	aws s3 sync dashboard/dist/ s3://$(BUCKET) --delete
	aws cloudfront create-invalidation --distribution-id $(DIST_ID) --paths "/*"

infra/.venv: infra/requirements.txt
	python3 -m venv --clear infra/.venv
	infra/.venv/bin/pip install -q -r infra/requirements.txt

install-all: poetry-install
	make install
	cd dashboard && npm i