#!/bin/bash

git_commit() {
  git remote add origin https://${GH_TOKEN}@github.com/checktheroads/hyperglass.git > /dev/null 2>&1
  git push --quiet --set-upstream origin master
}

git_commit
