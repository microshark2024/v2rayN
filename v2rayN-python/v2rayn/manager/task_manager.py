"""Task manager.

Ported from ServiceLib/Manager/TaskManager.cs.
Manages scheduled tasks (subscription updates, statistics collection, etc.).
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine

from v2rayn.common import logging_config

_tag = "TaskManager"


@dataclass
class ScheduledTask:
    """A scheduled task."""

    name: str = ""
    interval_seconds: int = 3600
    enabled: bool = True
    last_run: float = 0
    callback: Callable[[], Coroutine[Any, Any, None]] | None = None


class TaskManager:
    """Manages periodic scheduled tasks."""

    def __init__(self):
        """Initialize task manager."""
        self._tasks: list[ScheduledTask] = []
        self._running = False

    def add_task(
        self,
        name: str,
        interval_seconds: int,
        callback: Callable[[], Coroutine[Any, Any, None]],
        enabled: bool = True,
    ) -> None:
        """Add a scheduled task.

        Args:
            name: Task name
            interval_seconds: Interval between runs
            callback: Async callback function
            enabled: Whether task is enabled
        """
        task = ScheduledTask(
            name=name,
            interval_seconds=interval_seconds,
            enabled=enabled,
            callback=callback,
        )
        self._tasks.append(task)

    async def start(self) -> None:
        """Start the task scheduler."""
        self._running = True
        while self._running:
            import time

            now = time.time()
            for task in self._tasks:
                if not task.enabled or task.callback is None:
                    continue
                if now - task.last_run >= task.interval_seconds:
                    try:
                        await task.callback()
                        task.last_run = now
                    except Exception as ex:
                        logging_config.save_log_ex(_tag, ex)

            await asyncio.sleep(60)  # Check every minute

    def stop(self) -> None:
        """Stop the task scheduler."""
        self._running = False

    def get_tasks(self) -> list[ScheduledTask]:
        """Get all tasks."""
        return list(self._tasks)
