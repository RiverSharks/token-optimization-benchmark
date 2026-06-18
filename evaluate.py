#!/usr/bin/env python3
"""Token Optimization Benchmark — CLI entry point.

Usage examples
--------------
# Run everything with defaults
python evaluate.py

# Run only the baseline tool, 3 trials
python evaluate.py --tools baseline --trials 3

# Run specific tasks against two tools
python evaluate.py --tasks task_001 --tools baseline symdex

# Custom results file and model
python evaluate.py --results results/my_run.csv --model claude-opus-4-5-20251001
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys

from dotenv import load_dotenv

from benchmark.config import RunConfig, TaskResult, load_tasks
from benchmark.docker_runner import DockerRunner
from benchmark.metrics import parse_token_metrics
from benchmark.results import ResultsWriter
from benchmark.verifier import run_verification

log = logging.getLogger("benchmark")


def setup_logging() -> None:
    os.makedirs("results", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("results/debug.log", mode="w"),
            logging.StreamHandler(),
        ],
    )


def run_matrix(config: RunConfig, tasks_path: str = "tasks.json") -> None:
    all_tasks = load_tasks(tasks_path)
    log.info("Loaded %d task(s) from %s", len(all_tasks), tasks_path)

    tasks = (
        [t for t in all_tasks if t.id in config.task_ids]
        if config.task_ids
        else all_tasks
    )
    if not tasks:
        log.error("No matching tasks found (requested: %s)", config.task_ids)
        sys.exit(1)

    writer = ResultsWriter(config.results_file)

    for task in tasks:
        for tool in config.tools:
            for trial in range(1, config.num_trials + 1):
                label = f"{task.id} | tool={tool} | trial={trial}/{config.num_trials}"
                print(f"Executing: {label}")
                log.info("=== START %s ===", label)

                script_path = f"scripts/{tool}.sh"
                if not os.path.exists(script_path):
                    log.error("Script not found: %s", script_path)
                    continue

                image = config.images.get(tool)
                if not image:
                    log.error("No Docker image configured for tool: %s", tool)
                    continue

                container = f"eval_{task.id}_{tool}_{trial}".lower()

                with DockerRunner(container, image, script_path, task.commit_hash, task.prompt, config.model_name) as runner:
                    proc = runner.run()

                    in_tok, out_tok, c_hit = parse_token_metrics(proc.stdout)

                    shutil.rmtree("./tmp_eval_workspace", ignore_errors=True)
                    runner.copy_workspace("./tmp_eval_workspace")
                    shutil.rmtree("./tmp_claude_projects", ignore_errors=True)
                    runner.copy_claude_projects("./tmp_claude_projects")

                log.info("Running harness verify: %s", task.harness_verify_script)
                passed_bool, verify_output = run_verification(task.harness_verify_script)
                passed = 1 if passed_bool else 0

                if tool == "symdex":
                    mcp_passed, mcp_output = run_verification("hidden_tests/verify_mcp_usage.py")
                    log.info("MCP usage check — passed=%d output=%s", int(mcp_passed), mcp_output)

                log.info(
                    "RESULT %s — in_tok=%d out_tok=%d cache_hits=%d passed=%d",
                    label, in_tok, out_tok, c_hit, passed,
                )

                writer.write(TaskResult(
                    task_id=task.id,
                    tool=tool,
                    trial=trial,
                    in_tok=in_tok,
                    out_tok=out_tok,
                    cache_hits=c_hit,
                    passed=passed,
                ))

    log.info("All runs completed. Results: %s", config.results_file)
    print(f"All runs completed. Results: {config.results_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the token-optimization benchmark matrix.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--trials", type=int, default=1,
        help="Number of trials per task/tool combination.",
    )
    parser.add_argument(
        "--tools", nargs="+", default=["baseline", "symdex", "caveman"],
        metavar="TOOL",
        help="Which tool variants to run.",
    )
    parser.add_argument(
        "--tasks", nargs="+", default=None,
        metavar="TASK_ID",
        help="Task IDs to run (default: all tasks in tasks.json).",
    )
    parser.add_argument(
        "--results", default="results/benchmark_results.csv",
        metavar="PATH",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--model", default="claude-haiku-4-5-20251001",
        metavar="MODEL",
        help="Anthropic model name passed to the container.",
    )
    parser.add_argument(
        "--tasks-file", default="tasks.json",
        metavar="PATH",
        help="Path to the tasks JSON file.",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv(override=True)
    setup_logging()
    log.info("Logger initialised")

    args = parse_args()

    if "ANTHROPIC_API_KEY" not in os.environ:
        log.error("ANTHROPIC_API_KEY is not set. Add it to your .env or export it.")
        sys.exit(1)

    config = RunConfig(
        num_trials=args.trials,
        tools=args.tools,
        results_file=args.results,
        model_name=args.model,
        task_ids=args.tasks,
    )

    run_matrix(config, tasks_path=args.tasks_file)


if __name__ == "__main__":
    main()
