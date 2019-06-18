#!/bin/sh
echo "Travis thinks the branch is $TRAVIS_BRANCH"
git config --global user.email "travis@travis-ci.org"
git config --global user.name "Travis CI"
git checkout $TRAVIS_BRANCH
exit 0


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

git_setup
git checkout $CURRENT_BRANCH
export $CURRENT_BRANCH
exit 0
