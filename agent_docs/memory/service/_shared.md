## 2026-10-04 - Account input rules, password hashes and session tokens (plans/accounts)

- What changed: the first code of the rules layer, written by `plans/accounts/` before the skeleton existed: `service/account_rules.py` checks the pseudonym and the password of M9 with the explicit character set of `plans/accounts/ACCOUNTS_PLAN.md` D-3, `service/passwords.py` hashes with Argon2id at the floor of D-4 through argon2-cffi 25.1.0, and `service/session_tokens.py` issues and checks the HMAC-SHA256 token of D-6 with the standard library only.
- Why: these three need nothing of `backend_skeleton`, so the plan built them first; the actor resolution, the account operations, the data access and the programming interface wait for it.
- Reusable pattern: every way a token can be wrong ends in one `SessionExpiredError`, because the contract answers all of them with `session_expired`; a base64url part is accepted only in canonical form, its re-encoding equal to the input, which refuses padding, foreign characters and loose trailing bits at once; the signature is compared with `hmac.compare_digest` before the JSON is parsed; a JSON integer is checked with `type(value) is int`, because `bool` is an `int` in Python. A pseudonym trims only U+0020 and is never normalized, so a decomposed Polish letter is refused. Tests of time give explicit instants with their offset.
- Risk / notes: a renewed token does not revoke the earlier ones, which stay valid until their own expiry; whoever holds `SESSION_SIGNING_KEY` can forge a session of any account; a login with an unknown pseudonym is verified against `UNKNOWN_ACCOUNT_PASSWORD_HASH`, so its duration matches a wrong password.

## 2026-10-04 - Explicit administrative boundary (backend skeleton)

- What changed: The synchronous administrative wrapper uses the same configuration and log scope as the API.
- Why: An import is manually launched and introduces no periodic worker or duplicate environment reader.
- Reusable pattern: Keep the wrapper open around the complete consumer action and preserve specific publication outcomes.
- Risk / notes: There is no domain rule yet. Create SERVICE.md and SERVICE_ALGORITHM.md with the first product rule.
