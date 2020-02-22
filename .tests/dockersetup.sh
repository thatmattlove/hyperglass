#!/bin/sh -l
cd /tmp/hyperglass
echo "Starting setup..."
poetry run hyperglass setup -d
echo "Setup completed"
sleep 2
echo "Starting UI build"
poetry run hyperglass build-ui
echo "UI build completed"
# echo "Starting redis..."
# redis-server &
# echo "Redis started"
echo ""
