.PHONY: clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT


help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: ## remove all build, test, coverage and artifacts
	rm -rf node_modules

lint: ## check style with eslint
	yarn run eslint .

prettier: lint ## runs prettier
	yarn prettier --write src

test: export CI=true
test: ## run tests
	yarn test

install: clean ## install the package to the active Python's site-packages
	yarn install

start: install ## start local development server
	yarn dev

run: clean ## run docker-compose
	docker-compose up --build

################
# Docker Stuff #
################
PROJECT_NAME = dashboard
GIT_HASH = $(shell git rev-parse HEAD)
GIT_SHORT_HASH = $(shell git rev-parse --short HEAD)
DOCKER_REPO ?= MISSING_DOCKER_REPO
DOCKER_RUN_CMD ?= help

docker-build: clean ## build docker container
	docker build --cache-from $(DOCKER_REPO):latest -t $(PROJECT_NAME) .

docker-rm: ## remove previous docker container
	@echo 'Removing previous containers...'
	docker rm -f $(GIT_SHORT_HASH) &>/dev/null || echo 'No previous containers found.'

docker-run: docker-rm ## run docker container
	docker run --name $(GIT_SHORT_HASH) \
		-i $(PROJECT_NAME) $(DOCKER_RUN_CMD)
