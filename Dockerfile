FROM python:3.12.3-alpine AS base
# UI dependencies
RUN apk add build-base pkgconfig cairo-dev nodejs npm
# Setup rootless image
RUN addgroup -g 1000 hyperglass && adduser -D -u 1000 -G hyperglass hyperglass
RUN mkdir /etc/hyperglass /opt/hyperglass
RUN chown -R hyperglass:hyperglass /etc/hyperglass /opt/hyperglass
USER 1000:1000
WORKDIR /opt/hyperglass
COPY --chown=1000:1000 . .
ENV HYPERGLASS_APP_PATH=/etc/hyperglass
ENV HYPERGLASS_HOST=0.0.0.0
ENV HYPERGLASS_PORT=8001
ENV HYPERGLASS_DEBUG=false
ENV HYPERGLASS_DEV_MODE=false
ENV HYPERGLASS_REDIS_HOST=redis
ENV HYPEGLASS_DISABLE_UI=true
ENV HYPERGLASS_CONTAINER=true

FROM base AS ui
# Set NPM global install path to the home directory so permissions are correct
RUN mkdir ~/.npm-global ~/.npm-store
RUN npm config set prefix "~/.npm-global"
ENV PATH="/home/hyperglass/.npm-global/bin:${PATH}"
WORKDIR /opt/hyperglass/hyperglass/ui
RUN npm install -g pnpm
RUN pnpm install -P

FROM ui AS hyperglass
WORKDIR /opt/hyperglass
RUN pip3 install --user --no-cache-dir -e .

EXPOSE ${HYPERGLASS_PORT}
CMD ["python3", "-m", "hyperglass.console", "start"]
