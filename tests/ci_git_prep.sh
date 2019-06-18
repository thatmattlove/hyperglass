#!/bin/sh

THIS_BRANCH=0

git_setup() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

set_branch() {
  if [ "$TRAVIS_PULL_REQUEST" = "true" ]; then
    THIS_BRANCH=$TRAVIS_PULL_REQUEST_BRANCH
  else
    THIS_BRANCH='master'
  fi
}

git_setup
git fetch
set_branch
git checkout $THIS_BRANCH
exit 0
