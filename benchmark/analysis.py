"""Post-run summary of a benchmark CSV.

Reads the results written by :class:`benchmark.results.ResultsWriter` and
prints a per-tool table: token totals, pass rate, and mean wall time.
"""
from __future__ import annotations

import csv
import logging
import statistics
from dataclasses import dataclass

log = logging.getLogger("benchmark")


@dataclass
class ToolSummary:
    tool: str
    runs: int
    total_tokens: int
    mean_tokens: float
    pass_rate: float
    mean_duration_s: float
    mcp_pass_rate: float


def _rows(path: str) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def summarize(path: str) -> list[ToolSummary]:
    rows = _rows(path)
    tools = sorted({r["Tool"] for r in rows})

    summaries = []
    for tool in tools:
        mine = [r for r in rows if r["Tool"] == tool]

        # Every token the run was billed for, cache reads included.
        totals = [
            int(r["Input_Tokens"]) + int(r["Output_Tokens"]) + int(r["Cache_Hits"])
            for r in mine
        ]
        passes = [int(r["Verification_Passed"]) for r in mine]
        durations = [float(r["Duration_S"]) for r in mine]
        mcp = [int(r["MCP_Passed"]) for r in mine if r["MCP_Passed"] != ""]

        summaries.append(ToolSummary(
            tool=tool,
            runs=len(mine),
            total_tokens=sum(totals),
            mean_tokens=statistics.mean(totals),
            pass_rate=sum(passes) / len(rows),
            mean_duration_s=statistics.mean(durations),
            mcp_pass_rate=statistics.mean(mcp) if mcp else 0.0,
        ))
    return summaries


def print_summary(path: str) -> None:
    summaries = summarize(path)

    header = f"{'Tool':<10} {'Runs':>5} {'Total tok':>12} {'Mean tok':>11} {'Pass':>6} {'MCP':>6} {'Mean s':>8}"
    print()
    print(header)
    print("-" * len(header))
    for s in summaries:
        print(
            f"{s.tool:<10} {s.runs:>5} {s.total_tokens:>12,} {s.mean_tokens:>11,.0f} "
            f"{s.pass_rate:>5.0%} {s.mcp_pass_rate:>5.0%} {s.mean_duration_s:>8.1f}"
        )

    best = min(summaries, key=lambda s: s.mean_tokens)
    print(f"\nMost token-efficient tool: {best.tool} ({best.mean_tokens:,.0f} tokens/run)")
