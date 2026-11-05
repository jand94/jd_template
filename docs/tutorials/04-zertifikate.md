# Zertifikate in Entwicklung und Produktion

Der Browser spricht den Stack über HTTPS an. Dieses Kapitel ist die Referenz dafür: welche Datei wo liegt, welche Namen im Zertifikat stehen, und wie ein Client der ausstellenden Stelle vertraut.

Entwicklung und Produktion haben getrennte Zertifikate. Die Dev-CA öffnet nicht die Produktionsseite, und umgekehrt.

| | Entwicklung | Produktion, `generate` | Produktion, `own` |
|---|---|---|---|
| Umgebung | `docker/.env` | `docker/.env.prod` | `docker/.env.prod` |
| Schalter | immer dieser Weg | `PROD_TLS_MODE=generate` | `PROD_TLS_MODE=own` |
| Zusätzliche Namen | `DEV_CERT_DNS` | `PROD_CERT_DNS` | ungenutzt |
| Root-CA, nur öffentlich | `docker/certs/dev-ca.crt` | `docker/certs/prod/prod-ca.crt` | die CA des mitgebrachten Zertifikats |
| Schlüssel der CA | `docker/certs/dev-ca.key` | `docker/certs/prod/prod-ca.key` | bleibt beim Aussteller |
| Serverzertifikat | `docker/certs/dev.crt` | `docker/certs/prod/prod.crt` | Kopie von `PROD_TLS_CERT` |
| Serverschlüssel | `docker/certs/dev.key` | `docker/certs/prod/prod.key` | Kopie von `PROD_TLS_KEY` |
| Proxy | `docker/proxy/nginx.conf` | `docker/proxy/nginx.prod.conf` | dieselbe Datei |
| Anlegen | `make dev` oder `make certs` | `make prod` | `make prod` kopiert die Dateien |

Auf den Client, von dem der Browser die Seite öffnet, kommt nur die Root-CA. Die Schlüssel bleiben auf der Maschine, die den Stack betreibt. Nginx liest das Serverzertifikat, nicht die CA.

## Namen, die immer enthalten sind

Jedes erzeugte Serverzertifikat nennt diese Einträge, unabhängig von `DEV_CERT_DNS` und `PROD_CERT_DNS`:

- `localhost`
- `127.0.0.1`
- der kurze Hostname der Maschine, sofern er nicht `localhost` ist
- jede globale IPv4-Adresse der Maschine, auch die Adressen der Docker-Bridges

Der Common Name ist `localhost`. Der Browser prüft die Liste der alternativen Namen. Anzeigen:

```bash
openssl x509 -in docker/certs/dev.crt -noout -ext subjectAltName
openssl x509 -in docker/certs/prod/prod.crt -noout -ext subjectAltName
```

Weitere DNS-Namen kommen kommagetrennt in die passende Variable. Leerzeichen um die Kommas sind erlaubt. Eine IPv4-Adresse in derselben Liste wird als IP eingetragen, ein anderer Wert als DNS-Name.

```bash
DEV_CERT_DNS=dev.local, app.example
PROD_CERT_DNS=example.com, www.example.com
```

Ein Name, der in der Liste fehlt, ergibt im Browser `ERR_CERT_COMMON_NAME_INVALID`, auch wenn die CA bereits vertraut wird.

## Entwicklung

`make dev` ruft `make certs` auf. Das Skript `scripts/generate_dev_cert.sh` liest `DEV_CERT_DNS` aus `docker/.env` und schreibt die Dateien nach `docker/certs/`. Die Zeile in der Umgebungsdatei:

```bash
# Zusätzliche DNS-Namen, kommagetrennt.
# Immer enthalten: localhost, 127.0.0.1, der Hostname und die IPv4-Adressen.
DEV_CERT_DNS=
```

Die Root-CA `jd_template dev CA` gilt zehn Jahre. Sie wird nur angelegt, wenn `dev-ca.crt` oder `dev-ca.key` fehlt. Das Serverzertifikat gilt 825 Tage und wird neu signiert, wenn eine dieser Bedingungen zutrifft:

- `dev.crt` oder `dev.key` fehlt
- das Serverzertifikat gehört nicht zu dieser CA
- es läuft in weniger als 30 Tagen ab
- `DEV_CERT_DNS` oder die Adressen der Maschine haben sich geändert

