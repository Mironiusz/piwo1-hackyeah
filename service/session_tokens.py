"""
Signed session tokens of accounts (`docs/product/api_contract.md`, section Sessions and actors).

A token is `<payload>.<signature>`, both parts base64url without padding. The payload is the compact JSON
`{"a": <account id>, "e": <expiry>}`, the expiry in whole milliseconds since the UTC epoch, and the signature is
HMAC-SHA256 of the payload part under the signing key. A token is valid while the current instant is earlier than its
expiry, which is 24 hours after the request that issued it (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-6).

Every way a token can be wrong - its shape, its encoding, its signature, its JSON, its keys and their types, its expiry -
ends in the same `SessionExpiredError`, because the contract answers all of them with `session_expired`. The signature
is checked before the payload is parsed, so content nobody signed is never read.
"""

import base64
import binascii
import hashlib
import hmac
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

SESSION_LIFETIME = timedelta(hours=24)
UTC_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)
ONE_MILLISECOND = timedelta(milliseconds=1)
PAYLOAD_KEYS = frozenset({"a", "e"})


class SessionExpiredError(Exception):
    """A session token that is malformed, wrongly signed or expired, or that belongs to an account that no longer exists."""


@dataclass(frozen=True)
class SessionClaims:
    """What a valid token says: the account it was issued to and the instant it stops being valid."""

    account_id: int
    expires_at: datetime


def build_session_token(account_id: int, now: datetime, signing_key: bytes) -> str:
    """Builds the token of an account, valid until 24 hours after `now`, which is an aware instant."""
    expires_at_ms = (_build_utc_instant(now) + SESSION_LIFETIME - UTC_EPOCH) // ONE_MILLISECOND
    payload = _build_base64url(json.dumps({"a": account_id, "e": expires_at_ms}, separators=(",", ":")).encode("ascii"))
    return f"{payload}.{_build_base64url(_build_signature(payload, signing_key))}"


def resolve_session_claims(token: str, now: datetime, signing_key: bytes) -> SessionClaims:
    """Decides whether a token is valid at `now` and returns its claims, or refuses it with `SessionExpiredError`."""
    parts = token.split(".")
    if len(parts) != 2:
        raise SessionExpiredError
    payload, signature = parts
    payload_bytes = _build_token_part_bytes(payload)
    if not hmac.compare_digest(_build_token_part_bytes(signature), _build_signature(payload, signing_key)):
        raise SessionExpiredError
    claims = _build_session_claims(payload_bytes)
    if _build_utc_instant(now) >= claims.expires_at:
        raise SessionExpiredError
    return claims


def _build_utc_instant(now: datetime) -> datetime:
    """Builds the UTC instant of an aware `now`; a naive value is a bug of the caller, because its zone would be guessed."""
    if now.utcoffset() is None:
        raise ValueError("The current instant of a session token needs a zone offset; a naive datetime is refused.")
    return now.astimezone(UTC)


def _build_signature(payload: str, signing_key: bytes) -> bytes:
    """Builds the HMAC-SHA256 signature of the payload part of a token."""
    return hmac.new(signing_key, payload.encode("ascii"), hashlib.sha256).digest()


def _build_base64url(value: bytes) -> str:
    """Builds the base64url text of bytes without padding."""
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _build_token_part_bytes(part: str) -> bytes:
    """Builds the bytes of a part of a token, refusing any text that is not the canonical base64url of those bytes."""
    try:
        value = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    except (binascii.Error, ValueError) as error:
        raise SessionExpiredError from error
    if not part or _build_base64url(value) != part:
        raise SessionExpiredError
    return value


def _build_session_claims(payload: bytes) -> SessionClaims:
    """Builds the claims of a signed payload, refusing anything but an object of a positive account id and an expiry."""
    try:
        content = json.loads(payload)
    except ValueError as error:
        raise SessionExpiredError from error
    if not isinstance(content, dict) or content.keys() != PAYLOAD_KEYS:
        raise SessionExpiredError
    account_id, expires_at_ms = content["a"], content["e"]
    if type(account_id) is not int or type(expires_at_ms) is not int or account_id <= 0:
        raise SessionExpiredError
    try:
        expires_at = UTC_EPOCH + expires_at_ms * ONE_MILLISECOND
    except OverflowError as error:
        raise SessionExpiredError from error
    return SessionClaims(account_id=account_id, expires_at=expires_at)
