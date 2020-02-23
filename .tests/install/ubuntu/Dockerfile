FROM ubuntu:bionic as base
WORKDIR /tmp
COPY ./install.sh /tmp/install.sh
RUN apt-get update && apt-get install -y apt-utils \
    && apt-get install -y curl git gnupg build-essential

# FROM base as install
# RUN bash /tmp/install.sh