Nach einer Änderung an `DEV_CERT_DNS`:

```bash
make certs
make restart proxy
```

`make dev` allein erneuert die Dateien, ein schon laufender Proxy liest sie erst nach dem Neustart. Nginx hängt sie unter `/certs/dev.crt` und `/certs/dev.key` ein und bindet auf dem Host `FRONTEND_PORT` an Port 443 im Container und `BACKEND_PORT` an Port 8443. Beides ist TLS. Zwischen den Containern bleibt HTTP. Der Proxy setzt `X-Forwarded-Proto: https`.

`DEBUG` bleibt in der Entwicklung an. Django setzt deshalb kein HSTS, und die HTTPS-Umleitung von Django bleibt aus. Session- und CSRF-Cookies tragen trotzdem das Secure-Flag, weil der Compose-Block das für den Dev-Stack setzt.

### Root-CA auf dem Client installieren

Datei: `docker/certs/dev-ca.crt`. Kopieren, zum Beispiel:

```bash
scp user@vm:/opt/jd_template/docker/certs/dev-ca.crt .
```

Ubuntu, für Programme, die den Systemspeicher lesen:

```bash
sudo cp dev-ca.crt /usr/local/share/ca-certificates/jd-template-dev-ca.crt
sudo update-ca-certificates
```

Windows, Eingabeaufforderung als Administrator:

```bat
certutil -addstore -f ROOT dev-ca.crt
```

Chrome unter Windows und Linux liest diesen Speicher. Firefox hat einen eigenen: Einstellungen, Datenschutz und Sicherheit, Zertifikate, Zertifizierungsstellen, importieren. Danach die Seite neu laden. Ein bereits geöffnetes Warnfenster merkt sich die Ablehnung für diese Sitzung.

`curl` ohne diesen Speicher:

```bash
curl -fsS --cacert docker/certs/dev-ca.crt https://127.0.0.1:3000/anmelden
curl -fsS --cacert docker/certs/dev-ca.crt https://127.0.0.1:8000/api/v1/health/
```

Die Ports kommen aus `docker/.env`. `make urls` zeigt die Adressen mit `https`.

Eine neue Dev-CA, die danach auf jedem Client neu importiert werden muss:

```bash
rm -f docker/certs/dev-ca.crt docker/certs/dev-ca.key docker/certs/dev-ca.srl
make certs
make restart proxy
```

Ein erneuertes Serverzertifikat derselben CA braucht keinen neuen Import.

## Produktion

`make prod` führt zuerst `scripts/prepare_prod_tls.sh` aus und startet danach `docker/compose.prod.yml`. Der Proxy bindet `FRONTEND_PORT` als HTTPS. Für einen öffentlichen Server ist das oft `443`. Backend, PostgreSQL und Redis veröffentlichen keinen Host-Port.

Die Vorlage ist `docker/.env.prod.example`. Die Arbeitsdatei `docker/.env.prod` steht in `.gitignore`.

### `PROD_TLS_MODE=generate`

Der Weg ist derselbe wie in der Entwicklung, mit eigener CA `jd_template prod CA` und dem Namenszusatz aus `PROD_CERT_DNS`.

```bash
PROD_TLS_MODE=generate
PROD_CERT_DNS=example.com,www.example.com
```

`make prod` schreibt:

- `docker/certs/prod/prod-ca.crt` für den Client
- `docker/certs/prod/prod-ca.key` bleibt auf dem Server
- `docker/certs/prod/prod.crt` und `docker/certs/prod/prod.key` für Nginx

Dieselbe Erneuerungsregel wie in der Entwicklung: die CA bleibt, das Serverzertifikat wird ersetzt, wenn die Namen sich ändern, die Datei fehlt oder in weniger als 30 Tagen abläuft. Eine geänderte `PROD_CERT_DNS` braucht deshalb nur:

```bash
make prod
```

Der Client importiert `docker/certs/prod/prod-ca.crt` mit denselben Befehlen wie die Dev-CA, unter einem anderen Dateinamen im Speicher, zum Beispiel `jd-template-prod-ca.crt`. Zwei CAs im Speicher stören sich nicht.

Prüfung von der Maschine aus:

