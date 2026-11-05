#!/bin/sh
# Selbstsigniertes Zertifikat für den Dev-Proxy. Gilt für localhost und 127.0.0.1.
# Ohne --force bleibt ein Zertifikat liegen, das noch mindestens 30 Tage gilt.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
DEST="$ROOT/docker/certs"
CRT="$DEST/dev.crt"
KEY="$DEST/dev.key"
FORCE=0

if [ "${1:-}" = "--force" ]; then
  FORCE=1
elif [ -n "${1:-}" ]; then
  echo "Aufruf: generate_dev_cert.sh [--force]" >&2
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl fehlt. Auf Ubuntu: sudo apt install openssl" >&2
  exit 1
fi

mkdir -p "$DEST"

if [ "$FORCE" -eq 0 ] && [ -f "$CRT" ] && [ -f "$KEY" ]; then
  if openssl x509 -checkend 2592000 -noout -in "$CRT" >/dev/null 2>&1; then
    exit 0
  fi
fi

openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes \
  -keyout "$KEY" \
  -out "$CRT" \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" \
  -addext "keyUsage=digitalSignature,keyEncipherment" \
  -addext "extendedKeyUsage=serverAuth"

chmod 600 "$KEY"
chmod 644 "$CRT"
echo "Dev-Zertifikat geschrieben: $CRT"
