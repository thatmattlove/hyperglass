#!/bin/sh

echo "Travis Pull Request: $TRAVIS_PULL_REQUEST"
echo "Travis Branch: $TRAVIS_BRANCH"

git_setup() {
  git config user.email "travis@travis-ci.org"
  git config user.name "Travis CI"
}

detect_branch() {
  if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    echo $TRAVIS_BRANCH
  else
    echo $TRAVIS_PULL_REQUEST_BRANCH
  fi
}

export CURRENT_BRANCH=$(detect_branch)
echo "Detected Branch: $CURRENT_BRANCH"

echo "Setting git config parameters..."
git_setup
echo "Initiating git fetch..."
git fetch --depth=1 $GH_TOKEN@github.com:$TRAVIS_PULL_REQUEST_SLUG.git refs/heads/$CURRENT_BRANCH:refs/remotes/origin/$CURRENT_BRANCH > /dev/null 2>&1
echo "Running git checkout..."
git checkout origin/$CURRENT_BRANCH
