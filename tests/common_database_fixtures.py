"""Shared owner cleanup registration for exact, locally owned fixture objects."""

from collections.abc import Callable
from dataclasses import dataclass, field

from sqlalchemy import Connection, Engine


@dataclass
class DatabaseFixtureRegistry:
    """Runs exact-key cleanup actions with the local schema-owner engine."""

    owner_engine: Engine
    cleanup_actions: list[Callable[[Connection], None]] = field(default_factory=list)

    def apply_registration(self, action: Callable[[Connection], None]) -> None:
        """Registers fixture-specific exact-key cleanup before the exercised write."""
        self.cleanup_actions.append(action)

    def apply_cleanup(self) -> None:
        """Runs reverse-order cleanup in one owner transaction, without broad resets."""
        if self.cleanup_actions:
            with self.owner_engine.begin() as connection:
                for action in reversed(self.cleanup_actions):
                    action(connection)
            self.cleanup_actions.clear()
