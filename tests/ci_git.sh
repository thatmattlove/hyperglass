  #!/bin/sh

commit_black() {
  git add hyperglass/ *.py
  git commit --message "Black Formatting - travis $TRAVIS_BUILD_NUMBER"
}

commit_pylint() {
  git add pylint.svg
  git commit --message "Pylint Badge - travis $TRAVIS_BUILD_NUMBER"
}

setup_git() {
  git config --global user.email "travis@travis-ci.org"
  git config --global user.name "Travis CI"
}

setup_git
commit_black
commit_pylint

if [ $? -ne 0 ]; then
  exit 0
