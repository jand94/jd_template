#!/bin/sh
# Root-CA und davon signiertes Serverzertifikat.
# Aufruf: generate_cert.sh --dest DIR --name NAME --ca-cn TEXT [--dns LISTE] [--force]
# Immer enthalten: localhost, 127.0.0.1, der Hostname und die globalen IPv4-Adressen.
# --dns hängt weitere Namen an, kommagetrennt. Eine IPv4-Adresse wird als IP eingetragen.
set -eu

DEST=
NAME=
CA_CN=
DNS=
FORCE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --dest) DEST=$2; shift 2 ;;
    --name) NAME=$2; shift 2 ;;
    --ca-cn) CA_CN=$2; shift 2 ;;
    --dns) DNS=$2; shift 2 ;;
    --force) FORCE=1; shift ;;
    *)
      echo "Aufruf: generate_cert.sh --dest DIR --name NAME --ca-cn TEXT [--dns LISTE] [--force]" >&2
      exit 1
      ;;
  esac
done

if [ -z "$DEST" ] || [ -z "$NAME" ] || [ -z "$CA_CN" ]; then
  echo "Aufruf: generate_cert.sh --dest DIR --name NAME --ca-cn TEXT [--dns LISTE] [--force]" >&2
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1; then
  echo "openssl fehlt. Auf Ubuntu: sudo apt install openssl" >&2
  exit 1
fi

mkdir -p "$DEST"

CA_CRT="$DEST/$NAME-ca.crt"
CA_KEY="$DEST/$NAME-ca.key"
CA_SRL="$DEST/$NAME-ca.srl"
CRT="$DEST/$NAME.crt"
KEY="$DEST/$NAME.key"
EXT="$DEST/server.ext"

write_server_ext() {
  sans="DNS:localhost,IP:127.0.0.1"
  host=$(hostname -s 2>/dev/null || true)
  if [ -n "$host" ] && [ "$host" != "localhost" ]; then
    sans="$sans,DNS:$host"
  fi
  if command -v ip >/dev/null 2>&1; then
    for addr in $(ip -4 -o addr show scope global 2>/dev/null | awk '{print $4}' | cut -d/ -f1); do
      case ",$sans," in
        *",IP:$addr,"*) ;;
        *) sans="$sans,IP:$addr" ;;
      esac
    done
  fi
  rest=$DNS
  while [ -n "$rest" ]; do
    case "$rest" in
      *,*) name=${rest%%,*} rest=${rest#*,} ;;
      *) name=$rest rest= ;;
    esac
    name=$(printf '%s' "$name" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
    case "$name" in
      ""|"#"*) continue ;;
    esac
    case "$name" in
      [0-9]*.[0-9]*.[0-9]*.[0-9]*) kind=IP ;;
      *) kind=DNS ;;
    esac
    case ",$sans," in
      *",$kind:$name,"*) ;;
      *) sans="$sans,$kind:$name" ;;
    esac
  done
  cat > "$1" <<EOF
basicConstraints=CA:FALSE
keyUsage=digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=$sans
EOF
}

create_ca() {
  openssl req -x509 -newkey rsa:4096 -sha256 -days 3650 -nodes \
    -keyout "$CA_KEY" \
    -out "$CA_CRT" \
    -subj "/CN=$CA_CN" \
    -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
    -addext "keyUsage=critical,keyCertSign,cRLSign"
  chmod 600 "$CA_KEY"
  chmod 644 "$CA_CRT"
  rm -f "$CA_SRL"
}

sign_server() {
  csr=$(mktemp)
  trap 'rm -f "$csr"' EXIT
  openssl req -new -newkey rsa:2048 -sha256 -nodes \
    -keyout "$KEY" \
    -out "$csr" \
    -subj "/CN=localhost"
  openssl x509 -req -sha256 -days 825 \
    -in "$csr" \
    -CA "$CA_CRT" \
    -CAkey "$CA_KEY" \
    -CAserial "$CA_SRL" \
    -CAcreateserial \
    -out "$CRT" \
    -extfile "$EXT"
  chmod 600 "$KEY"
  chmod 644 "$CRT"
  rm -f "$csr"
  trap - EXIT
  echo "Root-CA für den Client: $CA_CRT"
  echo "Serverzertifikat: $CRT"
  openssl x509 -in "$CRT" -noout -ext subjectAltName
}

tmp_ext=$(mktemp)
trap 'rm -f "$tmp_ext"' EXIT
write_server_ext "$tmp_ext"

if [ "$FORCE" -eq 1 ] || [ ! -f "$CA_CRT" ] || [ ! -f "$CA_KEY" ]; then
  create_ca
fi

need_server=0
if [ ! -f "$CRT" ] || [ ! -f "$KEY" ] || [ ! -f "$EXT" ]; then
  need_server=1
elif ! cmp -s "$tmp_ext" "$EXT"; then
  need_server=1
elif ! openssl verify -CAfile "$CA_CRT" "$CRT" >/dev/null 2>&1; then
  need_server=1
elif ! openssl x509 -checkend 2592000 -noout -in "$CRT" >/dev/null 2>&1; then
  need_server=1
fi

if [ "$need_server" -eq 1 ]; then
  mv "$tmp_ext" "$EXT"
  trap - EXIT
  sign_server
else
  rm -f "$tmp_ext"
  trap - EXIT
fi
