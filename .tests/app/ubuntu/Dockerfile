FROM ubuntu:bionic as base
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
WORKDIR /tmp
RUN apt-get update \
    && apt-get install -y git curl net-tools \
    && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y python3 python3-pip python3-venv redis-server nodejs yarn \
    #    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 \
    #
    # Pinning Poetry installer to this specific version. As of 2020 07 24, the script from master
    # fails to install due to Python 2's executable matching first. See #2106
    #
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/e70ee3112ab06374dfef4ab84e6dded2382cc7dd/get-poetry.py | python3 \
    && python3 --version \
    && echo "NodeJS $(node --version)" \
    && echo "Yarn $(yarn --version)"
COPY ./ /tmp/hyperglass
ENV PATH=$PATH:/root/.poetry/bin

FROM base as install
WORKDIR /tmp/hyperglass
RUN poetry install --no-ansi

FROM install as setup
WORKDIR /tmp/hyperglass
COPY .tests/app/setup.sh /tmp/setup.sh
RUN ls -lsah /tmp