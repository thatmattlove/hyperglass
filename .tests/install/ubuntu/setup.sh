#!/usr/bin/env bash

echo "[INFO] Disabling multiverse repos..."
sed -i -e '/multiverse/s/^#*/#\ /g' /etc/apt/sources.list
cat /etc/apt/sources.list

echo "[INFO] Updating package repos..."
apt-get update &> /dev/null

echo "[INFO] Installing apt-utils..."
apt-get install -y apt-utils > /dev/null

echo "[INFO] Installing base dependencies..."
apt-get install -y curl git gnupg dialog build-essential > /dev/null

echo '[SUCCESS] Completed build'
exit 0