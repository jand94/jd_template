# jd_template

Vorlage für eine Web-Anwendung mit Django-API und Next.js-Frontend. Fachlichkeit liegt in eigenen Modulen: eine Django-App unter `backend/apps/<app>`, das passende Frontend unter `frontend/src/features/<feature>`. Seiten, Layout und der gemeinsame HTTP-Client bleiben dünn.

Lokal läuft der Stack über Docker Compose: Backend, Frontend, PostgreSQL und Redis. Anmeldung ist eine Django-Sitzung mit CSRF. Der Browser spricht nur das Frontend an; Next.js leitet `/accounts` und `/media` an Django weiter.

## Voraussetzungen

| Werkzeug | Wofür |
|---|---|
| Docker und Docker Compose | Images, Container, Volumes |
| Make | Ziele in der [Makefile](Makefile) |
| Python 3 | `make create_app` und `make create_feature` laufen auf dem Host |
| Git | Repository klonen |

Node, PostgreSQL und Redis laufen in den Containern. pytest läuft im Backend-Container. TypeScript und ESLint laufen im Frontend-Container.

## Repository klonen

```bash
git clone <repository-url> jd_template
cd jd_template
```

Alle Befehle in dieser Anleitung gelten im Projektroot, dort wo die `Makefile` liegt.

## Umgebung

```bash
cp docker/.env.example docker/.env
```

Die lokale Datei ist `docker/.env`. Die Vorlage [docker/.env.example](docker/.env.example) setzt Host-Ports, Datenbank, Branding und den ersten Superuser. Werte mit Leerzeichen gehören in Anführungszeichen, weil `make urls` die Datei als Shell einliest.

| Variable | Bedeutung |
|---|---|
| `FRONTEND_PORT`, `BACKEND_PORT`, `POSTGRES_PORT`, `REDIS_PORT` | Ports auf dem Rechner |
| `DEBUG`, `SECRET_KEY` | Debug-Betrieb und Signierschlüssel. Ohne Schlüssel läuft nur `DEBUG=true` |
| `EMAIL_BACKEND` | Versand. Lokal die Konsole, Tests nutzen locmem |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Dev-Datenbank |
| `PROJECT_NAME`, `API_TITLE`, `API_DESCRIPTION`, `API_VERSION` | Namen in Oberfläche, OpenAPI, Admin und E-Mails |
| `DEFAULT_FROM_EMAIL` | Absender für ausgehende Mail |
| `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | Erster Admin, nur wenn der Benutzer noch fehlt |

Im Compose-Netz bleiben die Ports fest: Backend `8000`, Frontend `3000`, PostgreSQL `5432`, Redis `6379`. Die Variablen oben sind nur die Ports auf dem Host. Django erreicht die Datenbank über den Dienstnamen `db` und Redis über `redis`.

Sind `8000`, `3000`, `5432` oder `6379` belegt, die Host-Ports in `docker/.env` ändern und `make dev` erneut ausführen. Branding liest das Frontend aus `frontend/src/config/brand.ts`. Compose übergibt die vier Namensvariablen an den Frontend-Container. Nach einer Änderung dort den Stack neu starten, damit der Container die Werte neu liest. Ports, Volumes und Dienste stehen in [docs/rules/dev-stack.md](docs/rules/dev-stack.md).

## Stack starten

```bash
make dev
```

Der erste Lauf baut die Images, installiert Python- und npm-Abhängigkeiten und dauert länger. Danach:

1. PostgreSQL und Redis werden gesund.
2. Das Backend führt `migrate` aus und legt den Superuser aus `DJANGO_SUPERUSER_*` an, falls er fehlt.
3. Das Frontend startet den Next.js-Dev-Server. Fehlt `next` im Volume, führt der Einstieg `npm ci` aus.

```bash
make urls
```

Mit den Ports aus der Vorlage:

| Oberfläche | Adresse |
|---|---|
| Frontend | `http://127.0.0.1:3000` |
| Health | `http://127.0.0.1:8000/api/v1/health/` liefert `{"status":"ok"}` |
| Ready | `http://127.0.0.1:8000/api/v1/ready/` prüft Datenbank und Redis |
| API | `http://127.0.0.1:8000/api/v1/` |
| Swagger | `http://127.0.0.1:8000/api/docs/` |
| OpenAPI-Schema | `http://127.0.0.1:8000/api/schema/` |
| Django-Admin | `http://127.0.0.1:8000/admin/` |

