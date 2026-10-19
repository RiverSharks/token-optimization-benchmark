from __future__ import annotations

import csv
import os

from benchmark.config import TaskResult

_HEADER = [
    "Task_ID", "Tool", "Trial",
    "Input_Tokens", "Output_Tokens", "Cache_Hits", "Verification_Passed",
    "MCP_Passed", "Duration_S",
]


class ResultsWriter:
    """Opens *path* for writing, writes the CSV header, then appends rows."""

    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.path = path
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(_HEADER)

    def write(self, result: TaskResult) -> None:
        with open(self.path, "a", newline="") as f:
            csv.writer(f).writerow([
                result.task_id,
                result.tool,
                result.trial,
                result.in_tok,
                result.out_tok,
                result.cache_hits,
                result.passed,
                round(result.duration_s, 2),
                "" if result.mcp_passed is None else result.mcp_passed,
            ])
