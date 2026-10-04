"""
Scenario tests of the identity of a person without an account: one hash for one pair of IP address and User-Agent, a
different one for any other input or key, and no input in the text of a record or an error
(`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-11, D-17, S-1).
"""

import hashlib
import hmac

import pytest

from service.anonymous_voters import (
    ANONYMOUS_VOTER_HASH_DOMAIN,
    InvalidAnonymousVoterInputError,
    build_anonymous_voter_hash,
    build_anonymous_voter_input,
)

KEY = b"invented-private-voter-hash-key-of-32"
OTHER_KEY = b"invented-private-voter-hash-key-other"
ADDRESS = "203.0.113.7"
USER_AGENT = "Mozilla/5.0 (invented)"


def build_hash(host: str, user_agent: str, key: bytes = KEY) -> bytes:
    """Builds the hash of an invented request."""
    return build_anonymous_voter_hash(build_anonymous_voter_input(host, user_agent), key)


def test_one_pair_gives_one_hash_of_32_bytes() -> None:
    first = build_hash(ADDRESS, USER_AGENT)
    assert first == build_hash(ADDRESS, USER_AGENT)
    assert len(first) == 32


def test_hash_follows_the_framing_of_the_plan() -> None:
    address, agent = ADDRESS.encode("ascii"), USER_AGENT.encode("utf-8")
    message = ANONYMOUS_VOTER_HASH_DOMAIN + len(address).to_bytes(4, "big") + address + len(agent).to_bytes(4, "big") + agent
    assert build_hash(ADDRESS, USER_AGENT) == hmac.new(KEY, message, hashlib.sha256).digest()


@pytest.mark.parametrize(
    ("host", "user_agent", "key"),
    [
        ("203.0.113.8", USER_AGENT, KEY),
        (ADDRESS, USER_AGENT + " ", KEY),
        (ADDRESS, "", KEY),
        (ADDRESS, USER_AGENT, OTHER_KEY),
    ],
)
def test_another_address_user_agent_or_key_gives_another_hash(host: str, user_agent: str, key: bytes) -> None:
    assert build_hash(host, user_agent, key) != build_hash(ADDRESS, USER_AGENT)


def test_empty_user_agent_is_a_value_of_its_own() -> None:
    assert build_hash(ADDRESS, "") == build_hash(ADDRESS, "")
    assert build_hash(ADDRESS, "") != build_hash("203.0.113.70", "")


def test_fields_cannot_shift_into_each_other() -> None:
    assert build_hash("2001:db8::1", "a") != build_hash("2001:db8::", "1a")


@pytest.mark.parametrize("mapped", ["::ffff:203.0.113.7", "::FFFF:cb00:7107", "0:0:0:0:0:ffff:203.0.113.7"])
def test_ipv4_mapped_ipv6_address_is_its_ipv4_address(mapped: str) -> None:
    assert build_hash(mapped, USER_AGENT) == build_hash(ADDRESS, USER_AGENT)


def test_one_ipv6_address_written_two_ways_is_one_identity() -> None:
    assert build_hash("2001:DB8:0:0:0:0:0:1", USER_AGENT) == build_hash("2001:db8::1", USER_AGENT)


@pytest.mark.parametrize("host", [None, "", "testclient", "203.0.113", "unix:/run/api.sock"])
def test_peer_that_is_not_an_ip_address_is_refused_without_its_text(host: str | None) -> None:
    with pytest.raises(InvalidAnonymousVoterInputError) as refusal:
        build_anonymous_voter_input(host, USER_AGENT)
    assert str(refusal.value) == ""
    assert USER_AGENT not in repr(refusal.value)


def test_record_text_holds_neither_input() -> None:
    text = repr(build_anonymous_voter_input(ADDRESS, USER_AGENT))
    assert ADDRESS not in text
    assert USER_AGENT not in text
