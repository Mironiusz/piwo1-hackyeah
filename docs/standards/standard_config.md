# Configuration and secrets standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

Configuration spread across the repository is a problem that surfaces only during a secret rotation or an audit: the question "where is this read from and who else uses it" then has to be answered by searching the whole code instead of opening one file. The second cost is quieter: when every place reads an environment variable its own way, some of them do it with a default value, some without, and a configuration error, instead of crashing at startup, surfaces randomly, in production, far from the cause.

This standard sets where a configuration value is to live and who has the right to read it.

## Scope and boundaries

This standard is responsible for: splitting configuration into layers, the rule for assigning a value to a layer, validating values coming from the environment, the place where secrets are stored and the contents of the configuration file.

What is not here:

- detecting secrets hardcoded in code and the dependency vulnerability scan - that is `standard_security.md`;
- the format, levels and content of a log entry, even though the log level is a configuration value - that is `standard_logging.md`;
- one source of truth for shared mechanisms as an architectural rule - that is `standard_architecture.md`;
- what exactly the service needs to have configured in the second and third layers - that is the product specification pointed to in `CLAUDE.md`. The names and meaning of the first layer's entries, on the other hand, are here, in the section about environment entries, because none of the three templates contains comments and so cannot carry them.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## Three configuration layers and four storage places

The first layer: environment variables. Everything that is a secret, and every non-secret that depends on the machine or on the environment. Names and values live in three versioned templates, `.env.example`, `.env.local.example` and `.env.priv.example`, and the meaning of each entry is described below in this document - the template file cannot carry it, because it contains no comments.

The environment contract requires every template key to also be present in the corresponding local file. The project enforces this rule with an architecture test that it creates together with the first code of this layer; the template does not contain it. Further in this document this test is called the environment contract test.

The split into three templates follows two questions asked in order. The first: is the value a secret. A secret goes to `.env.example`, unless it is a credential under which each team member acts in their own name in someone else's system - then it goes to `.env.priv.example`. The second question concerns non-secrets only: does the value differ between machines or environments. If yes, it goes to `.env.local.example`; if not, it is not an environment entry at all and is written directly in the second layer.

Separating secrets from the rest has one specific gain: the question of what in this repository is a secret is answered by opening one file in which every entry is one, instead of deciding it entry by entry. Separating personal credentials has two: the shared template stops forcing you to fill in a value that nobody can provide on someone else's behalf, and the personal credential sits in a file that is not opened when setting up the environment.

The split into three files is a purely local fact. The target environment gets one set of variables and knows nothing about the split into files, so any rule based on which file a value sits in describes the developer's machine, not the target environment.

The second layer: global configuration, that is `config/config.py`. The only place in the repository that reads environment variables and environment files, and at the same time the only place from which the rest of the repository takes configuration. It exposes ready, typed values as module constants, so the calling module does not know, and is not supposed to know, whether a given value came from the environment or is written directly. Contract validation is performed by `config/settings.py`. Neither it nor the other second-layer modules, for example reading the environment file format, reach for the environment themselves - they all get values passed in from the facade.

There is one order of sources in the facade, and whatever comes first takes precedence: process variables, then the local values file, then the secrets file. The launcher of tools running outside the full application environment uses the same order, so a value given before the command wins over the file in both paths. The facade does not read the personal credentials file at all.

The third layer: local configuration. Constants belonging to one piece of code and not differing between environments: limits, thresholds, names, default values of domain rules. They live next to the code they concern, not in the second layer.

## Environment entries

Every entry of the three templates has a record in this section, added together with the entry in the template. The record gives the entry's name, its meaning, whether the entry is required or has a default value, and how the process behaves when it is missing. The first entries came on 2026-10-04 with the database of `db/` (`plans_finished/schema_first_revision/`); every one of them is required and has no default value, and an empty or missing entry stops the Compose files of `db/`, `db/accessibility_db/migrations/env.py` or the critical tests of `db/tests/` with its name.

