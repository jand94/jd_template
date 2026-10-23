.DEFAULT_GOAL := help

COMPOSE := docker compose --env-file docker/.env -f docker/compose.yml
SERVICES := backend frontend db redis

LOCUST_USERS ?= 100
LOCUST_SPAWN_RATE ?= 10
LOCUST_RUN_TIME ?= 30s

ARG_VERBS := restart start stop logs build makemigrations manage

ifeq (create_app,$(firstword $(MAKECMDGOALS)))
  APP_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

ifeq ($(firstword $(MAKECMDGOALS)),$(filter $(firstword $(MAKECMDGOALS)),$(ARG_VERBS)))
  ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
endif

.PHONY: help dev up down restart start stop build rebuild logs ps shell \
	migrate makemigrations createsuperuser manage check \
	test test-unit test-integration test-api loadtest \
	lint install-backend install-frontend \
	psql redis-cli urls config pull destroy create_app clean-pyc

##@ Hilfe

help: ## Ziele und Aufrufe anzeigen
	@awk 'BEGIN {FS = ":.*##"; printf "Verwendung: make <ziel> [dev|backend|frontend|db|redis]\n"} \
		/^##@/ {printf "\n%s\n", substr($$0, 5)} \
		/^[a-zA-Z0-9_-]+:.*?## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

urls: ## Lokale URLs aus docker/.env anzeigen
	@set -a && . docker/.env && set +a && \
	printf 'Frontend   http://127.0.0.1:%s\n' "$$FRONTEND_PORT" && \
	printf 'API        http://127.0.0.1:%s/api/v1/\n' "$$BACKEND_PORT" && \
	printf 'Health     http://127.0.0.1:%s/api/v1/health/\n' "$$BACKEND_PORT" && \
	printf 'Swagger    http://127.0.0.1:%s/api/docs/\n' "$$BACKEND_PORT" && \
	printf 'Schema     http://127.0.0.1:%s/api/schema/\n' "$$BACKEND_PORT" && \
	printf 'Postgres   127.0.0.1:%s\n' "$$POSTGRES_PORT" && \
	printf 'Redis      127.0.0.1:%s\n' "$$REDIS_PORT"

##@ Stack

ifneq ($(filter dev,$(ARGS)),dev)
dev: ## Dev-Stack starten
	$(COMPOSE) up -d
endif

up: ## Wie dev: Stack im Hintergrund starten
	$(COMPOSE) up -d

down: ## Stack stoppen, Container entfernen, Volumes behalten
	$(COMPOSE) down

restart: ## Neu starten. make restart | make restart dev | make restart backend
	$(call compose_services,restart)

start: ## Gestoppte Container starten. make start frontend
	$(call compose_services,start)

stop: ## Container stoppen, ohne sie zu entfernen. make stop db
	$(call compose_services,stop)

ps: ## Laufende Compose-Dienste anzeigen
	$(COMPOSE) ps

logs: ## Logs folgen. make logs | make logs backend
	$(call compose_services,logs -f --tail=200)

config: ## Aufgelöste Compose-Konfiguration anzeigen
	$(COMPOSE) config

pull: ## Basis-Images ziehen (Postgres, Redis)
	$(COMPOSE) pull

destroy: ## Stack stoppen und Volumes löschen (Datenbank, Frontend-Caches)
	$(COMPOSE) down -v

##@ Build

build: ## Images bauen. make build | make build backend | make build frontend
	@svc="$(ARGS)"; \
	if [ -z "$$svc" ] || [ "$$svc" = "dev" ] || [ "$$svc" = "all" ]; then \
	  $(COMPOSE) build; \
	else \
	  for name in $$svc; do \
	    case $$name in \
	      backend|frontend) ;; \
	      *) echo "build gilt für backend und frontend"; exit 1 ;; \
	    esac; \
	  done; \
	  $(COMPOSE) build $$svc; \
	fi

rebuild: ## Images ohne Cache bauen und Stack starten
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