```bash
curl -fsS --cacert docker/certs/prod/prod-ca.crt "https://127.0.0.1:${FRONTEND_PORT}/anmelden"
```

`127.0.0.1` ist immer ein Name im Zertifikat. Der öffentliche Name muss in `PROD_CERT_DNS` stehen, sonst warnt der Browser beim Aufruf über diesen Namen.

### `PROD_TLS_MODE=own`

Ein vorhandenes Zertifikat wird an den Proxy kopiert. `PROD_CERT_DNS` bleibt ungenutzt. Die Pfade sind absolut oder relativ zum Projektroot. `PROD_TLS_CERT` ist die Kette, einschließlich Zwischenstellen, `PROD_TLS_KEY` der dazu passende Schlüssel.

```bash
PROD_TLS_MODE=own
PROD_TLS_CERT=/etc/letsencrypt/live/example.com/fullchain.pem
PROD_TLS_KEY=/etc/letsencrypt/live/example.com/privkey.pem
```

`make prod` kopiert beide Dateien nach `docker/certs/prod/prod.crt` und `docker/certs/prod/prod.key`. Nginx liest nur diese Kopien. Fehlt eine der beiden Quelldateien, bricht `make prod` vor dem Start ab.

Die Clients vertrauen dann der CA, die dieses Zertifikat ausgestellt hat. Eine eigene `prod-ca.crt` entsteht in diesem Modus nicht. `curl` ohne `--cacert` genügt, sobald diese CA im Systemspeicher liegt, wie bei einem öffentlichen Let's-Encrypt-Zertifikat.

Nach einem erneuerten Let's-Encrypt-Lauf erneut `make prod`, damit die Kopie im Ordner `docker/certs/prod/` die neue Kette enthält.

## Was der Proxy an Django weitergibt

Der Proxy setzt `X-Forwarded-Proto` fest auf `https`. Ein vom Browser mitgeschickter Wert kommt bei Next.js nicht an. Next.js ruft Django unter `http://backend:8000` auf. Die Route-Handler unter `frontend/src/app/accounts` und `frontend/src/app/media` reichen `x-forwarded-proto` weiter. In der Produktion ist `DEBUG` aus. Fehlt der Header dann bei Django, antwortet Django auf unsichere Methoden mit einer Weiterleitung auf HTTPS.

`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` und `FRONTEND_ORIGIN` in `docker/.env.prod` nennen dieselbe öffentliche Adresse, Schema `https`, ohne Pfad am Ende von `FRONTEND_ORIGIN`. Ein Name, der nur im Zertifikat steht und nicht in `ALLOWED_HOSTS`, besteht die TLS-Prüfung und scheitert danach an Django.

## Dateien, die nicht ins Repository gehören

`.gitignore` schließt die Zertifikate und Schlüssel unter `docker/certs/` und `docker/certs/prod/` aus. Übrig bleibt `docker/certs/prod/.gitkeep`, damit der Ordner existiert. Ein Schlüssel in einem Commit wird ersetzt: Dev-CA löschen und `make certs`, Prod-CA löschen und `make prod`, und die alten Dateien auf den Clients aus dem Vertrauensspeicher nehmen.

## Wenn der Browser warnt

| Meldung | Nächster Schritt |
|---|---|
| `ERR_CERT_AUTHORITY_INVALID` | Die passende Root-CA importieren: `dev-ca.crt` oder `prod-ca.crt`. Bei `PROD_TLS_MODE=own` die CA des mitgebrachten Zertifikats |
| `ERR_CERT_COMMON_NAME_INVALID` | Den aufgerufenen Namen in `DEV_CERT_DNS` oder `PROD_CERT_DNS` eintragen und den Proxy neu starten |
| Nginx startet nicht, das Zertifikat fehlt | Entwicklung: `make certs`. Produktion: `make prod`. Bei `own` die beiden Pfade prüfen |
| Seite lädt über HTTPS, Anmeldung leitet im Kreis | `CSRF_TRUSTED_ORIGINS` enthält Schema, Host und bei abweichendem Port auch den Port |

Die aufgelöste Prod-Compose-Datei, ohne die Schlüssel im Klartext zu brauchen, zeigt der Port des Proxys:

```bash
docker compose --env-file docker/.env.prod -f docker/compose.prod.yml ps proxy
```
