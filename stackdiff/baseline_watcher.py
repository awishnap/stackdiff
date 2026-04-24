"""Watch a config file and alert when it drifts from a saved baseline."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from stackdiff.baseline import BaselineError, compare_to_baseline
from stackdiff.config_loader import ConfigLoadError, load_config
from stackdiff.differ import DiffResult, has_diff


class BaselineWatcherError(Exception):
    """Raised when the baseline watcher encounters a fatal error."""


@dataclass
class WatchBaselineConfig:
    baseline_name: str
    config_file: str
    baseline_dir: str
    interval: float = 30.0
    max_cycles: Optional[int] = None
    on_drift: Callable[[DiffResult], None] = field(
        default_factory=lambda: lambda r: None
    )
    on_error: Callable[[Exception], None] = field(
        default_factory=lambda: lambda e: None
    )


def _run_baseline_cycle(
    cfg: WatchBaselineConfig,
) -> Optional[DiffResult]:
    """Load config and compare to baseline; return DiffResult or None on error."""
    try:
        current: Dict[str, str] = load_config(cfg.config_file)
        result = compare_to_baseline(cfg.baseline_name, current, cfg.baseline_dir)
        return result
    except (ConfigLoadError, BaselineError) as exc:
        cfg.on_error(exc)
        return None


def watch_baseline(cfg: WatchBaselineConfig) -> None:
    """Poll *config_file* at *interval* seconds and call *on_drift* when drift is detected.

    Stops after *max_cycles* iterations when set (useful for testing).
    """
    cycles = 0
    while True:
        result = _run_baseline_cycle(cfg)
        if result is not None and has_diff(result):
            cfg.on_drift(result)

        cycles += 1
        if cfg.max_cycles is not None and cycles >= cfg.max_cycles:
            break
        time.sleep(cfg.interval)
