#!/bin/bash

install_dependencies() {
  add-apt-repository universe
  apt-get update -q
  apt-get install -y redis
}

install_dependencies()
