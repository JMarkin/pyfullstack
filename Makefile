#!make
SHELL=/bin/bash

$(shell [ ! -f .env ] && cp .env.example .env)

include .env
export $(shell sed 's/=.*//' .env)

export COMPOSE_PROJECT_NAME?=pyfullstack

# включение docker buildkit для быстрой и более удобной сборки
export DOCKER_BUILDKIT=1

COMPOSE_CMD=docker compose -f docker/dev/docker-compose.yml

C_USER?=app
C_NAME?=back

run:
	$(COMPOSE_CMD) up --build

run-detach:
	$(COMPOSE_CMD) up -d

shell:
	$(COMPOSE_CMD) exec $(C_NAME) /bin/bash

shell-tmp:
	$(COMPOSE_CMD) run --rm $(C_NAME) /bin/bash

run-prod:
	docker compose -p $(COMPOSE_PROJECT_NAME)-prod -f docker/prod/docker-compose.yml up --build
