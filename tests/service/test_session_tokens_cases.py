"""
Scenario tests of the signed session tokens of `plans_finished/accounts/ACCOUNTS_PLAN.md` D-6: the rolling 24 hours of AC-6 of
`plans_finished/accounts/ACCOUNTS_PRD.md` with explicit instants, and every malformed, tampered or foreign token refused with the
same `SessionExpiredError` (AC-8).
"""

import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime

import pytest

from service.session_tokens import SessionClaims, SessionExpiredError, build_session_token, resolve_session_claims

SIGNING_KEY = b"k" * 32
OTHER_KEY = b"o" * 32
LOGIN_AT = datetime.fromisoformat("2026-10-04T10:00:00.000+02:00")
READ_AT = datetime.fromisoformat("2026-10-04T15:00:00.000+02:00")


def build_part(value: bytes) -> str:
    """Builds the base64url text of bytes without padding, as a token part."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def build_signed_token(payload: bytes, signing_key: bytes = SIGNING_KEY) -> str:
    """Builds a token of any payload bytes with a correct signature, to reach the checks behind the signature."""
    payload_part = build_part(payload)
    return f"{payload_part}.{build_part(hmac.new(signing_key, payload_part.encode('ascii'), hashlib.sha256).digest())}"


def test_token_of_a_login_is_valid_until_24_hours_later() -> None:
    token = build_session_token(42, LOGIN_AT, SIGNING_KEY)
    claims = resolve_session_claims(token, datetime.fromisoformat("2026-10-05T09:59:59.999+02:00"), SIGNING_KEY)
    assert claims == SessionClaims(account_id=42, expires_at=datetime(2026, 10, 5, 8, 0, tzinfo=UTC))


def test_token_is_refused_at_its_expiry_and_after_it() -> None:
    token = build_session_token(42, LOGIN_AT, SIGNING_KEY)
    for now in ("2026-10-05T10:00:00.000+02:00", "2026-10-05T10:00:00.001+02:00", "2026-10-06T00:00:00.000+02:00"):
        with pytest.raises(SessionExpiredError):
            resolve_session_claims(token, datetime.fromisoformat(now), SIGNING_KEY)


def test_token_renewed_at_15_00_expires_at_15_00_of_the_next_day() -> None:
    renewed = build_session_token(42, READ_AT, SIGNING_KEY)
    assert resolve_session_claims(renewed, datetime.fromisoformat("2026-10-05T14:59:59.999+02:00"), SIGNING_KEY).account_id == 42
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(renewed, datetime.fromisoformat("2026-10-05T15:00:00.000+02:00"), SIGNING_KEY)


def test_expiry_does_not_depend_on_the_offset_the_instant_was_given_in() -> None:
    token = build_session_token(42, LOGIN_AT.astimezone(UTC), SIGNING_KEY)
    assert resolve_session_claims(token, LOGIN_AT, SIGNING_KEY).expires_at == datetime(2026, 10, 5, 8, 0, tzinfo=UTC)


def test_naive_current_instant_is_refused_on_both_sides() -> None:
    token = build_session_token(42, LOGIN_AT, SIGNING_KEY)
    with pytest.raises(ValueError, match="naive"):
        build_session_token(42, datetime(2026, 10, 4, 10, 0), SIGNING_KEY)
    with pytest.raises(ValueError, match="naive"):
        resolve_session_claims(token, datetime(2026, 10, 4, 10, 0), SIGNING_KEY)


def test_token_signed_with_another_key_is_refused() -> None:
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(build_session_token(42, LOGIN_AT, OTHER_KEY), LOGIN_AT, SIGNING_KEY)


def test_token_with_a_changed_payload_is_refused() -> None:
    signature = build_session_token(42, LOGIN_AT, SIGNING_KEY).split(".")[1]
    forged_payload = build_part(json.dumps({"a": 43, "e": 1_900_000_000_000}, separators=(",", ":")).encode("ascii"))
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(f"{forged_payload}.{signature}", LOGIN_AT, SIGNING_KEY)


def test_token_with_a_changed_signature_is_refused() -> None:
    payload, signature = build_session_token(42, LOGIN_AT, SIGNING_KEY).split(".")
    changed = ("A" if signature[0] != "A" else "B") + signature[1:]
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(f"{payload}.{changed}", LOGIN_AT, SIGNING_KEY)


@pytest.mark.parametrize(
    "token",
    [
        "",
        ".",
        "abc",
        "a.b.c",
        "ż.ż",
        "@@@@.@@@@",
        "abcd==.abcd==",
        "eyJhIjo0Mn0.",
        ".c2lnbmF0dXJl",
    ],
)
def test_malformed_token_is_refused(token: str) -> None:
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(token, LOGIN_AT, SIGNING_KEY)


def test_token_with_padding_is_refused() -> None:
    payload, signature = build_session_token(42, LOGIN_AT, SIGNING_KEY).split(".")
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(f"{payload}=.{signature}", LOGIN_AT, SIGNING_KEY)


@pytest.mark.parametrize(
    "payload",
    [
        b"not json",
        b"\xff\xfe",
        b"[42, 1900000000000]",
        b'{"a": 42}',
        b'{"e": 1900000000000}',
        b'{"a": 42, "e": 1900000000000, "x": 1}',
        b'{"a": "42", "e": 1900000000000}',
        b'{"a": true, "e": 1900000000000}',
        b'{"a": 0, "e": 1900000000000}',
        b'{"a": -1, "e": 1900000000000}',
        b'{"a": 42.0, "e": 1900000000000}',
        b'{"a": 42, "e": 1900000000000.5}',
        b'{"a": 42, "e": "1900000000000"}',
        b'{"a": 42, "e": true}',
        b'{"a": 42, "e": NaN}',
        b'{"a": 42, "e": 99999999999999999999999999}',
    ],
)
def test_signed_payload_of_a_wrong_shape_is_refused(payload: bytes) -> None:
    with pytest.raises(SessionExpiredError):
        resolve_session_claims(build_signed_token(payload), LOGIN_AT, SIGNING_KEY)


def test_signed_payload_of_the_right_shape_is_accepted() -> None:
    claims = resolve_session_claims(build_signed_token(b'{"e":1900000000000,"a":7}'), LOGIN_AT, SIGNING_KEY)
    assert claims.account_id == 7
