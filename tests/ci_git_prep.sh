#!/bin/sh

git config --global user.email "travis@travis-ci.org"
git config --global user.name "Travis CI"
git fetch
git checkout $TRAVIS_BRANCH
exit 0
