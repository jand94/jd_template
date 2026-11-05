#!/bin/sh
# TLS für den Prod-Proxy.
# PROD_TLS_MODE=generate erzeugt Root-CA und Serverzertifikat wie in der Entwicklung.
# PROD_TLS_MODE=own kopiert PROD_TLS_CERT und PROD_TLS_KEY an den Proxy.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
ENV_FILE="$ROOT/docker/.env.prod"
DEST="$ROOT/docker/certs/prod"

if [ ! -f "$ENV_FILE" ]; then
  echo "docker/.env.prod fehlt. Vorlage: cp docker/.env.prod.example docker/.env.prod" >&2
  exit 1
fi

read_env() {
  key=$1
  line=$(grep -E "^[[:space:]]*${key}=" "$ENV_FILE" | tail -n 1 || true)
  [ -n "$line" ] || return 0
  val=${line#*=}
  val=$(printf '%s' "$val" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
  case "$val" in
    \"*) val=${val#\"}; val=${val%\"} ;;
    \'*) val=${val#\'}; val=${val%\'} ;;
  esac
  printf '%s' "$val"
}

resolve_path() {
  case "$1" in
    /*) printf '%s' "$1" ;;
    *) printf '%s' "$ROOT/$1" ;;
  esac
}

mode=$(read_env PROD_TLS_MODE)
case "$mode" in
  generate)
    dns=$(read_env PROD_CERT_DNS)
    exec "$ROOT/scripts/generate_cert.sh" \
      --dest "$DEST" \
      --name prod \
      --ca-cn "jd_template prod CA" \
      --dns "$dns"
    ;;
  own)
    cert=$(read_env PROD_TLS_CERT)
    key=$(read_env PROD_TLS_KEY)
    if [ -z "$cert" ] || [ -z "$key" ]; then
      echo "PROD_TLS_MODE=own braucht PROD_TLS_CERT und PROD_TLS_KEY in docker/.env.prod." >&2
      exit 1
    fi
    cert=$(resolve_path "$cert")
    key=$(resolve_path "$key")
    if [ ! -f "$cert" ] || [ ! -f "$key" ]; then
      echo "Zertifikat oder Schlüssel fehlt: $cert / $key" >&2
      exit 1
    fi
    mkdir -p "$DEST"
    if [ ! -f "$DEST/prod.crt" ] || ! cmp -s "$cert" "$DEST/prod.crt"; then
      cp "$cert" "$DEST/prod.crt"
    fi
    if [ ! -f "$DEST/prod.key" ] || ! cmp -s "$key" "$DEST/prod.key"; then
      cp "$key" "$DEST/prod.key"
    fi
    chmod 644 "$DEST/prod.crt"
    chmod 600 "$DEST/prod.key"
    echo "Eigenes Zertifikat übernommen: $DEST/prod.crt"
    ;;
  *)
    echo "PROD_TLS_MODE muss generate oder own sein, ist: ${mode:-leer}" >&2
    exit 1
    ;;
esac
