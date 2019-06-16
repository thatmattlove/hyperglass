#!/bin/bash

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

check_format() {
  black hyperglass
  git add hyperglass/ *.py
  git commit --message "Black Formatting - travis #$TRAVIS_BUILD_NUMBER"
}

run_pylint() {
  python3 manage.py pylint-badge --integer-only True
}

check_pylint() {
  PYLINT_SCORE=$(run_pylint)
  if  [ "$PYLINT_SCORE" != "10.00" ];
  then
    git add pylint.svg
    git commit --message "Pylint Badge - travis #$TRAVIS_BUILD_NUMBER"
  fi
}

# upload_files() {
#   git remote add origin-pages https://${GH_TOKEN}@github.com/MVSE-outreach/resources.git > /dev/null 2>&1
#   git push --quiet --set-upstream origin-pages gh-pages
# }

check_format
check_pylint
# setup_git
