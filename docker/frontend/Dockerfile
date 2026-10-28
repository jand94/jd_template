FROM node:24-bookworm-slim AS deps

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

FROM deps AS dev

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

FROM deps AS build

COPY . .

ARG PROJECT_NAME=jd_template
ARG API_TITLE=jd_template API
ARG API_DESCRIPTION=HTTP-API für jd_template
ARG API_VERSION=0.1.0

ENV PROJECT_NAME=$PROJECT_NAME \
    API_TITLE=$API_TITLE \
    API_DESCRIPTION=$API_DESCRIPTION \
    API_VERSION=$API_VERSION \
    NEXT_TELEMETRY_DISABLED=1

RUN npm run build

FROM node:24-bookworm-slim AS prod

WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1

COPY --from=build /app/package.json /app/package-lock.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
COPY --from=build /app/next.config.ts ./next.config.ts

EXPOSE 3000

CMD ["npm", "start"]
