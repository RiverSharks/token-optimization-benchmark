from __future__ import annotations

import json
import logging

log = logging.getLogger("benchmark")


def parse_token_metrics(stdout: str) -> tuple[int, int, int]:
    """Return (input_tokens, output_tokens, cache_read_input_tokens).

    The container writes JSON objects to stdout (one per line or in stdout).
    Extracts the first JSON object found. Falls back to (0, 0, 0) on any parse error.
    """
    try:
        # Try to parse each line as JSON to handle mixed output (git status + JSON)
        for line in stdout.strip().split('\n'):
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
            try:
                data = json.loads(line)
                if isinstance(data, dict) and "usage" in data:
                    usage = data.get("usage", {})
                    return (
                        usage.get("input_tokens", 0),
                        usage.get("output_tokens", 0),
                        usage.get("cache_read_input_tokens", 0),
                    )
            except json.JSONDecodeError:
                continue
        
        # Fallback: try parsing entire stdout as single JSON
        data = json.loads(stdout.strip())
        usage = data.get("usage", {})
        return (
            usage.get("input_tokens", 0),
            usage.get("output_tokens", 0),
            usage.get("cache_read_input_tokens", 0),
        )
    except (json.JSONDecodeError, AttributeError, ValueError) as exc:
        log.warning("Failed to parse token metrics: %s", exc)
        return 0, 0, 0
