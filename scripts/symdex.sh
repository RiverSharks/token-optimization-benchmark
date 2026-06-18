#!/bin/bash
set -e
git checkout -f "$1" 2>/dev/null
npx skills add https://github.com/husnainpk/SymDex --skill symdex-code-search --yes >&2
symdex index . --repo workspace >&2
symdex serve --port 8989 2>&1 | grep -v 'HTTP' >&2 &
sleep 3
claude mcp add --transport http symdex http://localhost:8989/mcp >&2
PROMPT="Use mcp__symdex__* tools to explore the codebase (repo path: workspace). $2"
echo "[symdex] prompt: $PROMPT" >&2
claude -p "$PROMPT" --output-format json --dangerously-skip-permissions
