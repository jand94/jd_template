# Anleitungen

Die ersten drei Kapitel bauen aufeinander auf. Das Zertifikatskapitel ist die Referenz für HTTPS in Entwicklung und Produktion und setzt den laufenden Stack voraus.

| Kapitel | Ergebnis |
|---|---|
| [01 Ubuntu-VM, Docker, UFW, Start](01-ubuntu-vm.md) | Eine Ubuntu-VM startet den Stack mit `make dev`. Frontend und Backend sind auf dem Host HTTPS |
| [02 Umgebung, Datenbanken, Make](02-umgebung-und-befehle.md) | `docker/.env` ist erklärt, eine weitere Datenbank ist anschließbar, jedes Make-Ziel hat einen Aufruf |
| [03 Eigene Implementierung](03-eigene-implementierung.md) | Eine Fach-App und das passende Frontend-Modul laufen über denselben Browser-Ursprung |
| [04 Zertifikate](04-zertifikate.md) | Dev- und Prod-Zertifikat, zusätzliche DNS-Namen, eigenes Prod-Zertifikat, Import der Root-CA |

## Was die Kapitel bewusst auslassen

Die verbindliche Form von Apps, Tests und Antworten steht in [docs/rules](../rules/README.md). Die Anleitungen zeigen den Ablauf und verweisen auf die Regel, sobald die Form festliegt.

## Kurzbefehle, sobald die Maschine steht

```bash
cp docker/.env.example docker/.env
make dev
make urls
```

Alle weiteren Befehle stehen in [Kapitel 2](02-umgebung-und-befehle.md).
