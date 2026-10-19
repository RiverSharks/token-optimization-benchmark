#!/bin/bash
set -e
git checkout -f "$1" 2>/dev/null

# Serena exposes its semantic code tools over an SSE MCP endpoint.
uvx --from git+https://github.com/oraios/serena serena start-mcp-server \
    --transport sse --port 9121 --project /workspace >&2 &
sleep 2

claude mcp add --transport sse serena http://localhost:9191/sse >&2

PROMPT="Use mcp__serena__* tools (find_symbol, get_symbols_overview, search_for_pattern) to explore the codebase before editing. $2"
echo "[serena] prompt: $PROMPT" >&2
claude -p "$PROMPT" --output-format json --dangerously-skip-permissions
