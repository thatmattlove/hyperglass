ARG HYPERGLASS_PATH=/opt/hyperglass
FROM python:3 AS base

# TODO nodejs and yarn are required during "build-ui", but also at runtime (in "start")
#      To my understanding the runtime requirement should be removed, because it should only be used in "build-ui"
#      Once fixed, this RUN can be moved to the builder stage instead
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
 && curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null \
 && echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list \
 && apt update \
 && apt install -y nodejs yarn \
 && rm -rf /var/lib/apt/lists/*

FROM base AS builder
ARG HYPERGLASS_PATH

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
RUN mkdir -p /usr/local/src/hyperglass ${HYPERGLASS_PATH}
# TODO Only COPY the files that are required for the build
#      Keep .dockerignore in mind too
COPY . /usr/local/src/hyperglass
WORKDIR /usr/local/src/hyperglass
RUN /root/.poetry/bin/poetry build
RUN cd ./dist/ && pip install hyperglass*.whl
RUN hyperglass setup
# TODO "build-ui" needs a devices.yaml.
#      The "build-ui" requirement for devices.yaml should be removed, because to my understanding it's only needed in "start"
#      Once fixed, this COPY can be moved to the app stage instead
COPY ./hyperglass/examples/devices.yaml ${HYPERGLASS_PATH}
RUN hyperglass build-ui

FROM base AS app
ARG HYPERGLASS_PATH

COPY --from=builder /usr/local/src/hyperglass/dist/ /tmp/build
RUN cd /tmp/build/ && pip install hyperglass*.whl
RUN useradd -s /usr/sbin/nologin hyperglass
COPY --from=builder --chown=hyperglass:hyperglass ${HYPERGLASS_PATH} ${HYPERGLASS_PATH}
COPY --chown=hyperglass:hyperglass ./hyperglass/examples/hyperglass.docker.yaml ${HYPERGLASS_PATH}/hyperglass.yaml
# TODO Log to stderr by default instead of to /tmp/hyperglass.log
#      RUN ln -sf /dev/stderr /tmp/hyperglass.log
#      ^ Won't work because stderr isn't seekable

# TODO hyperglass needs to run as root, i.e. because
#      "EACCES: permission denied, mkdir '/usr/local/lib/python3.9/site-packages/hyperglass/ui/node_modules'"
#      This is undesired, uncomment the next line once fixed
# USER hyperglass

ENV HYPERGLASS_PATH ${HYPERGLASS_PATH}

EXPOSE 8001
CMD ["hyperglass", "start"]