##@ Shell

shell: ## Shell öffnen. make shell | make shell db
	@svc="$(ARGS)"; \
	if [ -z "$$svc" ] || [ "$$svc" = "dev" ]; then svc=backend; fi; \
	case $$svc in \
	  backend|frontend|db|redis) ;; \
	  *) echo "Unbekannter Dienst: $$svc"; echo "Erlaubt: backend, frontend, db, redis"; exit 1 ;; \
	esac; \
	$(COMPOSE) exec $$svc sh

psql: ## psql in der Dev-Datenbank öffnen
	$(COMPOSE) exec db sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

redis-cli: ## redis-cli im Redis-Container öffnen
	$(COMPOSE) exec redis redis-cli

##@ Django

migrate: ## Migrationen im Backend ausführen
	$(COMPOSE) exec -T backend python manage.py migrate

makemigrations: ## Migrationen erzeugen. make makemigrations api
	$(COMPOSE) exec -T backend python manage.py makemigrations $(ARGS)

createsuperuser: ## Django-Superuser anlegen
	$(COMPOSE) exec backend python manage.py createsuperuser

manage: ## manage.py ausführen. make manage showmigrations
	@if [ -z "$(ARGS)" ]; then echo "Aufruf: make manage <befehl>"; exit 1; fi
	$(COMPOSE) exec -T backend python manage.py $(ARGS)

check: ## Django-Systemcheck
	$(COMPOSE) exec -T backend python manage.py check

create_app: ## App anlegen. make create_app <appname>
	python3 scripts/create_app.py $(APP_ARGS)

##@ Tests

test: ## pytest mit Abdeckung im Backend-Container
	$(COMPOSE) exec -T backend pytest

test-unit: ## Nur Unit-Tests
	$(COMPOSE) exec -T backend pytest -m unit

test-integration: ## Nur Integrationstests
	$(COMPOSE) exec -T backend pytest -m integration

test-api: ## Nur API-Tests
	$(COMPOSE) exec -T backend pytest -m api

loadtest: ## Locust, Standard 100 Benutzer für 30s. LOCUST_USERS=10 make loadtest
	@set -a && . docker/.env && set +a && \
	backend/.venv/bin/locust -f backend/locustfile.py --headless \
	-u $(LOCUST_USERS) -r $(LOCUST_SPAWN_RATE) -t $(LOCUST_RUN_TIME) \
	--host http://127.0.0.1:$$BACKEND_PORT

##@ Qualität

lint: ## ESLint im Frontend-Container
	$(COMPOSE) exec -T frontend npm run lint

install-backend: ## Python-Abhängigkeiten im Backend-Container installieren
	$(COMPOSE) exec -T backend pip install --no-cache-dir -r requirements-dev.txt

install-frontend: ## npm ci im Frontend-Container
	$(COMPOSE) exec -T frontend npm ci

clean-pyc: ## Python-Bytecode unter backend/ entfernen
	find backend -type d -name __pycache__ -prune -exec rm -rf {} +

ifeq (create_app,$(firstword $(MAKECMDGOALS)))
  ifneq ($(APP_ARGS),)
    $(eval $(APP_ARGS):;@:)
  endif
endif

ifeq ($(firstword $(MAKECMDGOALS)),$(filter $(firstword $(MAKECMDGOALS)),$(ARG_VERBS)))
  ifneq ($(ARGS),)
    $(eval $(ARGS):;@:)
  endif
endif

define compose_services
@svc="$(ARGS)"; \
if [ -z "$$svc" ] || [ "$$svc" = "dev" ] || [ "$$svc" = "all" ]; then svc=""; fi; \
for name in $$svc; do \
  case $$name in \
    backend|frontend|db|redis) ;; \
    *) echo "Unbekannter Dienst: $$name"; echo "Erlaubt: backend, frontend, db, redis, dev"; exit 1 ;; \
  esac; \
done; \
$(COMPOSE) $(1) $$svc
endef