Ohne Sitzung leitet das Frontend auf `/anmelden`. Erreichbar ohne Anmeldung sind nur `/anmelden`, `/registrieren` und `/passwort-vergessen`. Nach der Anmeldung öffnet `/dashboard`. `/` mit Sitzung leitet dorthin weiter. Profil und System liegen unter `/profil` und `/system`.

Der Superuser aus `docker/.env` gilt für das Django-Admin und für die Anmeldung im Frontend. Beide Oberflächen teilen sich die Session-Cookies, weil Cookies nicht an den Port gebunden sind.

Stack beenden:

```bash
make down
```

`make down` entfernt die Container. Datenbank, `node_modules` und der Next-Cache bleiben in den Volumes. `make destroy` löscht die Volumes mit.

## Alltag

`make help` listet jedes Ziel mit Kurztext.

```bash
make logs backend          # Logs eines Dienstes, auch frontend, db, redis
make logs                  # alle Dienste
make restart backend       # ein Dienst
make restart dev           # ganzer Stack
make ps
make shell                 # Shell im Backend, sonst make shell frontend
make psql
make redis-cli
```

Dieselbe Form `make <ziel> <dienst>` gilt für `start`, `stop` und `build`. Erlaubt sind `backend`, `frontend`, `db` und `redis`. `make build` baut die Images von Backend und Frontend. `make rebuild` baut ohne Cache und startet danach.

Django im laufenden Stack:

```bash
make migrate
make makemigrations <app>
make createsuperuser
make check
make manage showmigrations
```

## Fachlichkeit anlegen

App und Feature tragen denselben Zuschnitt, sind aber getrennte Module. Eine App importiert keine andere App über Interna, ein Feature importiert kein anderes Feature. Die Form steht in [docs/rules/ordnerstruktur.md](docs/rules/ordnerstruktur.md).

### Django-App

```bash
make create_app billing
```

Der Name beginnt mit einem Kleinbuchstaben und enthält nur Kleinbuchstaben, Ziffern und Unterstriche. Reserviert sind `apps`, `backend`, `config`, `django`, `test` und `tests`. Python-Schlüsselwörter sind ebenfalls ausgeschlossen.

Das Skript [scripts/create_app.py](scripts/create_app.py):

- legt `backend/apps/billing/` mit Admin, `api/v1`, Exceptions, Migrationen, Models, Services und den Testordnern `unit`, `integration` und `api` an,
- trägt `apps.billing.apps.BillingConfig` im Abschnitt `interne Apps` von `INSTALLED_APPS` ein,
- hängt `path("billing/", include("apps.billing.urls"))` in `backend/backend/urls.py` ein.

Die HTTP-Basis ist `/billing/v1/`. `apps/billing/urls.py` bindet `v1/` ein. Eine spätere Version ist ein Geschwisterpaket von `v1` und bekommt dort einen eigenen `path`. Öffentliche Modelle, Serializer und Views werden im `__init__.py` des jeweiligen Pakets importiert.

Nach dem Anlegen, sobald es Modelle gibt:

```bash
make makemigrations billing
make migrate
```

### Frontend-Feature

```bash
make create_feature billing
```

Dieselbe Zeichenregel. Reserviert sind bestehende Routen und Ordner, darunter `accounts`, `anmelden`, `app`, `components`, `config`, `dashboard`, `features`, `lib`, `media`, `passwort-vergessen`, `profil`, `registrieren` und `system`.

Das Skript [scripts/create_feature.py](scripts/create_feature.py):

