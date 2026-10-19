#!/bin/bash
set -e
git checkout -f "$1" 2>/dev/null

# Pack the whole repository into a single file and hand it to the agent up
# front, so no exploration round-trips are needed.
repomix --style xml --output repomix-output.xml >&2

PROMPT="Here is the full repository packed as XML:

$(cat repomix-output.xml)

Task: $2"
echo "[repomix] packed $(wc -c < repomix-output.xml) bytes into the prompt" >&2
claude -p "$PROMPT" --output-format json --dangerously-skip-permissions
