"""Verify the delivered image offers extensions without activating product schema."""

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.critical


def test_image_offers_the_pinned_extension_files(scratch_database):
    """Require the packages supplied by the actual project database image."""
    _owner, service = scratch_database
    with service.connect() as connection:
        versions = dict(connection.execute(text("SELECT name, default_version FROM pg_available_extensions WHERE name IN ('postgis', 'pgrouting')")).tuples())
    assert versions == {"postgis": "3.6.4", "pgrouting": "4.0.1"}


def test_image_uses_utf8_and_byte_comparison(scratch_database):
    """Read the database's encoding and observe the agreed sorting behavior."""
    _owner, service = scratch_database
    with service.connect() as connection:
        assert connection.execute(text("SHOW server_encoding")).scalar_one() == "UTF8"
        ordered = list(connection.execute(text("SELECT value FROM (VALUES ('ą'), ('Z'), ('a')) AS scratch(value) ORDER BY value")).scalars())
        assert ordered == ["Z", "a", "ą"]