- legt `frontend/src/features/billing/` mit `api`, `components`, `hooks`, `schemas`, `types` und `index.ts` an,
- exportiert `BillingScreen` als einzige öffentliche Schnittstelle,
- legt die Route `frontend/src/app/(app)/billing/page.tsx` an, also `/billing`, und verlangt dafür eine Sitzung,
- erzeugt `api/client.ts` mit `createApiClient("/billing/v1")`.

Ein Eintrag in der Navigation ist eine eigene Änderung. Seiten importieren das Feature nur über den Barrel:

```tsx
import { BillingScreen } from "@/features/billing";
```

`components/`, `lib/` und `config/` importieren keine Features. Features importieren keine anderen Features. ESLint prüft das mit `features/boundaries`. Server Components sind der Default. `"use client"` steht nur in der Datei, die Zustand oder Browser-APIs braucht.

HTTP-Aufrufe laufen über `createApiClient` aus `frontend/src/lib/api.ts`. Der Client holt das CSRF-Cookie, sendet `X-CSRFToken`, liest Fehlerfelder und spricht denselben Origin. Das Account-Feature ist das Muster: `frontend/src/features/accounts`.

## Qualität

Der Stack muss laufen. pytest legt die Testdatenbank in PostgreSQL an.

```bash
make test                 # pytest mit Abdeckung
make test-unit
make test-integration
make test-api
make test-frontend        # Vitest
make typecheck            # tsc --noEmit im Frontend
make lint                 # Ruff und ESLint
make lint-python          # nur Ruff
make build-frontend       # next build
make check-deploy         # manage.py check --deploy
make check-migrations     # makemigrations --check
make loadtest             # Locust, 100 Benutzer, 30 Sekunden
```

`LOCUST_USERS`, `LOCUST_SPAWN_RATE` und `LOCUST_RUN_TIME` ändern den Lastlauf. Locust braucht `backend/.venv` und die Pakete aus `backend/requirements-dev.txt`. Schichten, Marker und Ablage stehen in [docs/rules/testing.md](docs/rules/testing.md).

CI liegt in [.github/workflows/ci.yml](.github/workflows/ci.yml). Bei Push und Pull Request kopiert der Lauf `docker/.env.example` nach `docker/.env`, startet den Stack und führt Deploy-Check, Migrationscheck, pytest, Vitest, Typecheck, Lint und den Frontend-Build aus.

Produktion startet über `make prod`, nachdem `docker/.env.prod.example` nach `docker/.env.prod` kopiert wurde. Ablauf und Variablen stehen in [docs/rules/deploy.md](docs/rules/deploy.md).

## Dokumentation

| Datei | Inhalt |
|---|---|
| [docs/rules/README.md](docs/rules/README.md) | Index der verbindlichen Regeln |
| [docs/rules/ordnerstruktur.md](docs/rules/ordnerstruktur.md) | Repository, Apps, Pakete, API-Versionen, Frontend-Module |
| [docs/rules/dev-stack.md](docs/rules/dev-stack.md) | Compose, Ports, Volumes, Make |
| [docs/rules/testing.md](docs/rules/testing.md) | Unit, Integration, API, Last |
| [docs/rules/api.md](docs/rules/api.md) | Rechte, Seiten, Fehlerform |
| [docs/rules/deploy.md](docs/rules/deploy.md) | Produktion, Umgebung, Bereitschaft |

## Aufbau

```text
backend/                 Django-Projekt, Konfiguration in backend/backend
  apps/<app>/            eine Fach-App, HTTP unter /<app>/v1/
frontend/                Next.js, Anwendungscode in src/
  src/app/               Routen und Layouts
  src/features/<name>/   ein Modul, öffentliche Schnittstelle index.ts
  src/lib/api.ts         gemeinsamer Client
  src/components/        UI ohne Fachlichkeit
docker/                  Compose, .env.example, Dockerfiles
docs/rules/              Ordnerstruktur, Tests, Dev-Stack
scripts/                 create_app.py, create_feature.py
.github/workflows/       CI
Makefile
```
