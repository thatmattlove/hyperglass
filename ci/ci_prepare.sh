#!/bin/bash

copy_config() {
  rm ../hyperglass/configuration/*.toml
  cp *.toml ../hyperglass/configuration/
}

start_flask() {
  nohup python3 ./ci_dev_server.py &
}

copy_config()
start_flask()
