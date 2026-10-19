#!/bin/bash
set -e
git checkout "$1" 2>/dev/null

# probe is a ripgrep-backed code search engine with an MCP front end.
claude mcp add --transport stdio probe -- npx -y @buger/probe-mcp >&2

PROMPT="Use the mcp__probe__* tools (search_code, query_code, extract_code) to locate relevant code before editing. $2"
echo "[probe] prompt: $PROMPT" >&2
claude -p "$PROMPT" --output-format json --dangerously-skip-permissions
