"""
Scenario tests of the input rules of an account: the pseudonym and the password of M9 (AC-1, AC-2 and AC-4 of
`plans/accounts/ACCOUNTS_PRD.md`), on both sides of every limit, with the character set of
`plans/accounts/ACCOUNTS_PLAN.md` D-3.
"""

import pytest

from service.account_rules import InvalidAccountInputError, resolve_password, resolve_pseudonym

POLISH_LETTERS = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"


def test_pseudonym_loses_the_spaces_at_both_ends_and_keeps_its_case() -> None:
    assert resolve_pseudonym("  Wózek_KRK  ") == "Wózek_KRK"


@pytest.mark.parametrize("pseudonym", ["abc", "a" * 30, "Wózek-KRK_2026", "ZAŻÓŁĆ_gęślą_jaźń", "x-_9", "123"])
def test_pseudonym_inside_the_rules_is_accepted(pseudonym: str) -> None:
    assert resolve_pseudonym(pseudonym) == pseudonym


@pytest.mark.parametrize("letter", list(POLISH_LETTERS))
def test_every_polish_letter_in_both_cases_is_accepted(letter: str) -> None:
    assert resolve_pseudonym(f"ab{letter}") == f"ab{letter}"


@pytest.mark.parametrize(
    "pseudonym",
    [
        "ab",
        "a" * 31,
        "  ab  ",
        "",
        "Wózek KRK",
        "Wózek!",
        "Jürgen_99",
        "Čapek",
        "\u0436aba",
        "Wo\u0301zek",
        "\tWózek",
        "Wózek\n",
        "Wózek.KRK",
        "Wózek@KRK",
        "\u0663\u0663\u0663",
        "ab\ud800",
    ],
)
def test_pseudonym_outside_the_rules_is_refused_as_its_field(pseudonym: str) -> None:
    with pytest.raises(InvalidAccountInputError) as refusal:
        resolve_pseudonym(pseudonym)
    assert refusal.value.field == "pseudonym"


def test_pseudonym_length_counts_code_points_after_the_trim() -> None:
    assert resolve_pseudonym(" " + "ż" * 30 + " ") == "ż" * 30
    with pytest.raises(InvalidAccountInputError):
        resolve_pseudonym("ż" * 31)


@pytest.mark.parametrize("password", ["a" * 5, "a" * 128, "pięć ", "  spaces inside and around  ", "\U0001f600" * 5, "password", "12345", "\x00\x01\x02\x03\x04"])
def test_password_of_5_to_128_code_points_is_accepted_unchanged(password: str) -> None:
    assert resolve_password(password) == password


@pytest.mark.parametrize("password", ["a" * 4, "a" * 129, "", "\U0001f600" * 4, "ż" * 129, "\ud800abcde", "abcde\udfff"])
def test_password_outside_5_to_128_code_points_is_refused_as_its_field(password: str) -> None:
    with pytest.raises(InvalidAccountInputError) as refusal:
        resolve_password(password)
    assert refusal.value.field == "password"
