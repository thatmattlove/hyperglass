#!/bin/bash

install_dependencies() {
  sudo add-apt-repository universe
  sudo apt-get update -q
  sudo apt-get install -y redis
}

install_dependencies()
