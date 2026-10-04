"""
The identity of a person without an account: a one-way hash of the IP address and the User-Agent header of the request, and nothing else (M9).

The hash is HMAC-SHA256 under the secret `VOTER_HASH_KEY` over the domain `ANONYMOUS_VOTER_HASH_DOMAIN` followed by two
fields, each a 4-byte big-endian length and its UTF-8 bytes: the canonical address, then the User-Agent. The canonical
address is the IP address in compressed form, with an IPv4-mapped IPv6 address reduced to its IPv4 address, so one
connection gives one identity however the server wrote its peer. Identical pairs share one identity, which the
specification accepts; a changed key gives every person a new identity, so the key stays the same for the whole demo
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-11, D-15).

Neither the address nor the User-Agent appears in the text of a record or of an error, and nothing here logs.
"""

import hashlib
import hmac
import ipaddress
from dataclasses import dataclass, field

ANONYMOUS_VOTER_HASH_DOMAIN = b"enableme-anonymous-voter:v1"
FIELD_LENGTH_BYTES = 4


class InvalidAnonymousVoterInputError(Exception):
    """The request carries no peer address that is an IP address, which is a fault of the transport, not an input of the person."""


@dataclass(frozen=True)
class AnonymousVoterInput:
    """The two inputs of the identity of a person without an account; both stay out of the text of the record."""

    address: ipaddress.IPv4Address | ipaddress.IPv6Address = field(repr=False)
    user_agent: str = field(repr=False)


def build_anonymous_voter_input(host: str | None, user_agent: str) -> AnonymousVoterInput:
    """Builds the inputs of an identity from the peer host of a request and its User-Agent, refusing a missing host or one that is not an IP address."""
    if host is None:
        raise InvalidAnonymousVoterInputError
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        raise InvalidAnonymousVoterInputError from None
    return AnonymousVoterInput(address=address, user_agent=user_agent)


def build_canonical_address(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> str:
    """Builds the compressed text of an address, an IPv4-mapped IPv6 address written as its IPv4 address."""
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        return address.ipv4_mapped.compressed
    return address.compressed


def build_hash_field(value: str) -> bytes:
    """Builds one field of the hashed message: the 4-byte big-endian length of the UTF-8 bytes of the value, then those bytes."""
    encoded = value.encode("utf-8")
    return len(encoded).to_bytes(FIELD_LENGTH_BYTES, "big") + encoded


def build_anonymous_voter_hash(voter: AnonymousVoterInput, key: bytes) -> bytes:
    """Builds the 32 bytes that identify a person without an account under the given key."""
    message = ANONYMOUS_VOTER_HASH_DOMAIN + build_hash_field(build_canonical_address(voter.address)) + build_hash_field(voter.user_agent)
    return hmac.new(key, message, hashlib.sha256).digest()


def fetch_voter_hash_key() -> bytes:
    """Reads the key of the anonymous identity from the configuration facade, imported here so a module import needs no configuration."""
    from config.config import VOTER_HASH_KEY

    return VOTER_HASH_KEY.get_secret_value().encode("utf-8")
