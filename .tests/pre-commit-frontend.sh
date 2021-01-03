#!/usr/bin/env bash

UI_DIR="./hyperglass/ui"

cd $UI_DIR
node_modules/.bin/tsc

# if git diff --cached --name-only | grep --quiet $UI_DIR
# then
#     cd $UI_DIR
#     node_modules/.bin/tsc
# else
#     echo "No frontend files have changed, skipping pre-commit check..."
#     exit 0
# fi
