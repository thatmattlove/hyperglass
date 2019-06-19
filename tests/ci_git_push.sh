#!/bin/sh
git push $GH_TOKEN@github.com:$TRAVIS_PULL_REQUEST_SLUG.git origin $CURRENT_BRANCH > /dev/null 2>&1
