#!/bin/sh

echo "Travis Pull Request State: $TRAVIS_PULL_REQUEST"
echo "Travis Branch: $TRAVIS_BRANCH"

git_setup() {
  git config user.email "travis@travis-ci.org"
  git config user.name "Travis CI"
}

detect_branch() {
  if [ "$TRAVIS_PULL_REQUEST" = "true" ]; then
    echo $TRAVIS_PULL_REQUEST_BRANCH
  else
    echo $TRAVIS_BRANCH
  fi
}

CURRENT_BRANCH=$(detect_branch)

echo "Detected Branch: $CURRENT_BRANCH"

git_setup
git checkout $CURRENT_BRANCH
export $CURRENT_BRANCH
exit 0
