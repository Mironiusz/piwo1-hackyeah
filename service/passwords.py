"""
Password hashes of accounts: Argon2id in its encoded form, which carries its parameters inside every hash.

The parameters are the floor of `plans_finished/account_sessions/ACCOUNT_SESSIONS_PLAN.md` D-4 - 19 MiB of memory,
2 iterations and 1 degree of parallelism - chosen in `plans_finished/accounts/ACCOUNTS_PLAN.md` D-4 to keep one login cheap on
the shared server of the demo. A hash written with other parameters is still verified, because they travel in it.

`UNKNOWN_ACCOUNT_PASSWORD_HASH` is the hash of a random value built once per process. A login with a pseudonym that has
no account is verified against it, so it takes as long as a login with a wrong password and does not tell the two
apart by its duration (D-5).
"""

import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

PASSWORD_HASHER = PasswordHasher(time_cost=2, memory_cost=19456, parallelism=1)


def build_password_hash(password: str) -> str:
    """Builds the encoded Argon2id hash of a password with a fresh random salt."""
    return PASSWORD_HASHER.hash(password)


def resolve_password_match(password_hash: str, password: str) -> bool:
    """Decides whether a password matches a stored hash; a wrong password and a damaged hash both give False."""
    try:
        return PASSWORD_HASHER.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


UNKNOWN_ACCOUNT_PASSWORD_HASH = build_password_hash(secrets.token_urlsafe(32))
