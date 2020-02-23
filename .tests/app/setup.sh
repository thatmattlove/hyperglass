#!/bin/sh -l

get_status () {
    echo $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001)
}

echo "[INFO] Starting Redis..."
redis-server &

cd /tmp/hyperglass

echo "[INFO] Starting setup..."
poetry run hyperglass setup -d
echo "[SUCCESS] Setup completed."
sleep 2

echo "[INFO] Starting UI build."
poetry run hyperglass build-ui
echo "[SUCCESS] UI build completed."

echo "[INFO] Starting hyperglass..."
poetry run hyperglass start &> /var/log/hyperglassci.log &
sleep 10

if [[ ! $? == 0 ]]; then
    echo "[ERROR] Failed to start hyperglass."
    exit 1
fi

echo "[SUCCESS] Started hyperglass."
echo "[INFO] Running HTTP test..."
echo "[INFO] Status code: $(get_status)"

if [[ ! $? == 0 ]]; then
    echo "[ERROR] HTTP test failed."
    exit 1
fi

echo "[SUCCESS] Tests ran successfully."
exit 0