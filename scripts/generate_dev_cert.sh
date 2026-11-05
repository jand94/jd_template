#!/bin/sh
# Dev-Zertifikat. Zusätzliche Namen kommen aus DEV_CERT_DNS in docker/.env.
set -eu

ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
FORCE=
if [ "${1:-}" = "--force" ]; then
  FORCE=--force
elif [ -n "${1:-}" ]; then
  echo "Aufruf: generate_dev_cert.sh [--force]" >&2
  exit 1
fi

dns=
if [ -f "$ROOT/docker/.env" ]; then
  line=$(grep -E '^[[:space:]]*DEV_CERT_DNS=' "$ROOT/docker/.env" | tail -n 1 || true)
  if [ -n "$line" ]; then
    dns=${line#*=}
    dns=$(printf '%s' "$dns" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    case "$dns" in
      \"*) dns=${dns#\"}; dns=${dns%\"} ;;
      \'*) dns=${dns#\'}; dns=${dns%\'} ;;
    esac
  fi
fi

exec "$ROOT/scripts/generate_cert.sh" \
  --dest "$ROOT/docker/certs" \
  --name dev \
  --ca-cn "jd_template dev CA" \
  --dns "$dns" \
  $FORCE
