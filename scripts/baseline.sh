#!/bin/bash
set -e
git checkout -f "$1" 2>/dev/null
claude -p "$2" --output-format json --dangerously-skip-permissions
