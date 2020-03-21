#!/usr/bin/env bash

function isort_all () {
    isort -y hyperglass/*.py
    if [[ ! $? == 0 ]]; then
      exit 1
    fi
    isort -y hyperglass/**/*.py
    if [[ ! $? == 0 ]]; then
      exit 1
    fi
}

function validate_examples () {
  python3 ./validate_examples.py
  if [[ ! $? == 0 ]]; then 
    exit 1
  fi
}

# isort_all
validate_examples

exit 0