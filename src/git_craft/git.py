"""Small, checked wrappers around the Git commands used by Git Craft."""

import subprocess
from typing import Sequence


class Git:
    """Run Git commands and expose their output to the application."""

    def _run(self, args: Sequence[str]) -> str:
        """Run a Git command, returning stdout or raising on failure."""
        try:
            result = subprocess.run(
                ["git", *args], capture_output=True, text=True, check=True
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Git is not installed or not on PATH.") from exc
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip() or f"git {' '.join(args)} failed"
            raise RuntimeError(detail) from exc
        return result.stdout.strip()

    def status(self) -> str:
        """Return the working tree status in porcelain format."""
        return self._run(["status", "--porcelain"])

    def get_diff(self) -> str:
        """Return changes staged for commit, or unstaged changes if none are staged."""
        staged = self._run(["diff", "--cached"])
        return staged if staged else self._run(["diff"])

    def get_log(self, n: int = 5) -> str:
        """Return the subjects of the most recent ``n`` commits."""
        return self._run(["log", f"-n{n}", "--format=%s"])
