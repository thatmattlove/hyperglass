FROM ubuntu:bionic as base
WORKDIR /tmp
COPY .tests/install/ubuntu/setup.sh /tmp/init.sh
COPY ./install.sh /tmp/install.sh
RUN bash /tmp/init.sh