| Entry                         | Template             | Meaning                                                                                                                                                                                            |
| ----------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DB_BOOTSTRAP_PASSWORD`       | `.env.example`       | The password of the bootstrap superuser the database image creates at its first start, used only by the script creating accounts.                                                                  |
| `DB_SCHEMA_OWNER_PASSWORD`    | `.env.example`       | The password of the schema owner account, which owns the database and applies the revisions.                                                                                                       |
| `DB_SERVICE_ACCOUNT_PASSWORD` | `.env.example`       | The password of the service account of the running app, the import included.                                                                                                                       |
| `SESSION_SIGNING_KEY`         | `.env.example`       | The secret that signs and verifies the session tokens of accounts, at least 32 characters; whoever holds it can forge a session of any account, and changing it ends every session.                |
| `DB_NAME`                     | `.env.local.example` | The name of the database.                                                                                                                                                                          |
| `DB_BOOTSTRAP_NAME`           | `.env.local.example` | The name of the bootstrap superuser of the database image.                                                                                                                                         |
| `DB_SCHEMA_OWNER_NAME`        | `.env.local.example` | The name of the schema owner account.                                                                                                                                                              |
| `DB_SERVICE_ACCOUNT_NAME`     | `.env.local.example` | The name of the service account; the first revision grants its rights to this name.                                                                                                                |
| `DB_HOST_PORT`                | `.env.local.example` | The port of the local machine at which `db/compose.yaml` publishes the database on `127.0.0.1`; the hosted demo publishes none.                                                                    |
| `APP_ENVIRONMENT`             | `.env.local.example` | The environment of the backend, `local` or `target`; the critical tests run only under `local`.                                                                                                    |
| `API_BIND_HOST`               | `.env.local.example` | The IP address or host name on which `python -m api` listens.                                                                                                                                      |
| `API_PORT`                    | `.env.local.example` | The port, 1 - 65535, on which `python -m api` listens.                                                                                                                                             |
| `BUSINESS_TIMEZONE`           | `.env.local.example` | The IANA business zone of `standard_time.md`, `Europe/Warsaw` for this project.                                                                                                                    |
| `LOG_LEVEL`                   | `.env.local.example` | The level of the shared logger, one of `DEBUG`, `INFO`, `WARNING`, `ERROR` and `CRITICAL`.                                                                                                         |
| `IMPORT_WORKSPACE_ROOT`       | `.env.local.example` | The absolute path of the one persistent import workspace of a database, read only by the import exclusion (`docs/setup/backend.md`).                                                               |
| `ROUTING_SERVICE_URL`         | `.env.local.example` | The `http` or `https` address of the routing service of the project, called only by `data/valhalla.py`.                                                                                            |
| `ROUTING_DATA_DIR`            | `.env.local.example` | The absolute path of the routing data, with `copies/<name>/` of every copy and the pointer `current`, written by the import and read by the backend for the boundary of Kraków of the copy in use. |
| `VALHALLA_TOOL_DIR`           | `.env.local.example` | The absolute path of the directory of the Valhalla build tools the import runs.                                                                                                                    |
| `VALHALLA_CONFIG_TEMPLATE`    | `.env.local.example` | The absolute path of the Valhalla JSON configuration whose `mjolnir` section the import specializes for each build.                                                                                |
| `PUBLIC_TRANSPORT_ENABLED`    | `.env.local.example` | Whether the app offers routes with public transport (O9): `true` turns them on, `false` or the empty marker keeps walking routes only.                                                             |
| `TILE_ARCHIVE_SOURCE`         | `.env.local.example` | The absolute path of the map tile archive a person put on the machine, read only by `python -m worker.tile_archive`, which copies it into `TILE_ARCHIVE_DIR`; it lies outside that directory.      |
| `TILE_ARCHIVE_DIR`            | `.env.local.example` | The absolute path of the directory from which the proxy serves the map tile archive at `/tiles/krakow.pmtiles`, written only by `python -m worker.tile_archive`.                                   |

The backend entries came on 2026-10-04 with `plans_finished/backend_skeleton/` and are read by the configuration facade `config/config.py`. `APP_ENVIRONMENT`, `API_BIND_HOST`, `API_PORT` and `BUSINESS_TIMEZONE` are required and have no default value: an empty or missing one stops `python -m api` and every other process that imports the facade with its name and file. `LOG_LEVEL` defaults to `INFO`, and its empty marker means that default, never a more verbose level. `IMPORT_WORKSPACE_ROOT` is an administrative entry in the sense of the section Validating values from the environment: empty or missing, it does not stop the API and the facade exposes it as `None`; a relative path stops the facade with its name. The import passes it explicitly to `apply_import_exclusion` of `data/locks.py` and, when it is `None`, ends its run as failed with a named exception before any acquisition (`docs/setup/backend.md`, section Configuration).

`SESSION_SIGNING_KEY` came on 2026-10-04 with `plans_finished/accounts/` and is required and has no default value: an empty or missing one, or one shorter than 32 characters, stops `python -m api` and every other process that imports the facade with its name and file, without its value. It is a secret, so it stands in `.env.example` next to the passwords, and every environment generates its own, for example with `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Changing it makes every token signed with the old one fail with `session_expired`, so every person has to log in again (`plans_finished/accounts/ACCOUNTS_PLAN.md` D-6).

