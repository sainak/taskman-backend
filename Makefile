.PHONY: test static
.DEFAULT_GOAL := help

PROJECT_NAME := taskman
SETTINGS := $(PROJECT_NAME).settings.$(ENVIRONMENT)

help: ## Display callable targets.
	@egrep -h '\s##\s' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

require-%:
	@command -v $(@:require-%=%) > /dev/null || { echo "$(@:require-%=%) not found in path"; exit 1; }

migrations: ## Create migrations.
	@echo "--> Creating migrations"
	@pipenv run ./manage.py makemigrations

rm-migrations: ## Delete all migration files in migrations folders.
	@echo "--> Removing migrations"
	@find . -type f -path '**/migrations/**' -name '*.py' ! -name "__init__.py" -exec rm -f {} \;

migrate: ## Migrate database.
	@echo "--> Migrating database"
	@pipenv run ./manage.py migrate

dump dumpdata: ## Dump database.
	@echo "--> Dumping database"
	@pipenv run ./manage.py dumpdata taskman > db_dump_$(shell date +%FT%T.%3N%Z).json

loaddata: ## Load data from most recent db dump
	@echo "--> Loading data from db dump"
	@pipenv run ./manage.py loaddata $(shell ls -t db_dump_*.json | head -n 1) || \
	{ echo "Failed to load data"; exit 0; }

init-dev: require-pipenv require-direnv ## Setup Dev environment.
	@echo "--> Initializing"
	@pipenv install --dev
	@echo "--> Copying .env files"
	@cp -n sample.envrc .envrc
	@cp -n sample.env .env
	@direnv edit
	@echo "--> Installing pre-commit hooks"
	@pipenv run pre-commit install --hook-type pre-commit --hook-type pre-push

init-db: ## Create database.
	@echo "--> Creating database"
	@${MAKE} migrations migrate loaddata

init-tw: ## Initialize django-tailwind.
	@echo "--> Initializing django-tailwind"
	@pipenv run ./manage.py tailwind install
	@pipenv run ./manage.py tailwind build

init: ## Initialize project for development.
	@echo "--> Initializing project"
	@${MAKE} init-dev init-db
# @${MAKE} init-dev init-db init-tw

clean: ## Clean up.
	@echo "--> Removing venv"
	@pipenv --rm
	@echo "--> Cleaning pycache files"
	@find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

clean-db: dump ## Clear database.
	@echo "--> Dropping database"
	@pipenv run ./manage.py sqlflush | pipenv run ./manage.py dbshell

reinit-db: clean-db init-db ## Re-initialize database.

reinit: clean init reinit-db ## Re-initialize project.

update: ## Install and update dependencies.
	@echo "--> Updating dependencies"
	@pipenv update --dev
# @pipenv run ./manage.py tailwind update

su: ## Create superuser.
	@echo "--> Creating superuser"
	@pipenv run ./manage.py createsuperuser

r run: ## Runserver.
	@pipenv run ./manage.py runserver 0.0.0.0:8000

tw: ## Start django-tailwind build server.
	@pipenv run ./manage.py tailwind start

celery: require-celery ## Run Celery worker.
	@pipenv run celery -A core worker --beat --loglevel INFO

ngrok: require-ngrok require-jq ## Run debugserver and ngrok.
	@echo "--> Starting server"
	@pipenv run ./manage.py runserver --noreload 0.0.0.0:8001 > /dev/null 2>&1 &
	@echo "--> Starting ngrok"
	@ngrok http 8001 --region=in --log=stdout > /dev/null 2>&1 &
	@sleep 2
	@curl -s http://127.0.0.1:4040/api/tunnels | jq '.tunnels[0].public_url' -r

kill-ngrok: ## Kill debugserver and ngrok.
	@echo "--> Killing server"
	@kill -15 $(shell ps a | awk '/[r]unserver.*8001/{print $$1}') > /dev/null 2>&1 || { echo "server not running";}
	@echo "--> Killing ngrok"
	@kill -15 $(shell ps a | awk '/[n]grok.*8001/{print $$1}') > /dev/null 2>&1 || { echo "ngrok not running";}
	@echo "RIP"

shell: ## Start django interactive shell.
	@pipenv run ./manage.py shell

db-shell: ## Access db shell.
	@pipenv run ./manage.py dbshell

test: ## Run tests.
	@echo "--> Running tests"
	@pipenv run coverage erase
	@-pipenv run coverage run manage.py test --parallel=$(shell nproc)
	@pipenv run coverage combine > /dev/null
	@pipenv run coverage html
	@pipenv run coverage xml
	@pipenv run coverage report

lint: ## Lint code.
	@echo "--> Formatting code"
	@pre-commit run --all-files
	@echo "All clear!"

deploy: ## Deploy to production.
	@git push heroku main
	@echo "Now look for bugs!"

static: ## Collect static files.
	@echo "--> Collecting static files"
	@pipenv run ./manage.py collectstatic --noinput
