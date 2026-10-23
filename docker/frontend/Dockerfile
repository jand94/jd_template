FROM node:24-bookworm-slim

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

RUN printf '%s\n' \
    '#!/bin/sh' \
    'set -e' \
    'if [ ! -x node_modules/.bin/next ]; then npm ci; fi' \
    'exec npm run dev -- --hostname 0.0.0.0 --port 3000' \
    > /usr/local/bin/dev-entrypoint.sh \
    && chmod +x /usr/local/bin/dev-entrypoint.sh

EXPOSE 3000

ENTRYPOINT ["/usr/local/bin/dev-entrypoint.sh"]
