# Code security standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

The service code connects to databases and external systems and processes personal data - a security bug in this place has a different cost than a style or performance bug, because its effect can reach beyond the repository itself. This standard states explicitly which class of vulnerabilities the code is to avoid and how to check whether external dependencies carry known security holes.

## Scope and boundaries

This standard is responsible for static security analysis of production code, for scanning the project's dependencies for known, publicly described vulnerabilities (CVE) and for handling real personal data in local environments.

What is not here:

- Dependency hygiene - a mismatch between declared and actually used packages, unrelated to security - that is `standard_code_quality.md`.
- The place and format for storing the module's secrets and configuration - that is `standard_config.md`. Here only the detection of secrets hardcoded directly in the code.
- Scanning for secrets in version control history - not covered by any standard of the repository.
- The proper way to write an SQL query, the database schema as the source of truth, migrations and the ban on triggers - that is `standard_database.md`. Here only the automatic detection of a deviation from parameterization.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

The dependency vulnerability scan works at the level of the whole repository, not a single module - a new vulnerability in an existing dependency can surface without any change in the code, just through the publication of a new CVE. The deviation rule still applies, in a narrower scope: a change that introduces a new dependency or raises its version is obliged to check that dependency, not to re-audit the whole dependency tree on every unrelated change.

## Static security analysis of code

The code passes static security analysis with the bandit tool without findings at high and medium confidence levels. Bandit detects, among other things: hardcoded passwords and keys written directly into the code, dangerous calls such as `eval` or launching processes with `shell=True`, and constructs vulnerable to SQL injection when queries are built by string concatenation instead of parameterization. A vulnerability detected statically and fixed before the change is merged costs one look at the code - the same vulnerability found after deployment, through an incident or an external audit, costs an impact analysis, notifying the affected parties and a fix under time pressure.

## Dependency vulnerability scan

The project's dependencies are scanned with the pip-audit tool for known, publicly reported vulnerabilities (CVE) before deploying a change that introduces a new dependency or raises its version. A dependency with a discovered vulnerability, used without awareness of that fact, brings into the repository a known risk documented in public databases - the difference compared to a vulnerability in our own code is that the way to exploit it is already described publicly, so the time between the publication of a CVE and an attempt to exploit it is sometimes shorter than the time needed to notice the problem manually.

## Real personal data in the local environment

Real personal data in the local database is allowed. This is a decision, not an oversight: diagnosing a production report on made-up data is sometimes diagnosing a different problem.

What follows from this permission is a rule, not the absence of one: the local environment stops being an environment without personal data, and the same rules apply there as anywhere else.

Three of them are concrete and verifiable:

- exporting anything from the local database outside the machine is forbidden. This covers pasting a query result into a ticket, into a conversation with an agentic tool and into any cloud document. A database schema dump is safe because it does not contain a single row of data, not because nobody looks there;
- the log level in a local environment with real data stays at `INFO` or higher. `DEBUG` combined with the rule from `standard_logging.md` turns every oversight in the code into data exposure, and locally nobody rotates or watches those logs;
- removing this data from the machine has one simple path and you have to know it before you need it: resetting the local database deletes the volume together with its contents. You do it before handing over the hardware and after the diagnosis is finished, not when someone asks.

## Checklist

- Does new or changed code pass bandit without findings at high and medium confidence levels?
- Are database queries built through parameterization, not through string concatenation with input data?
- Is the code free of hardcoded passwords, keys and tokens?
- Has a new or upgraded dependency been checked with pip-audit for known CVEs?
- Does a secret needed by new code go to the shared source of truth (`standard_config.md`) instead of being written directly in the code?
- Does the change avoid exporting the contents of the local database outside the machine - in a ticket, in a conversation with an agentic tool or in a file attached to a review?
- Does a change touching logging avoid raising log verbosity where personal data may pass through?
