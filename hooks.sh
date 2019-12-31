#!/usr/bin/env bash

LC=$(./manage.py line-count-badge)

echo $LC

if [[ ! $? == 0 ]]; then
    exit 1
fi
exit 0