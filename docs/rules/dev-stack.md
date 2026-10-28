# Dev-Stack

Der lokale Stack ist Docker Compose. Host-Ports und der Datenbankzugang stehen in `docker/.env`.

| Dienst | Image | Host-Port-Variable | Port im Compose-Netz |
|---|---|---|---|
| frontend | Next.js | `FRONTEND_PORT` | 3000 |
| backend | Django | `BACKEND_PORT` | 8000 |
| db | PostgreSQL 18 | `POSTGRES_PORT` | 5432 |
| redis | Redis 8.10 | `REDIS_PORT` | 6379 |

Im Container spricht Django die Datenbank über `POSTGRES_HOST=db` und Redis über `REDIS_HOST=redis` an, jeweils auf dem internen Port. Die Variablen in `.env` sind die Ports auf dem Rechner.

`PROJECT_NAME`, `API_TITLE`, `API_DESCRIPTION` und `API_VERSION` gelten für Backend und Frontend. Das Frontend liest sie in `src/config/brand.ts`. Compose übergibt diese vier Variablen an den Frontend-Container.

PostgreSQL speichert Daten im Volume `postgres_data` unter `/var/lib/postgresql`. Redis ist Cache. Sessions liegen zusätzlich in PostgreSQL (`cached_db`).

## Alltag

```bash
make dev
make urls
make logs backend
make restart backend
make down
```

`make restart dev` startet den ganzen Stack neu. `make restart backend`, `make restart frontend`, `make restart db` und `make restart redis` treffen einen Dienst. Dieselbe Form gilt für `start`, `stop` und `logs`.

`make build` und `make build backend` bauen die Images von Backend und Frontend. `make rebuild` baut ohne Cache und startet danach. `make destroy` entfernt die Volumes, also auch die Datenbank.

`make migrate`, `make makemigrations <app>`, `make createsuperuser`, `make shell`, `make psql` und `make redis-cli` arbeiten im laufenden Stack. `make test` prüft das Backend, `make typecheck` und `make lint` das Frontend. Die vollständige Liste liefert `make help`.
