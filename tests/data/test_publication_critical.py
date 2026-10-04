"""Verify publication outcomes against real PostgreSQL transactions."""

from uuid import uuid4

import pytest
from sqlalchemy import event, text

from common_time import build_deadline, fetch_monotonic_seconds
from data.locks import apply_import_exclusion
from data.publication import PublicationOutcomeUnknown, PublicationRolledBack, apply_publication

pytestmark = pytest.mark.critical


def fetch_count(owner, token):
    """Observe committed scratch rows through an independent account."""
    with owner.connect() as connection:
        return connection.execute(text("SELECT count(*) FROM public.backend_skeleton_scratch WHERE run_id=:token"), {"token": token}).scalar_one()


def test_publication_commits_atomically(scratch_database, tmp_path):
    """Expose two writes together only after acknowledged commit."""
    owner, service = scratch_database
    token = str(uuid4())

    def apply_write(connection):
        """Write invented values without exposing them before commit."""
        for value in ("ŁÓDŹ", "second"):
            connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, :value)"), {"token": token, "value": value})
            assert fetch_count(owner, token) == 0
        return "done"

    with apply_import_exclusion(service, tmp_path) as lease:
        assert apply_publication(lease, build_deadline(3, fetch_monotonic_seconds()), apply_write).value == "done"
    assert fetch_count(owner, token) == 2


def test_server_timeout_rolls_back_and_releases_after_cleanup(scratch_database, tmp_path):
    """Enforce one shortened transaction budget while confirming invisibility."""
    owner, service = scratch_database
    token = str(uuid4())

    def apply_write(connection):
        """Start durable-looking work then spend the transaction budget."""
        connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, 'invented')"), {"token": token})
        connection.execute(text("SELECT pg_sleep(1)"))

    with apply_import_exclusion(service, tmp_path) as lease, pytest.raises(PublicationRolledBack):
        apply_publication(lease, build_deadline(0.25, fetch_monotonic_seconds()), apply_write)
    assert fetch_count(owner, token) == 0
    with apply_import_exclusion(service, tmp_path):
        assert not any(path.name != "admission.lock" and not path.is_dir() for path in tmp_path.iterdir())


def test_commit_response_loss_is_unknown_even_when_visible(scratch_database, tmp_path):
    """Lose acknowledgement after a real commit and refuse a rollback claim."""
    owner, service = scratch_database
    token = str(uuid4())

    def apply_write(connection):
        """Inject the acknowledgement fault after the driver's real COMMIT."""
        connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, 'invented')"), {"token": token})

        def apply_response_loss(_conn, _cursor, statement, _parameters, context, _executemany):
            """Simulate transport loss only after successful commit execution."""
            if statement == "COMMIT":
                raise ConnectionError("invented transport failure")

        event.listen(connection, "after_cursor_execute", apply_response_loss)

    with apply_import_exclusion(service, tmp_path) as lease, pytest.raises(PublicationOutcomeUnknown):
        apply_publication(lease, build_deadline(3, fetch_monotonic_seconds()), apply_write)
    assert fetch_count(owner, token) == 1


def test_production_120_second_ceiling(scratch_database, tmp_path):
    """Rollback an 80-second wait plus 50-second statement at the shared ceiling."""
    owner, service = scratch_database
    token = str(uuid4())
    started = fetch_monotonic_seconds()

    def apply_write(connection):
        """Attempt the exact acceptance timing with one invented scratch write."""
        connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, 'invented')"), {"token": token})
        connection.execute(text("SELECT pg_sleep(80)"))
        connection.execute(text("SELECT pg_sleep(50)"))

    with apply_import_exclusion(service, tmp_path) as lease, pytest.raises(PublicationRolledBack):
        apply_publication(lease, build_deadline(180, started), apply_write)
    assert 119 <= fetch_monotonic_seconds() - started < 125
    assert fetch_count(owner, token) == 0


def test_repeated_short_statements_share_one_budget(scratch_database, tmp_path):
    """Refuse accumulation even though every statement individually fits."""
    owner, service = scratch_database
    token = str(uuid4())

    def apply_write(connection):
        """Repeat short work without extending the original deadline."""
        connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, 'invented')"), {"token": token})
        for _ in range(10):
            connection.execute(text("SELECT pg_sleep(0.05)"))

    with apply_import_exclusion(service, tmp_path) as lease, pytest.raises(PublicationRolledBack):
        apply_publication(lease, build_deadline(0.2, fetch_monotonic_seconds()), apply_write)
    assert fetch_count(owner, token) == 0


def test_commit_phase_expiration_does_not_claim_confirmed_rollback(scratch_database, tmp_path):
    """Exercise a commit-phase delay rather than a final-write timeout."""
    import time

    owner, service = scratch_database
    token = str(uuid4())

    def apply_write(connection):
        """Delay commit transmission until the server transaction expires."""
        connection.execute(text("INSERT INTO public.backend_skeleton_scratch (run_id, value) VALUES (:token, 'invented')"), {"token": token})

        def apply_commit_delay(_conn, _cursor, statement, _parameters, _context, _executemany):
            """Spend the remaining budget after commit intent is recorded."""
            if statement == "COMMIT":
                time.sleep(0.3)

        event.listen(connection, "before_cursor_execute", apply_commit_delay)

    with apply_import_exclusion(service, tmp_path) as lease, pytest.raises(PublicationOutcomeUnknown):
        apply_publication(lease, build_deadline(0.15, fetch_monotonic_seconds()), apply_write)
    assert fetch_count(owner, token) == 0
