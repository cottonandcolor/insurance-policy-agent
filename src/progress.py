"""Live progress output for notebooks and CLI."""

from __future__ import annotations

import sys


def progress(msg: str) -> None:
    """Print immediately; use stderr in notebooks where stdout may buffer."""
    stream = sys.stderr if _in_ipython() else sys.stdout
    stream.write(msg + "\n")
    stream.flush()


def _in_ipython() -> bool:
    try:
        from IPython import get_ipython

        return get_ipython() is not None
    except ImportError:
        return False
