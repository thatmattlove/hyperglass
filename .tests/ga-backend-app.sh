#!/usr/bin/env bash

LOG_FILE="$HOME/hyperglass-ci.log"
touch /tmp/hyperglass.log

. .venv/bin/activate

echo "[INFO] Starting setup..."
python3 -m hyperglass.console setup -d &>$LOG_FILE
echo "[SUCCESS] Setup completed."
sleep 2

echo "[INFO] Copying directives.yaml file..."
cp ./.tests/directives.yaml $HOME/hyperglass/directives.yaml

echo "[INFO] Copying devices.yaml file..."
cp ./.tests/devices.yaml $HOME/hyperglass/devices.yaml

echo "[INFO] Starting UI build."
python3 -m hyperglass.console build-ui &>$LOG_FILE

if [[ ! $? == 0 ]]; then
    echo "[ERROR] Failed to build hyperglass ui."
    cat /tmp/hyperglass.log
    cat $LOG_FILE
    exit 1
else
    echo "[SUCCESS] UI build completed."
fi

echo "[INFO] Starting hyperglass..."
python3 -m hyperglass.console start &>$LOG_FILE &
sleep 120

if [[ ! $? == 0 ]]; then
    echo "[ERROR] Failed to start hyperglass."
    cat /tmp/hyperglass.log
    cat $LOG_FILE
    exit 1
else
    echo "[SUCCESS] Started hyperglass."
fi

echo "[INFO] Running HTTP test..."

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001)

echo "[INFO] Status code: $STATUS"

if [[ ! $? == 0 ]]; then
    echo "[ERROR] HTTP test failed."
    exit 1
elif [[ ! "$STATUS" == "200" ]]; then
    echo "[ERROR] HTTP test failed."
    cat /tmp/hyperglass.log
    cat $LOG_FILE
    exit 1
fi

echo "[SUCCESS] Tests ran successfully."
exit 0
