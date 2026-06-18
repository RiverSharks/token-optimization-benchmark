#!/bin/bash
set -e
git checkout -f "$1" 2>/dev/null
claude plugin marketplace add JuliusBrussee/caveman >&2
claude plugin install caveman@caveman >&2
PROMPT="/caveman ultra \n $2"
echo "[caveman] prompt: $PROMPT" >&2
claude -p "$PROMPT" --output-format json --dangerously-skip-permissions
