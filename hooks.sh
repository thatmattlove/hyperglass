#!/usr/bin/env bash

function make_badge () {
    ./manage.py line-count-badge
    if [[ ! $? == 0 ]]; then
        exit 1
    fi
}

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

make_badge
# isort_all

exit 0