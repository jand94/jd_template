# Dev-Stack

Der lokale Stack ist Docker Compose. Host-Ports und der Datenbankzugang stehen in `docker/.env`.

| Dienst | Image | Host-Port-Variable | Port im Compose-Netz |
|---|---|---|---|
| proxy | nginx | `FRONTEND_PORT` → 443, `BACKEND_PORT` → 8443 | TLS zum Browser |
| frontend | Next.js | keiner | 3000, HTTP |
| backend | Django | keiner | 8000, HTTP |
| db | PostgreSQL 18 | `POSTGRES_PORT` | 5432 |
| redis | Redis 8.10 | `REDIS_PORT` | 6379 |

`make dev` erzeugt `docker/certs/dev.crt` und `docker/certs/dev.key`, wenn sie fehlen oder in weniger als 30 Tagen ablaufen. Der Dienst `proxy` beendet TLS mit diesem Zertifikat. Der Browser spricht `https://127.0.0.1:<FRONTEND_PORT>` und `https://127.0.0.1:<BACKEND_PORT>`. Zwischen den Containern bleibt HTTP. Nginx setzt `X-Forwarded-Proto: https` und schreibt Weiterleitungen von `http://` auf `https://` um. Session- und CSRF-Cookies tragen im Dev-Stack das Secure-Flag. `DEBUG` bleibt an, deshalb bleiben HSTS und die HTTPS-Umleitung von Django aus.

Im Container spricht Django die Datenbank über `POSTGRES_HOST=db` und Redis über `REDIS_HOST=redis` an, jeweils auf dem internen Port. Die Variablen in `.env` sind die Ports auf dem Rechner. `REDIS_PASSWORD` gilt für Redis und den Django-Cache. `make redis-cli` nutzt dasselbe Passwort über `REDISCLI_AUTH`.

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

`make restart dev` startet den ganzen Stack neu. `make restart backend`, `make restart frontend`, `make restart proxy`, `make restart db` und `make restart redis` treffen einen Dienst. Dieselbe Form gilt für `start`, `stop` und `logs`.

`make build` und `make build backend` bauen die Images von Backend und Frontend. `make rebuild` baut ohne Cache und startet danach. `make destroy` entfernt die Volumes, also auch die Datenbank.

`make migrate`, `make makemigrations <app>`, `make createsuperuser`, `make shell`, `make psql` und `make redis-cli` arbeiten im laufenden Stack. `make test` und `make lint-python` prüfen das Backend, `make test-frontend`, `make typecheck`, `make lint` und `make build-frontend` das Frontend. `make prod` startet die Produktionsstufe aus [deploy.md](deploy.md). Die vollständige Liste liefert `make help`.
