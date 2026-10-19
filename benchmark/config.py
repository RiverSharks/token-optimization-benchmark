from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    id: str
    type: str
    commit_hash: str
    prompt: str
    harness_verify_script: str


@dataclass
class RunConfig:
    num_trials: int = 1
    tools: list[str] = field(default_factory=lambda: ["baseline", "symdex", "caveman", "serena"])
    images: dict[str, str] = field(default_factory=lambda: {
        "baseline": "agent-benchmark-base",
        "symdex":   "agent-benchmark-symdex",
        "caveman":  "agent-benchmark-base",
        "serena":   "agent-benchmark-base",
    })
    results_file: str = "results/benchmark_results.csv"
    model_name: str = "claude-haiku-4-5-20251001"
    task_ids: Optional[list[str]] = None  # None = run all tasks


@dataclass
class TaskResult:
    task_id: str
    tool: str
    trial: int
    in_tok: int
    out_tok: int
    cache_hits: int
    passed: int  # 1 or 0
    error: Optional[str] = None


def load_tasks(path: str) -> list[Task]:
    with open(path) as f:
        raw = json.load(f)
    return [Task(**t) for t in raw]