The routing entries came on 2026-10-04 with `plans_finished/route_planning/` and `plans_finished/osm_importer/`. `ROUTING_SERVICE_URL` and `ROUTING_DATA_DIR` are required and have no default value: an empty or missing one, an address with a scheme other than `http` or `https` or without a host, or a relative path stops every process that imports the facade with its name and file, because the API calls the routing service and reads the boundary of Kraków of the copy in use, and the import writes the routing data. `VALHALLA_TOOL_DIR` and `VALHALLA_CONFIG_TEMPLATE` are administrative entries like `IMPORT_WORKSPACE_ROOT`: empty or missing, they do not stop the API and the facade exposes them as `None`, a relative path stops the facade with its name, and the import ends its run as failed with a named configuration failure when one of them is missing (`plans_finished/osm_importer/OSM_IMPORTER_PLAN.md` D-50). The loading step of the GTFS, `python -m worker.gtfs_import`, needs all three and `IMPORT_WORKSPACE_ROOT` in the same way (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-11).

`PUBLIC_TRANSPORT_ENABLED` came on 2026-10-04 with `plans/public_transport_routing/` and is optional with the default `false`: missing or empty, it keeps the app at walking routes only; only the exact text `true` turns routes with public transport on, and any other value stops the facade with its name. The team sets it to `true` in an environment only after a route with a tram in Kraków works there, and back to `false` everywhere when the time box of O9 ends without one (`docs/product/specification.md`, O9; `plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-5).

The tile entries came on 2026-10-04 with `plans_finished/tile_loading/`. `TILE_ARCHIVE_SOURCE` and `TILE_ARCHIVE_DIR` are administrative entries like `IMPORT_WORKSPACE_ROOT`: empty or missing, they do not stop the API and the facade exposes them as `None`, a relative path stops the facade with its name, and `python -m worker.tile_archive` ends as failed with a named configuration failure when one of them or `IMPORT_WORKSPACE_ROOT` is missing (`plans_finished/tile_loading/TILE_LOADING_PLAN.md` D-3).

The Compose files of `db/` also set, for the containers that apply the revisions and run the tests, `DB_HOST` and `DB_PORT`, the address of the database inside the network of Compose, and `DB_ENVIRONMENT`, `local` in `db/compose.yaml` and `target` in `db/compose.deploy.yaml`. They are written in those files, not in a template, because they follow from the file itself; the critical tests refuse to run unless `DB_ENVIRONMENT` is `local`. The backend reads `DB_HOST` and `DB_PORT` too, together with `DB_NAME`, `DB_SERVICE_ACCOUNT_NAME` and `DB_SERVICE_ACCOUNT_PASSWORD`, and builds from them the address of the service account in `data/engine.py`, decided by the user on 2026-10-04 at the merge of `mw-osm-import`. For the same reason they stay out of the templates: whoever launches the backend gives them - the Compose file of the backend on the hosted demo, and on a developer machine `127.0.0.1` and the value of `DB_HOST_PORT` - and a missing or empty one stops the configuration facade with its name.

A value given ad hoc at call time, such as consent to apply a revision to the target environment's database, has no entry in any template and cannot have one. Absence from the template is a rule here, not an oversight, and follows directly from the environment contract: every template key has to also be present in the local file, so an entry in the template would make you write the consent down once and for all - and consent written into a file stops being consent, and the gate becomes a fiction. For the same reason, adding such a key to your own environment file is a workaround of the rule, not a convenience: the environment contract test will not catch it, because it checks the template keys, not extra keys. For the revisions of `db/` this consent is `DB_REVISION_CONSENT=apply`, given with `-e` to the call of the profile `migrate` of `db/compose.deploy.yaml`.

## Rule for assigning a value to a layer

The place of a value is decided first by secrecy, then by expected variability:

- the value is a secret - first layer, the secrets file, and for a personal credential the private file;
- the value is not a secret but depends on the machine or on the environment - first layer, the local values file;
- the value is not a secret, we assume it will not change, and more than one place uses it - second layer, written directly;
- the value is constant across all environments and used in one place - third layer.

The expected variability criterion is a judgment, not a fact, and a mistake in one direction means that changing the value requires a deployment instead of editing an entry. That is why a value that someone will one day want to change without a deployment stays an environment entry even when it is the same everywhere today.

A value that is the same everywhere also stays an environment entry when it is read by a consumer outside Python, for example compose file interpolation or a shell script: only Python code can import a constant from the second layer. An entry that no service process reads has no counterpart either in the settings model or in the facade.

Not every non-secret may be brought into the repository, and this rule is independent of the ones above. No address, host, login or secret of the target environment enters the repository in any form - not into the code, not into the documentation, not into the environment template. The same ban covers user identifiers of a third-party system. A non-secret covered by the ban goes to the local values file regardless of the fact that it does not change, and in the second layer only the entry name appears, never its content. In the template, a to-fill-in marker stands in place of the value, and in the target environment a human enters the value in that environment's configuration.

The consequence of these rules is unambiguous and intended: reading an environment variable outside the second layer is a violation of the standard, no matter how local the value is and how convenient it was to read it on the spot. Scattered environment reads are exactly the state in which you cannot answer the question of what the service needs to have set without searching the whole code.

The only allowed exception: code run outside the full application environment. This includes one-off tools run from the command line, the environment of the schema revisions (`alembic/env.py`, in this repository `db/accessibility_db/migrations/env.py`), and those conftests and tests that read entries unknown to the facade, for example the migration account address. Such an exception is described in a docstring at the place of the read, together with the reason - it is not silent.

The connection address for the schema owner account, used only when applying revisions, is read by the environment of the schema revisions (`alembic/env.py`, in this repository `db/accessibility_db/migrations/env.py`) directly from the environment, and the second layer does not know it and is not supposed to: the account that changes the schema has no right to sit in a layer that every service process imports. A missing address stops Alembic with the name of the correct key, without a fallback.

## Validating values from the environment

A value coming from the environment is validated at process startup, not at first use. A missing required variable or a value of an incorrect type stops startup with a message saying which variable is missing and in which file that variable is supposed to be - it does not continue with a default value and does not crash later, in a random place. The assignment of entries to files sits in `config/settings.py` as an explicit map and is maintained together with the templates: adding an entry to a template without a record in this map gives a message that names the variable but is silent about the file.

A violation message gives the variable name and the name of the broken rule, never the value or a fragment of it.

Validation checks the shape of the value, not the state of the resource the value points to. It does not check whether a directory or file exists at a path from the configuration - a missing resource of this kind surfaces on the readiness probe or at first use.

The address to which the process sends a secret or a token, and the address from which it fetches public keys for verifying token signatures, must use HTTPS, with no exception for local addresses, because the former carries a credential, and a substituted key set would validate any token. A violation stops startup.

A default value is allowed only where a sensible safe value exists and using it does not hide a configuration error. A connection string has no default value. The log level does - and it is `INFO`, never `DEBUG`: a default `DEBUG` level combined with the personal data rule from `standard_logging.md` turns every oversight in the code into data exposure.

The business zone (`standard_time.md`) has no default value and cannot have one: the machine's zone looks like a sensible default, but it is a value that on a different server silently changes the stored offset. A switch exposing anything beyond the product contract, for example an interactive viewer of the interface document, defaults to off: a deployment that does not know about the switch exposes nothing beyond the specification.

For a required entry an empty value is sometimes a legitimate decision, for example an empty list of origins from which a browser may call the service means that no browser has access. A missing key and an empty value are then two different things: the first is unfilled configuration and stops startup, the second is a deliberate decision.

The exception to validation at startup is an entry that is not read by the process handling requests, but only by the worker process or by a single periodic task. Such an entry may be optional and have no default value: its absence does not stop the startup of the API, and it surfaces at the first attempt to use it as a named exception and ends the run as failed. The absence is not silent either: the run records in its details that configuration is missing, instead of pretending it did the work. For such an entry an empty value means missing configuration, explicitly and on purpose, because the environment contract requires every template key to be present in the local file, and a machine on which nobody configures this function leaves the entry empty.

The service is built on Pydantic, so the environment contract is a validated model, not a set of loose checks scattered across the code. The model gives type validation, an explicit message about a missing value and one place where the whole contract is visible. The facade injects values into it with one map - the model does not read the environment itself, so a test gives it its own map instead of replacing process variables.

## Secrets

A secret does not enter the repository in any form - not as a default value in code, not as an example in documentation, not in a template file. `.env.example` contains only explicit placeholders to fill in, also for values that are not secrets: the server address, the database name and the account name. The reason for these three: together with the password they form a complete access set, and separately they are a map of the infrastructure that has no reason to lie in a public repository.

A secret issued by an external system arrives through the channel indicated by its issuer, never through the repository, a ticket or a chat.

A personal credential that grants write access to a system outside this repository has a stricter usage boundary than the other entries. Neither the second layer nor any of the three service layers may read it, it may not be passed as a command-line argument, and its value may not be printed in any form - not in a tool report, not in an exception message, not in a log. It is read only by the tool that needs it, and redacted in one place before anything reaches the output. The name of such an entry stands in the private template so that it is the same for the whole team.

All three local files are in `.gitignore`, and access to the secret files, that is `.env` and `.env.priv`, is blocked on the agent tool side by two barriers, neither of which replaces the other.

The first is the block list in `.claude/settings.json`. It covers reading and writing with file-operating tools - writing because the secrets file belongs to the human, and overwriting it is irreversible other than by regenerating everything from scratch on the other side. The list names each file explicitly and is not a pattern, so a new secrets file has to be added to it - otherwise, simply by existing, it sits outside the reach of the rule.

The second is the hook `block_dangerous_commands.py`, which stops shell commands that print the contents of such a file, as well as recursive searches of the tree root without an explicit exclusion of secret files, because a pattern run across the whole tree hits the secrets file just as it hits the code. The hook recognizes a command by its first word, so it does not see a read inside an interpreter - and this is a deliberate concession, because a program that reads a secret from a file and passes it on is the recommended way. Moreover, the hook works only on the Claude Code side, with no counterpart on the Codex side.

Neither of these two barriers covers `.env.local`, and this is a decision, not an oversight. In most ecosystems this name means a file of local secrets; in this repository it carries only non-secrets, so its contents may be quoted in conversation and in a report. The price is real and accepted deliberately: a secret written there out of habit will be caught neither by the read block nor by the shell command check.

Both barriers protect against a mistake, neither against intent. A token or password revealed anywhere, including in command output, is considered burned and is revoked on the side of the system that issued it.

The rule ignoring local files rests on the pattern `.env.*`, from which the versioned templates are excluded by the negations `!.env.example` and `!.env.*.example`. The order in `.gitignore` is part of the rule here, because a negation works only after a pattern that matches the given file. A one-letter difference between the template name and the local file name decides whether the secret stays on the machine, so both conditions - the presence of the pattern and the absence of a negation for the local file - are enforced by the environment contract test.

A secret also does not go into a log, into the error body returned by the API, or into an exception message. In the settings model a secret has the type `SecretStr`, so it does not end up in repr. A connection string in an exception message is the most common way a password lands in a log.

## Contents of environment files

Environment files contain no comments. The ban covers all six: the versioned templates `.env.example`, `.env.local.example` and `.env.priv.example` and the local files `.env`, `.env.local` and `.env.priv`, and there is no exception to it for an explanatory comment, a grouping header or a section marker.

The reason has two parts. A template is copied and filled in, so a comment in it drifts away from the contract at the first change and from that moment describes a state that no longer exists - and it is then read by someone who has no way of noticing that the description is outdated. The second part is more important: the description of a variable's meaning has one place, and that place is this standard, the section about environment entries. Two places describing the same thing are two places to update and one that someone will forget.

The consequence is intended: adding a variable to a template without describing it in this document is an incomplete change, just like adding it only here.

The rule is not enforced by a test. The environment contract test reads the environment files skipping comments, because its job is to compare keys, not to check form - extending it would change its purpose. Enforcement stays with the human and with review.

The to-fill-in marker in a template is a value that does not pass validation. A copied and unfilled template is supposed to stop startup with the variable name, not set up a working configuration pointing to a non-existent resource.

## Contents of the configuration file

The configuration file contains values and their validation. It does not contain domain logic, does not execute queries, does not open connections and has no side effects other than reading the environment.

Importing the configuration facade is expensive and requires a complete environment, because the values are created at import time. The cost is paid by anyone who imports anything from `api/`, `service/` or `data/`, including a test that itself requests no value. This is the price for the rest of the repository having one configuration address instead of a function that has to be called and whose result has to be cleared between tests. The symptom of a missing value is immediate and named, not silent.

The second-layer modules standing under the facade - contract validation, reading the environment file format and logging configuration - have a cheap and safe import, and it is to stay that way. They are the ones imported by tools running outside the full application environment.

Configuration is not a place to work around a missing value. If a value is required and is not present in the environment, the correct reaction is to stop startup, not to substitute anything.

## Checklist

- Does any new read of an environment variable appear outside the configuration facade - and if so, is it an exception described in a docstring for code outside the full application environment?
- Did the new environment entry go to the correct one of the three files: a secret to `.env`, a personal credential to `.env.priv`, a non-secret depending on the machine or environment to `.env.local` - and did an unchanging non-secret not become an environment entry at all?
- Does the new environment entry have a record in the entry-to-file assignment map in `config/settings.py`, so that the message about its absence also names the file?
- Does every new required value from the environment stop process startup when it is missing, instead of continuing with a default value?
- Is the new optional entry read only by the worker process or a periodic task, and does its absence end the run with a named exception instead of a silent skip?
- Does the validation violation message name the variable and the rule, without the value or a fragment of it?
- Is the new default value safe, and does it avoid hiding a configuration error?
- Did the new configuration value go to the layer that follows from its origin, not from its scope of use?
- Was the new environment variable added to the correct template as a to-fill-in marker that does not pass validation, without a real value, and was its meaning described in the section about environment entries?
- Does the choice of template follow from one criterion, that is whether the value is the same for the whole team - and not from the fact that the entry is a secret? The private template is not the place for every secret, only for the one under which everyone acts with their own account.
- Did no address, host, login or secret of the target environment end up in code, documentation or a template?
- Was the new secrets file, if one was created, covered by a rule in `.gitignore` and added to the read block in `.claude/settings.json`?
- Do the environment files remain free of comments?
- Does the secret stay out of the log, the error body and the exception message?
- Does the configuration file remain free of logic and of side effects other than reading the environment?
