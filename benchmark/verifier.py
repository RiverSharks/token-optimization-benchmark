from __future__ import annotations

import logging
import subprocess

log = logging.getLogger("benchmark")


def run_verification(script_path: str) -> tuple[bool, str]:
    """Run *script_path* with the current Python interpreter.

    Returns ``(passed, combined_output)`` where *passed* is ``True`` when the
    script exits with code 0.
    """
    proc = subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True,
    )
    log.debug("verify returncode: %d", proc.returncode)
    log.debug("verify stdout:\n%s", proc.stdout)
    if proc.stderr:
        log.debug("verify stderr:\n%s", proc.stderr)

    combined = (proc.stdout + proc.stderr).strip()
    return proc.returncode == 0, combined
