# Anleitungen

Die drei Kapitel bauen aufeinander auf. Jedes setzt das vorige Ergebnis voraus und lässt sich danach als Nachschlagewerk nutzen.

| Kapitel | Ergebnis |
|---|---|
| [01 Ubuntu-VM, Docker, UFW, Start](01-ubuntu-vm.md) | Eine Ubuntu-VM startet den Stack mit `make dev`. Frontend und Backend sind auf dem Host HTTPS mit selbstsigniertem Zertifikat |
| [02 Umgebung, Datenbanken, Make](02-umgebung-und-befehle.md) | `docker/.env` ist erklärt, eine weitere Datenbank ist anschließbar, jedes Make-Ziel hat einen Aufruf |
| [03 Eigene Implementierung](03-eigene-implementierung.md) | Eine Fach-App und das passende Frontend-Modul laufen über denselben Browser-Ursprung |

## Was die Kapitel bewusst auslassen

Die verbindliche Form von Apps, Tests und Antworten steht in [docs/rules](../rules/README.md). Die Anleitungen zeigen den Ablauf und verweisen auf die Regel, sobald die Form festliegt.

## Kurzbefehle, sobald die Maschine steht

```bash
cp docker/.env.example docker/.env
make dev
make urls
```

Alle weiteren Befehle stehen in [Kapitel 2](02-umgebung-und-befehle.md).
