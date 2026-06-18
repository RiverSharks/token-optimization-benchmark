from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path

log = logging.getLogger("benchmark")


class DockerRunner:
    """Context manager that runs a task container and cleans up on exit."""

    def __init__(
        self,
        container: str,
        image: str,
        script_path: str,
        commit_hash: str,
        prompt: str,
        model_name: str,
    ) -> None:
        self.container = container
        self.image = image
        self.script_path = os.path.abspath(script_path)
        self.commit_hash = commit_hash
        self.prompt = prompt
        self.model_name = model_name

    def __enter__(self) -> "DockerRunner":
        # Remove any leftover container with this name.
        subprocess.run(
            ["docker", "rm", "-f", self.container],
            capture_output=True,
        )
        log.debug("Pre-run rm of %s (if existed)", self.container)
        return self

    def __exit__(self, *_) -> None:
        rm = subprocess.run(
            ["docker", "rm", "-f", self.container],
            capture_output=True,
        )
        log.debug("docker rm returncode: %d", rm.returncode)

    def run(self) -> subprocess.CompletedProcess:
        """Start the container and wait for it to finish."""
        args = [
            "docker", "run", "--name", self.container,
            # Pass the env var name only — Docker forwards the value from the
            # host environment so the key never appears in the process table or
            # in log output.
            "-e", "ANTHROPIC_API_KEY",
            "-e", f"ANTHROPIC_MODEL={self.model_name}",
            "-v", f"{self.script_path}:/run_task.sh",
            self.image, "/run_task.sh", self.commit_hash, self.prompt,
        ]
        log.debug("docker run args: %s", args)
        proc = subprocess.run(args, capture_output=True, text=True)
        log.debug("docker returncode: %d", proc.returncode)
        log.debug("docker stdout:\n%s", proc.stdout)
        if proc.stderr:
            log.debug("docker stderr:\n%s", proc.stderr)
        return proc

    def copy_workspace(self, dest: str) -> None:
        """Copy /workspace out of the container to *dest* on the host."""
        cp = subprocess.run(
            ["docker", "cp", f"{self.container}:/workspace", dest],
            capture_output=True,
        )
        log.debug("docker cp returncode: %d", cp.returncode)
        if cp.stderr:
            log.debug("docker cp stderr:\n%s", cp.stderr.decode(errors="replace"))

    def copy_claude_projects(self, dest: str) -> None:
        """Copy ~/.claude/projects/ out of the container to *dest* on the host."""
        cp = subprocess.run(
            ["docker", "cp", f"{self.container}:/home/appuser/.claude/projects", dest],
            capture_output=True,
        )
        log.debug("docker cp claude projects returncode: %d", cp.returncode)
        if cp.stderr:
            log.debug("docker cp claude projects stderr:\n%s", cp.stderr.decode(errors="replace"))
