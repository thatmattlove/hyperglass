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
  python3 ./tests/validate_examples.py
  if [[! $? == 0]]; then 
    exit 1
  fi
}

# make_badge
# isort_all

exit 0