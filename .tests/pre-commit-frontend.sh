#!/usr/bin/env bash

UI_DIR="$(pwd)/hyperglass/ui"

check_typescript() {
    yarn --cwd $UI_DIR typecheck
}

check_eslint() {
    yarn --cwd $UI_DIR lint
}

check_prettier() {
    yarn --cwd $UI_DIR prettier -c .
}

for arg in "$@"; do
    if [ "$arg" == "--typescript" ]; then
        check_typescript
        exit $?
    elif [ "$arg" == "--eslint" ]; then
        check_eslint
        exit $?
    elif [ "$arg" == "--prettier" ]; then
        check_prettier
        exit $?
    else
        echo "Arguments --typescript, --eslint, or --prettier required."
        exit 1
    fi
done
