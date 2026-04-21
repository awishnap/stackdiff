"""watcher.py — periodic config drift detection with configurable polling.

Runs diff_configs on a schedule and triggers notifications when drift is
detected. Designed to be invoked from the CLI or as a background process.
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Optional

from stackdiff.differ import diff_configs, has_diff, DiffResult
from stackdiff.notifier import NotifyConfig, notify_all
from stackdiff.auditor import record_event

logger = logging.getLogger(__name__)


class WatcherError(Exception):
    """Raised when the watcher encounters a fatal configuration or runtime error."""


@dataclass
class WatchConfig:
    """Parameters that control a single watch session.

    Attributes:
        name:           Human-readable label for this watch (used in audit logs).
        interval:       Polling interval in seconds.
        max_cycles:     Stop after this many cycles (0 = run forever).
        notify:         Optional notification settings; skipped when None.
        on_drift:       Optional callback invoked with the DiffResult on each
                        cycle that detects drift.
        on_clear:       Optional callback invoked when a previously drifted
                        config returns to parity.
    """

    name: str
    interval: float = 60.0
    max_cycles: int = 0
    notify: Optional[NotifyConfig] = None
    on_drift: Optional[Callable[[DiffResult], None]] = None
    on_clear: Optional[Callable[[DiffResult], None]] = None


@dataclass
class WatchState:
    """Mutable runtime state for an active watch session."""

    cycles: int = 0
    drift_cycles: int = 0
    last_result: Optional[DiffResult] = None
    previously_drifted: bool = False
    errors: list[str] = field(default_factory=list)


def _run_cycle(
    loader_a: Callable[[], dict],
    loader_b: Callable[[], dict],
    cfg: WatchConfig,
    state: WatchState,
) -> None:
    """Execute one polling cycle: load configs, diff, notify, callback."""
    try:
        config_a = loader_a()
        config_b = loader_b()
    except Exception as exc:  # noqa: BLE001
        msg = f"[{cfg.name}] failed to load configs: {exc}"
        logger.error(msg)
        state.errors.append(msg)
        return

    result = diff_configs(config_a, config_b)
    state.last_result = result
    drifted = has_diff(result)

    record_event(
        "watch_cycle",
        {
            "name": cfg.name,
            "cycle": state.cycles,
            "drifted": drifted,
            "added": len(result.added),
            "removed": len(result.removed),
            "changed": len(result.changed),
        },
    )

    if drifted:
        state.drift_cycles += 1
        logger.warning("[%s] drift detected on cycle %d", cfg.name, state.cycles)
        if cfg.notify:
            try:
                notify_all(cfg.notify, result)
            except Exception as exc:  # noqa: BLE001
                logger.error("[%s] notification failed: %s", cfg.name, exc)
        if cfg.on_drift:
            cfg.on_drift(result)
        state.previously_drifted = True
    else:
        if state.previously_drifted:
            logger.info("[%s] drift cleared on cycle %d", cfg.name, state.cycles)
            if cfg.on_clear:
                cfg.on_clear(result)
        state.previously_drifted = False


def watch(
    loader_a: Callable[[], dict],
    loader_b: Callable[[], dict],
    cfg: WatchConfig,
    *,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> WatchState:
    """Block and poll until *max_cycles* is reached (or forever if 0).

    Args:
        loader_a:   Zero-argument callable that returns the *baseline* config dict.
        loader_b:   Zero-argument callable that returns the *target* config dict.
        cfg:        Watch configuration (interval, notifications, callbacks …).
        sleep_fn:   Injectable sleep function (override in tests to avoid blocking).

    Returns:
        The final :class:`WatchState` after all cycles complete.
    """
    if cfg.interval <= 0:
        raise WatcherError("interval must be a positive number of seconds")

    state = WatchState()
    logger.info(
        "[%s] starting watcher — interval=%.1fs max_cycles=%d",
        cfg.name,
        cfg.interval,
        cfg.max_cycles,
    )

    while True:
        state.cycles += 1
        _run_cycle(loader_a, loader_b, cfg, state)

        if cfg.max_cycles and state.cycles >= cfg.max_cycles:
            logger.info("[%s] reached max_cycles=%d, stopping", cfg.name, cfg.max_cycles)
            break

        sleep_fn(cfg.interval)

    return state
