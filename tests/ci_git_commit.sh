#!/bin/sh

commit_black() {
  git add hyperglass/*.py
  git commit --message "Black Formatting - travis $TRAVIS_BUILD_NUMBER"
}

commit_pylint() {
  git add pylint.svg
  git commit --message "Pylint Badge - travis $TRAVIS_BUILD_NUMBER"
}

commit_black
commit_pylint

exit 0
