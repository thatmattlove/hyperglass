FROM python:3.13-alpine AS base
WORKDIR /opt/hyperglass
ENV HYPERGLASS_APP_PATH=/etc/hyperglass
ENV HYPERGLASS_HOST=0.0.0.0
ENV HYPERGLASS_PORT=8001
ENV HYPERGLASS_DEBUG=false
ENV HYPERGLASS_DEV_MODE=false
ENV HYPERGLASS_REDIS_HOST=redis
ENV HYPEGLASS_DISABLE_UI=false
ENV HYPERGLASS_CONTAINER=true
COPY . .

FROM base AS ui
WORKDIR /opt/hyperglass/hyperglass/ui
RUN apk add --no-cache build-base pkgconfig cairo-dev nodejs npm \
    gcc \
    g++ \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    harfbuzz-dev \
    fribidi-dev \
    curl && sleep 2 && npm install -g pnpm && pnpm install -P

FROM ui AS hyperglass
WORKDIR /opt/hyperglass
RUN pip3 install -e .

EXPOSE ${HYPERGLASS_PORT}
CMD ["python3", "-m", "hyperglass.console", "start"]
