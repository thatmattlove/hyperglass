#!/usr/bin/env bash

UI_DIR="$(pwd)/hyperglass/ui"

check_typescript () {
    cd $UI_DIR
    node_modules/.bin/tsc
}

check_eslint () {
    cd $UI_DIR
    node_modules/.bin/eslint .
}

check_prettier () {
    cd $UI_DIR
    node_modules/.bin/prettier -c -w .
}

for arg in "$@"
do
    if [ "$arg" == "--typescript" ]
    then
        check_typescript
    else [ "$arg" == "--eslint" ]
        check_eslint
    else [ "$arg" == "--prettier" ]
        check_prettier
    fi
done
