"""
Shared writes of the critical tests: the statements that store test rows and the made-up keys and hashes they use.

Every hash here is computed from a made-up text, never from a real address, because the hash of a vote without an
account is pseudonymized personal data (`docs/product/specification.md`, M9).
"""

import hashlib

INSERT_USER_REPORT_SQL = """
INSERT INTO fact (fact_type, source, geog, geozone_radius_m, is_sample, idempotency_key, is_removed_from_osm, created_at, created_at_utc_offset_minutes)
VALUES (:fact_type, 'user_report', ST_GeogFromText('SRID=4326;POINT(19.9370 50.0614)'), :geozone_radius_m, false, :idempotency_key, false, '2026-10-04 10:00:00+02', 120)
RETURNING id
"""

INSERT_OSM_FACT_SQL = """
INSERT INTO fact (fact_type, source, geog, is_sample, osm_element_type, osm_element_id, osm_edited_on, is_removed_from_osm, created_at, created_at_utc_offset_minutes)
VALUES ('stairs', :source, ST_GeogFromText('SRID=4326;POINT(19.9380 50.0620)'), false, 'way', 101, DATE '2026-09-30', :is_removed_from_osm, '2026-10-04 03:00:00+02', 120)
RETURNING id
"""

INSERT_ACCOUNT_SQL = """
INSERT INTO account (pseudonym, password_hash, is_moderator, created_at, created_at_utc_offset_minutes)
VALUES (:pseudonym, 'made-up hash', false, '2026-10-04 09:00:00+02', 120)
RETURNING id
"""

INSERT_ACCOUNT_VOTE_SQL = """
INSERT INTO vote (fact_id, verdict, is_cast_with_account, account_id, cast_at, cast_at_utc_offset_minutes)
VALUES (:fact_id, :verdict, true, :account_id, :cast_at, 120)
ON CONFLICT DO NOTHING
RETURNING id
"""

INSERT_HASH_VOTE_SQL = """
INSERT INTO vote (fact_id, verdict, is_cast_with_account, voter_hash, cast_at, cast_at_utc_offset_minutes)
VALUES (:fact_id, :verdict, false, :voter_hash, :cast_at, 120)
ON CONFLICT DO NOTHING
RETURNING id
"""


def build_idempotency_key(seed: str) -> bytes:
    """Builds a made-up 32-byte idempotency key of a test save, the SHA-256 hash the target schema expects."""
    return hashlib.sha256(f"create_fact:{seed}".encode()).digest()


def build_voter_hash(seed: str, length: int = 32) -> bytes:
    """Builds a made-up hash of a person without an account, cut to the given length."""
    return hashlib.sha256(f"made-up person:{seed}".encode()).digest()[:length]
