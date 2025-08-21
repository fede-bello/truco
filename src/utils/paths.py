from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from schemas.constants import BASE_OUTPUT_DIR

if TYPE_CHECKING:
    from pathlib import Path


def create_new_session_dir(now: datetime | None = None) -> Path:
    """Create and return a new date-time stamped output directory.

    The directory is created under BASE_OUTPUT_DIR using the format
    YYYYmmdd-HHMMSS to ensure lexicographic ordering matches chronology.

    Args:
        now: Optional datetime to use for naming, mainly for testing.

    Returns:
        Path to the newly created session directory.
    """
    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp_source = now or datetime.now(UTC)
    session_name = timestamp_source.strftime("%Y%m%d-%H%M%S")
    session_dir = BASE_OUTPUT_DIR / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    return session_dir


def get_latest_session_dir() -> Path | None:
    """Return the most recent date-time stamped output directory if any.

    Returns:
        The Path to the newest session directory, or None if none exist.
    """
    if not BASE_OUTPUT_DIR.exists():
        return None
    subdirs = [p for p in BASE_OUTPUT_DIR.iterdir() if p.is_dir()]
    if not subdirs:
        return None
    # Directory names are in YYYYmmdd-HHMMSS so lexicographic order works
    subdirs.sort(key=lambda p: p.name)
    return subdirs[-1]
