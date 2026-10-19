import sys
import json
from pathlib import Path


def run_validation(prefix: str = "symdex"):
    projects_dir = Path("./tmp_claude_projects")
    jsonl_files = list(projects_dir.rglob("*.jsonl"))

    if not jsonl_files:
        print("FAILURE: No JSONL session files found in tmp_claude_projects/")
        sys.exit(1)

    mcp_calls = []
    for path in jsonl_files:
        try:
            with open(path) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        # Check if this entry has a message with content
                        message = entry.get("message", {})
                        if not isinstance(message, dict):
                            continue
                        
                        content = message.get("content", [])
                        # Content must be a list to process tool blocks
                        if not isinstance(content, list):
                            continue
                        
                        # Look for tool_use blocks with symdex in the name
                        for block in content:
                            if isinstance(block, dict):
                                if block.get("type") == "tool_use" and prefix in block.get("name", ""):
                                    mcp_calls.append(block["name"])
                    except (json.JSONDecodeError, TypeError, AttributeError) as e:
                        # Skip malformed lines but don't stop processing
                        continue
        except Exception as e:
            print(f"ERROR reading {path}: {e}", file=sys.stderr)
            pass

    if not mcp_calls:
        print(f"FAILURE: No mcp__{prefix}__* tools were called during the session")
        sys.exit(1)

    print(f"SUCCESS: {prefix} MCP tools used: {mcp_calls}")
    sys.exit(0)


if __name__ == "__main__":
    # Optional argv[1] selects which MCP server's tool calls to look for.
    run_validation(sys.argv[1] if len(sys.argv) > 1 else "symdex")
