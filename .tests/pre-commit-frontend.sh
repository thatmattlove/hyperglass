#!/usr/bin/env bash

UI_DIR="$(pwd)/hyperglass/ui"

check_typescript () {
    cd $UI_DIR
    node_modules/.bin/tsc --noEmit
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
        exit 0
    elif [ "$arg" == "--eslint" ]
    then
        check_eslint
        exit 0
    elif [ "$arg" == "--prettier" ]
    then
        check_prettier
        exit 0
    else
        echo "Arguments --typescript, --eslint, or --prettier required."
        exit 1
    fi
done
