# jd_template

Basis für eine Web-Anwendung mit Django-API und Next.js-Frontend. Lokal läuft alles über Docker Compose: Backend, Frontend, PostgreSQL und Redis.

## Erster Start

Docker, Docker Compose und Make müssen installiert sein. Im Projektroot:

1. Umgebung anlegen.

   ```bash
   cp docker/.env.example docker/.env
   ```

2. Stack bauen und starten. Der erste Lauf zieht die Images und dauert länger.

   ```bash
   make dev
   ```

3. Adressen anzeigen.

   ```bash
   make urls
   ```

4. Prüfen, dass die drei Oberflächen antworten. Die Ports kommen aus `docker/.env`.

   - Frontend: `http://127.0.0.1:3000`
   - Health: `http://127.0.0.1:8000/api/v1/health/` liefert `{"status":"ok"}`
   - Swagger: `http://127.0.0.1:8000/api/docs/`

5. Stack stoppen, wenn die Session zu Ende ist.

   ```bash
   make down
   ```

Sind `8000`, `3000`, `5432` oder `6379` belegt, die Host-Ports in `docker/.env` ändern und `make dev` erneut ausführen. Im Compose-Netz bleiben Backend auf `8000`, Frontend auf `3000`, PostgreSQL auf `5432` und Redis auf `6379`.

Logs eines Dienstes: `make logs backend`. Alles neu starten: `make restart dev`. Weitere Ziele: `make help`.

## Aufbau

```text
backend/          Django, DRF, OpenAPI
frontend/         Next.js
docker/           Compose, .env, Dockerfiles
docs/rules/       Ordnerstruktur, Tests, Dev-Stack
Makefile
```

Fachlichkeit liegt in `backend/apps/<app>`. Eine neue App:

```bash
make create_app <appname>
```

Die App wird registriert und unter `/<appname>/v1/` eingehängt. Ein Frontend-Modul:

```bash
make create_feature <name>
```

Es liegt unter `frontend/src/features/<name>`, ist über `@/features/<name>` erreichbar und hat die Route `/<name>`. Die Form steht in [docs/rules/ordnerstruktur.md](docs/rules/ordnerstruktur.md).

## Tests

```bash
make test
make loadtest
```

`make test` führt pytest im Backend-Container aus. `make loadtest` braucht die Pakete aus `backend/requirements-dev.txt` in `backend/.venv`. Details stehen in [docs/rules/testing.md](docs/rules/testing.md).

## Weitere Regeln

| Datei | Inhalt |
|---|---|
| [docs/rules/ordnerstruktur.md](docs/rules/ordnerstruktur.md) | Apps, Pakete, API-Versionen |
| [docs/rules/testing.md](docs/rules/testing.md) | Unit, Integration, API, Last |
| [docs/rules/dev-stack.md](docs/rules/dev-stack.md) | Compose, Ports, Make |
