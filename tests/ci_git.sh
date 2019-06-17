  #!/bin/sh

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
  git add hyperglass/ *.py
  git commit --message "Black Formatting - travis $TRAVIS_BUILD_NUMBER"
  git add pylint.svg
  git commit --message "Pylint Badge - travis $TRAVIS_BUILD_NUMBER"
}

setup_git
