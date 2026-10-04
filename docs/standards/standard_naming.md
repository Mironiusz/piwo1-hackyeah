# Naming standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

A file name and a function name are the first information that someone searching for something in the repository gets - and the only one they see before opening anything. When the same responsibility is named in three different ways in three places, searching stops working: you have to know the history of the repository to know what to search for. This standard sets the target names so that this knowledge is not needed.

## Scope and boundaries

This standard is responsible for the naming conventions of files and functions.

What is not here:

- the registry of names actually present in the repository - that is `naming_registry.md`, which describes the actual state, not the target one;
- what exactly a given code layer does and what it does not do - that is `standard_architecture.md`, section Layer boundary;
- names in the database: tables, columns, indexes, constraints - that is `standard_database.md` and the product specification indicated in `CLAUDE.md`;
- path names in the programming interface - those are settled by the programming interface contract `docs/product/api_contract.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

## Language of names in code

Identifiers in code are in English: names of functions, variables, classes, constants, files, tests and fixtures. Docstrings, error messages, log content and all documentation are in English as well.

The reason is not aesthetic. Code mixes with names from libraries, which are English and will stay English - `logging`, `pytest`, the database access layer. A Polish function name standing next to an English name from a library forces jumping between two languages within one line, and with derived forms (plural, declension by case) it leads to names that are hard to predict when searching. The name `entries` is one; `wpisy`, `wpisow`, `wpisy_pliku` are three versions of the same concept.

Originally this rule covered only identifiers; docstrings, error messages, log content and documentation followed on 2026-10-03, when the team switched the repository to English because the Huawei challenge requires English project documentation - conversation with the user stays in Polish, see `CLAUDE.md`, section Language and communication style.

## Forbidden names

A file or function name must not be so generic that it says nothing about the content: `utils.py`, `helpers.py`, `misc.py`, `common.py` without a topic, `process_data`, `handle_items`, `do_work`, `manager`. Such a name is an invitation to throw in everything that had no better place - and a file into which everything fits has, after half a year, neither an owner nor a boundary.

A file with shared helpers is acceptable, but named after its topic, not after its function in the project: `common_dates.py`, not `common.py`.

## Function names: a verb that states the responsibility

The prefix of a function name says which responsibility the function belongs to. The four binding prefixes:

- `fetch_` - reading data from a source external to this function: a database, a file, a service. Reading only, without deciding what to do with the data.
- `build_` - assembling a value or a structure from data already at hand. No reading and no writing.
- `resolve_` - a domain decision: choice, classification, settlement based on rules. It returns the decision, it does not execute it.
- `apply_` - executing a decision: writing, sending, changing state.

The name `get_` is not used for reading from a source - `fetch_` is for that. `get_` can be misleading, because in many libraries it means cheap access to a value already held, not a database query whose cost is several orders of magnitude different.

A function whose name would require two prefixes at once does two things - that is a signal to split it, not to pick one of the prefixes.

## File names

The code unit is the layer. This determines the shape of names: the directory names the layer, the file names the responsibility inside that layer.

Layer directories sit in the repository root: `api` accepts requests, `service` holds the rules, `data` reads and writes, and `worker` triggers periodic tasks. The name of a file in such a directory says what it is responsible for in that layer, for example `api/errors.py`, `api/health.py`, `service/readiness.py`, `data/engine.py`.

There is no suffix with the layer name in the file name, and this is intentional. When the layer is the unit, the layer is the directory, and the file has nothing to repeat after the directory - `data/database_probe.py` is the same as `data/data_database_probe.py`, only shorter by the repetition. This is the reverse of the rule that would apply if the unit were a subdomain.

The name of a file with a helper shared by many layers has the reverse shape of a layer file name: the shared topic goes in as a prefix (`common_<topic>.py`). This distinction makes it possible to answer the question "can I change this without looking at the rest of the repository" from the file name alone. The two explicit places for cross-cutting knowledge within one layer and between layers are described by `standard_agent_docs.md` for durable memory and by this rule for code.

## Names of query constants

A constant holding a database query has a name of the shape `<VERB>_<WHAT>_SQL`. The order is the reverse of an `SQL_` prefix, because this way names sort by verb and topic, not by a shared prefix that distinguishes nothing.

## Names in tests

A test file is named after what it tests, plus the test layer. The test layer convention is in `standard_tests.md`, together with how the layered split of the code maps onto test directories.

A fixture may be named like the class it returns, breaking the function naming convention - this is explicitly allowed and excluded from the linter rules in `pyproject.toml`.

## Checklist

- Is no new file or function name so generic that it says nothing about the content?
- Does the prefix of each new function match its actual responsibility, and not how convenient it was to name it?
- Is there no new function that would need two prefixes at once?
- Does the new file sit in the directory of the layer it belongs to, and does its name state the responsibility inside that layer instead of repeating the layer's name?
- Does the new file with shared helpers have a topic in its name and a prefix shape, not a suffix shape?
- Does the new query constant have the shape `<VERB>_<WHAT>_SQL`?
- Were new names that this standard does not yet settle added to `naming_registry.md`, so that the next person does not invent them from scratch?
