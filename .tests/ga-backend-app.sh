#!/usr/bin/env bash

LOG_FILE="$HOME/hyperglass-ci.log"

export POETRY_HYPERGLASS_UI_BUILD_TIMEOUT="600"
echo "[INFO] Set build timeout to $POETRY_HYPERGLASS_UI_BUILD_TIMEOUT seconds"

echo "[INFO] Starting setup..."
poetry run hyperglass setup -d &> $LOG_FILE
echo "[SUCCESS] Setup completed."
sleep 2

echo "[INFO] Copying devices.yaml file..."
cp ./hyperglass/examples/devices.yaml $HOME/hyperglass/devices.yaml

echo "[INFO] Setting listen_address..."
echo "listen_address: 127.0.0.1" >> $HOME/hyperglass/hyperglass.yaml

echo "[INFO] Starting UI build."
poetry run hyperglass build-ui &> $LOG_FILE

if [[ ! $? == 0 ]]; then
    echo "[ERROR] Failed to build hyperglass ui."
    cat /tmp/hyperglass.log
    exit 1
else
    echo "[SUCCESS] UI build completed."
fi

echo "[INFO] Starting hyperglass..."
poetry run hyperglass start &> $LOG_FILE &
sleep 120

if [[ ! $? == 0 ]]; then
    echo "[ERROR] Failed to start hyperglass."
    cat /tmp/hyperglass.log
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
    cat $LOG_FILE
    exit 1
fi

echo "[SUCCESS] Tests ran successfully."
exit 0
