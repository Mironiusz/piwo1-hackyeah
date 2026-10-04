"""
The input rules of an account: which pseudonym and which password a person can register (M9 of the specification).

The rules count Unicode code points. A pseudonym loses the spaces U+0020 at both ends and is then kept as it is, without
Unicode normalization, so it is accepted only when every character is a Latin letter, one of the nine Polish letters in
either case, a digit `0` - `9`, the underscore or the hyphen; a Polish letter written as a base letter and a combining
mark is refused like any other character outside that set (`plans/accounts/ACCOUNTS_PLAN.md` D-3). A password is never
trimmed and accepts every character that text in UTF-8 can carry; its length is checked (D-4), and a lone surrogate, which a
JSON escape can produce but UTF-8 cannot encode, is refused (decided by Kuba on 2026-10-04, `ACCOUNTS_REVIEW.md`).
"""

import string

PSEUDONYM_MIN_LENGTH = 3
PSEUDONYM_MAX_LENGTH = 30
PSEUDONYM_CHARACTERS = frozenset(string.ascii_letters + string.digits + "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ" + "_-")
PASSWORD_MIN_LENGTH = 5
PASSWORD_MAX_LENGTH = 128


class InvalidAccountInputError(Exception):
    """A pseudonym or a password outside its rules; `field` names the field of the request it came from."""

    def __init__(self, field: str) -> None:
        super().__init__(field)
        self.field = field


def resolve_pseudonym(raw: str) -> str:
    """Trims the spaces at both ends of a pseudonym and returns it when it meets M9, or refuses it as `pseudonym`."""
    pseudonym = raw.strip(" ")
    if not PSEUDONYM_MIN_LENGTH <= len(pseudonym) <= PSEUDONYM_MAX_LENGTH or not set(pseudonym) <= PSEUDONYM_CHARACTERS:
        raise InvalidAccountInputError("pseudonym")
    return pseudonym


def resolve_password(raw: str) -> str:
    """Returns a password of 5 to 128 code points that UTF-8 can encode unchanged, or refuses it as `password`."""
    if not PASSWORD_MIN_LENGTH <= len(raw) <= PASSWORD_MAX_LENGTH:
        raise InvalidAccountInputError("password")
    try:
        raw.encode("utf-8")
    except UnicodeEncodeError as error:
        raise InvalidAccountInputError("password") from error
    return raw
