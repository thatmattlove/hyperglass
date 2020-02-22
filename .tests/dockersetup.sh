#!/bin/sh -l
cd /tmp/hyperglass
echo "Starting setup..."
poetry run hyperglass setup -d
echo "Setup completed"
sleep 2
echo "Starting UI build"
poetry run hyperglass build-ui
echo "UI build completed"
echo "Starting hyperglass..."
poetry run hyperglass start &> /var/log/hyperglassci.log &
echo "Started hyperglass"
echo "Running HTTP test..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:8001
echo "Tests ran successfully"
exit 0