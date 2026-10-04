"""
${message}

Write here what this revision adds and why exactly at this place in the chain (docs/standards/standard_database.md).
"""

from alembic import op

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Applies the change of this revision, one raw SQL statement per call."""


def downgrade() -> None:
    """Reverts the change of this revision."""
