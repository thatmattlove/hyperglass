FROM python:3.12.3-alpine AS tools
RUN apk add build-base pkgconfig cairo-dev nodejs npm
RUN npm install -g pnpm

FROM tools AS base
ENV HYPERGLASS_APP_PATH=/etc/hyperglass \
    HYPERGLASS_HOST=0.0.0.0 \
    HYPERGLASS_PORT=8001 \
    HYPERGLASS_DEBUG=false \
    HYPERGLASS_DEV_MODE=false \
    HYPERGLASS_REDIS_HOST=redis \
    HYPEGLASS_DISABLE_UI=true \
    HYPERGLASS_CONTAINER=true

FROM base AS deps
# JS Dependencies for UI
WORKDIR /opt/hyperglass/hyperglass/ui
COPY hyperglass/ui/package.json .
COPY hyperglass/ui/pnpm-lock.yaml .
RUN pnpm install -P

# Python Dependencies for Backend
WORKDIR /opt/hyperglass
COPY README.md .
COPY pyproject.toml .
RUN pip install -e .

FROM deps AS hyperglass
COPY . .
EXPOSE ${HYPERGLASS_PORT}
CMD ["python3", "-m", "hyperglass.console", "start"]
