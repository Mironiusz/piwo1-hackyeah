"""${message}."""
from alembic import op
${imports if imports else ""}

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Apply the explicitly authored revision."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Reverse the explicitly authored revision."""
    ${downgrades if downgrades else "pass"}
