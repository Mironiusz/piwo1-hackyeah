"""
Scenario tests of the password hashes of accounts: the encoded Argon2id form with the parameters of
`plans_finished/accounts/ACCOUNTS_PLAN.md` D-4, a match, a refusal and a damaged hash (AC-4 of `plans_finished/accounts/ACCOUNTS_PRD.md`).
"""

import pytest

from service.passwords import UNKNOWN_ACCOUNT_PASSWORD_HASH, build_password_hash, resolve_password_match

ENCODED_PREFIX = "$argon2id$v=19$m=19456,t=2,p=1$"


def test_hash_is_encoded_argon2id_with_the_floor_parameters_and_no_plaintext() -> None:
    password_hash = build_password_hash("pięć znaków")
    assert password_hash.startswith(ENCODED_PREFIX)
    assert "pięć znaków" not in password_hash


def test_two_hashes_of_one_password_differ_by_their_salt() -> None:
    assert build_password_hash("pięć znaków") != build_password_hash("pięć znaków")


def test_right_password_matches_its_hash() -> None:
    assert resolve_password_match(build_password_hash("  spaces count  "), "  spaces count  ")


@pytest.mark.parametrize("password", ["pięć znakóW", "pięć znaków ", "piec znakow", ""])
def test_any_other_password_does_not_match(password: str) -> None:
    assert not resolve_password_match(build_password_hash("pięć znaków"), password)


@pytest.mark.parametrize("password_hash", ["", "not a hash", ENCODED_PREFIX + "broken$broken"])
def test_damaged_hash_matches_nothing(password_hash: str) -> None:
    assert not resolve_password_match(password_hash, "pięć znaków")


def test_hash_of_an_unknown_account_has_the_same_parameters_and_matches_no_chosen_password() -> None:
    assert UNKNOWN_ACCOUNT_PASSWORD_HASH.startswith(ENCODED_PREFIX)
    assert not resolve_password_match(UNKNOWN_ACCOUNT_PASSWORD_HASH, "pięć znaków")
