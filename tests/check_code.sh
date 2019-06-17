#!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

check_format() {
  black hyperglass
  git add hyperglass/ *.py
  git commit --message "Black Formatting - travis #$TRAVIS_BUILD_NUMBER"
  echo "Completed Black Formatting"
}

run_pylint() {
  echo $(python3 manage.py pylint-badge --integer-only True)
}

check_pylint() {
  PYLINT_SCORE=$(run_pylint)
  echo "Pylint score: $PYLINT_SCORE"
  if  [ "$PYLINT_SCORE" == "10.00" ]
  then
    git add pylint.svg
    git commit --message "Pylint Badge - travis #$TRAVIS_BUILD_NUMBER"
    echo "Completed Pylint Check & Badge Creation"
  fi
}

check_format
check_pylint
