# Testing standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

A test written without an agreed convention lands wherever it was convenient for the author and checks whatever was easy to check. After a few months this produces a collection in which it is impossible to answer the question whether a given rule is covered - you have to read all the tests to find out.

This standard defines where a test is to live and what it is to check, and explicitly lists the tests that are mandatory regardless of the project's domain.

## Scope and boundaries

This standard is responsible for: test layers and their naming, the locality of test configuration, coverage scope, markers, and the mandatory tests that follow from the risks in the specification.

What is not here:

- the architecture of the production code these tests are about, including the layer boundary and the direction of dependencies - that is `standard_architecture.md`;
- what exactly the tested logic is to do - that is the product specification pointed to in `CLAUDE.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## Test layers

Unit tests check one function or one rule in isolation, without a database, without the network and without the file system. They live in the directory corresponding to the path of the tested code, in files named after what they check.

The code unit is the layer, so the test directories mirror the layer directories: `tests/api/`, `tests/service/`, `tests/data/`, `tests/worker/`. Each of them tests the layer it names, and it may replace only what that layer calls - a test of the input layer replaces the endpoint's dependency, not a probe in the data layer. The split into directories is therefore the same split as the direction of dependencies between layers from `standard_architecture.md`: a test that has to replace something from two layers below says something about the code, not about itself. The project guards the direction of dependencies with an architecture test that it creates together with the first code of that layer; the template does not contain it.

Scenario tests check a rule on a set of input cases, including edge cases. The file has the `_cases.py` suffix. This layer is the right place for the cases that the specification describes with the words "unless" - they are the most common source of bugs.

Integration tests glue several layers together and have the `integration` marker. They do not use the real network or a real database - if a test needs one or the other, it belongs to a lower layer or gets the `critical` marker.

Programming interface tests check the behavior visible to the consumer: the response code, the shape of the response, a permission denial. They check the contract, not the implementation - a test that still passes after the response code changes from a permission denial to a validation error does not check the contract.

Infrastructure tests in `tests/architecture/` guard the rules of the repository itself, not the service logic. The template has gates for documents and agentic tools there: parity of both tool branches (`test_agent_docs_parity.py`), prose style in documents (`test_prose_style.py`), the plan document contract (`test_plan_document_contract.py`), no conflict markers (`test_conflict_markers.py`), the dangerous commands hook (`test_dangerous_commands_hook.py`) and the session start hook (`test_session_context_hook.py`). The project added the list of third-party content that the first two gates skip, `common_vendored_content.py`, guarded by `test_vendored_content.py` (`standard_agentic_workflow.md` ch. 6.1). Rules of the service code, for example the direction of dependencies between layers, the match between the environment template and reality or the consistency of periodic tasks, the project guards with an architecture test that it creates together with the first code of the given layer; the template does not contain it.

A repository rule that can be checked by a machine belongs to this layer, not to a separate command-line tool. The test goes into `make test`, through that into `make check` and through that into the Standard - verifying tool map in `standard_review.md`, so it runs by itself during implementation and during review. A separate target in the `makefile` has to be remembered to be called, and a rule that has to be remembered is not guarded.

Critical tests with the `critical` marker use real dependencies and are meant to crash the environment quickly when something does not work. They are not run in every run. A fast run without real dependencies excludes them with the expression `-m "not critical"`.

A critical test that seeds data with a durable write cleans up after itself. A durable write is necessary there when the called function opens its own connection and does not see the fixture's transaction, so a rollback is not enough. Cleanup goes through a shared fixture in `tests/conftest.py`: before the call, the test registers in it the natural key of the seeded row or, when the test itself created the row, its identifier. After the test, the fixture resolves the keys into identifiers and deletes the registered rows together with the rows that point to them. When the foreign keys have no `ON DELETE`, the deletion order is part of the fixture. Deletion goes only by the registered keys, never by a name pattern.

A critical test may write and runs a durable seed, so it always goes against the local database. A session with a critical test refuses to start when the application configuration points to the target environment. This is done by the `pytest_collection_finish` hook in `tests/conftest.py`: after the collection is gathered, before the first test, it ends the session with code 4 (`pytest.ExitCode.USAGE_ERROR`) and a message built from constants, without any address. It reads the environment from the same configuration value by which the service code chooses the database. The hook also works during collection alone (`--collect-only`), so an IDE collecting tests in a copy configured for the target environment is also stopped. There is no workaround: a critical run against the target environment is never intended. The limitation of this safeguard is that it does not detect a wrong local address that points to the target server: the repository cannot know the target address, so there is nothing to compare it with. The project guards this rule with an architecture test that it creates together with the first critical test; the template does not contain it.

## Test configuration is local

The `conftest.py` file lives closest to the tests it concerns. A fixture needed in one directory does not go into the root `conftest.py`, because there it applies everywhere and after half a year nobody knows what turned it on or what will happen after it is removed.

A fixture that replaces anything global is confined to its own directory and reverts the change after itself.

## Ad hoc runs

The pytest configuration in `pyproject.toml` has `addopts = "-ra -q"`. A second `-q` given in the call adds up with the one from the configuration to `-qq`, which hides the summary line, so a green run cannot be told apart from an empty one. Run ad hoc runs with `-o addopts=-ra`, which overrides the options from the configuration.

## Mandatory tests

The product specification pointed to in `CLAUDE.md` explicitly names the places where it expects bugs. Each of them is to have its own test, named so that it is clear what it guards. These tests follow from the project's domain, so this standard does not list them.

Regardless of the domain, the tests below are mandatory.

Code that reads or writes the database has a critical test against a real database. A unit test and an integration test by design do not touch a real database, so a query checked only by them has never been executed on the server.

A repository rule that can be checked by a machine has a test in `tests/architecture/`, described in the section Test layers.

A round trip of a time value. Write a value with a specific zone offset, read it back and check that the offset is the same - not only that the instant is the same. A test comparing only instants will also pass when the driver layer silently normalizes everything to universal time, and then the offset preservation rule from `standard_time.md` cannot be fulfilled, although nobody will notice. This test comes first, before the code that relies on it.

Permissions and visibility, separately for the list and for the detail view. A matrix over all the roles the project defines, checking both what is allowed and what is not allowed. Checking only the positive side lets through the worst bug of this class, that is opening other people's data to everyone.

## Coverage scope

Coverage is not a goal in itself, but below a certain level it stops saying anything. Goal: every domain rule has at least one test checking its positive side and at least one checking that the rule actually refuses.

A rule whose test only checks that it works when it is allowed is not tested - the most expensive bugs are the ones where something passed although it had no right to.

Coverage is not enforced automatically today: the repository has no threshold in the configuration and no external run that would guard it. Enforcement stays on the side of the human and the review - this is a known debt, recorded in the standards map.

## What a test does not do

A test does not repeat the implementation to check whether the implementation does what it does. A test checking that a function called another function says nothing about correctness - it only says that the code is written the way it is written.

A test does not depend on the current date, unless it is checking exactly the time-dependent behavior - then the time is given explicitly, not taken from the system clock.

A test does not depend on the order of other tests or on the state left behind by the previous one.

## Checklist

- Does the new domain rule have a test for the positive side and for the refusal?
- Does the new test live in the layer that corresponds to what it actually checks?
- Does the integration test have the `integration` marker and avoid using the real network or database?
- Does a test requiring a real dependency have the `critical` marker?
- Does code that reads or writes the database have a critical test against a real database?
- Does a machine-checkable repository rule have a test in `tests/architecture/` rather than a separate command-line tool?
- Does the new fixture live closest to the tests it concerns, and does it revert global changes after itself?
- Does a change in `tests/conftest.py` keep the refusal to start critical tests under the target configuration?
- Does a critical test that seeds data with a durable write register it in the cleanup fixture before the call, and does cleanup go by the registered keys, not by a name pattern?
- Is a change touching writing or reading time values covered by a test checking that the offset is preserved, not only the instant?
- Does a change touching permissions or visibility have a test for the list and a separate one for the detail view, across all roles, in both directions?
- Does the test avoid checking only that one function called another?
- Does the test avoid taking the current date from the system clock without a reason?
