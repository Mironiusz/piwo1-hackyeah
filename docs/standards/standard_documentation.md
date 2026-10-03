# Module documentation standard

Document state: 2026-10-03

Status: ready - a minimalist standard for documenting code units.

Terminology note: this document says "module" for the code unit you document. In the Python profile this unit is a layer from `standard_architecture.md` - `api`, `service`, `data` and `worker`. A project outside the Python profile records its own code unit here. This project records one: the code unit of frontend code is the whole frontend application in `frontend/`, and its pair of documents is `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md` (`standard_frontend.md`, section Code unit and documentation). The pair of documents is therefore created for a layer, not for a single file in it: `MODULE_ALGORITHM.md` describes the domain rules of that layer, `MODULE.md` its construction and the division of responsibilities between files. The word "module" stays in the text below, because it describes the same concept, and rewriting the whole document to "layer" would change only the vocabulary.

A layer that does not yet have a single domain rule does not get this pair up front. A behavior document without a single rule to describe and a construction document repeating the list of files visible from the directory tree are worse than their absence - they look like knowledge about the layer, but all they carry is its name. The condition for creating the pair is then written down explicitly in the durable memory of the layer (`agent_docs/memory/<layer>/_shared.md`), and that is where its decisions live until then.

Goal: module documentation is to quickly explain the behavior and the technical construction of the module. It is not meant to replace reading the code, it is not meant to be a runbook and it is not meant to repeat the same information in several places.

Formatting of the prose itself - forbidden characters, quotation marks only where they are needed for something, and the ban on bold in prose and on bold labels opening a paragraph - is in `standard_formatting.md` and applies to every document described below. The section templates in this standard give headings, not bold: if a fragment of documentation deserves to be set apart, it gets a heading.

---

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - documentation that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

This standard does not have the remaining core sections (scope and boundaries, checklist) - this is a known debt, recorded in the unresolved boundaries and debts section of `docs/standards/README.md`. The deviation rule must be in every standard of the set, without exception.

## Prose tone

Documentation is a contract for the person writing code, not a text to be read for pleasure. The prose is dry and matter-of-fact: a sentence names the mechanism directly, in a full declarative sentence, not in a broken-off fragment. No metaphors, showy phrases or punchlines that sell the content instead of delivering it - a flashy phrase costs the reader a round of decoding and adds no precision. The rationale stays, but in the form of a technical cause, not a punchline.

When rewriting the style of an existing document, no fact may be lost. The sets of identifiers in backticks, numbers, references to paragraphs and headings are compared before the change and after it.

## 1. Two levels of documentation

Every larger module should have two documentation files:

1. `MODULE_ALGORITHM.md` - a description of the module's behavior and domain rules.
2. `MODULE.md` - a description of the module's technical construction and the division of responsibilities.

The most important rule:

```text
ALGORITHM.md explains behavior.
MODULE.md explains construction.
```

We do not repeat the same information in both places. If a piece of information naturally belongs to one level, we do not duplicate it in the other.

`MODULE_ALGORITHM.md` should survive a refactor of file and helper names. `MODULE.md` does not have to, because it is a map of the current implementation.

---

## 2. `MODULE_ALGORITHM.md`

### 2.1. Role of the document

`MODULE_ALGORITHM.md` is for a person who wants to understand how the module works from the point of view of the process, the data and the domain rules.

After reading this file, the reader should know:

- what data enters the module,
- which domain concepts are needed to understand the process,
- what happens to the data, step by step,
- by which rules the result is produced,
- what is rejected, skipped, updated or saved,
- how reconcile, idempotency or deduplication works,
- which diagnostics and the most important summary counters may appear.

This document does not describe the file structure, the list of helpers, imports or instructions for developing the code.

### 2.2. Minimal structure

A standard `MODULE_ALGORITHM.md` should contain only these sections:

```text
# MODULE_NAME_ALGORITHM

Document state: YYYY-MM-DD

## Algorithm goal

## Domain concepts

## General process map

## Detailed run order

## Domain rules

## Reconcile and deduplication

## Diagnostics and summary
```

A section can be omitted if it makes no sense for a given module. We do not add extra sections without justification.

### 2.3. What a standard `MODULE_ALGORITHM.md` does not contain

By default we do not add the sections:

- `Document scope`,
- `Side effects`,
- `Run properties`,
- `Limitations of the current version`,
- `Example scenarios`,
- `How to test`,
- `How to develop`.

Such information can be added only when the module is genuinely incomprehensible without it or the user explicitly wants it. It is not part of the base template.

---

## 3. Sections of `MODULE_ALGORITHM.md`

### 3.1. Algorithm goal

Briefly describe what the module does with the data and what result is to be produced.

A good level:

```text
The algorithm imports signups from a web form and from a CSV file from a partner, normalizes them to a common model, splits them into active signups, signups awaiting confirmation and rejected signups, and then reconciles the result with the existing DB state.
```

Do not describe files, classes, helpers or implementation details here.

### 3.2. Domain concepts

Describe only the concepts needed to read the algorithm.

Examples:

- provider,
- source file,
- secondary source,
- normalized signup,
- bucket,
- reconcile key,
- conflict alert.

If a concept does not come back later in the algorithm, there is no need to describe it.

### 3.3. General process map

This is the most important section in `MODULE_ALGORITHM.md`.

`General process map` is a short, semantic version of the algorithm. It is not a list of keywords and it is not a list of function names.

Each point is to describe a specific data transformation or domain decision. A point may have 1-3 sentences, if one sentence would force a mental shortcut.

A good point should state at least some of these things:

- what range of data is taken,
- by which key the stage works,
- which condition decides whether to move on,
- what is produced after the stage,
- what is treated as context,
- what is deliberately skipped,
- what state of the data goes to the next step.

A bad level:

```text
1. Fetch the data.
2. Prepare the data.
3. Group the records.
4. Compute the result.
5. Save to DB.
```

A good level:

```text
1. For each provider, choose the input sources that are to enter the current run. Local files are chosen according to a time window since the last successful import, and fileless sources are included only when they have a complete configuration.

2. Convert all of the provider's sources to a common raw signup contract. A file and a web form may have different input formats, but after the adapter they are to be comparable as one stream of raw records.

3. Normalize the raw records to a common signup model. At this stage a unified e-mail address, the signup date, the source, the bucket classification and the auxiliary data needed for reconcile are produced.
```

Avoid empty verbs and qualitative judgments without specifics:

- fetch the data,
- prepare the data,
- build a window,
- group the records,
- compute the result,
- handle errors,
- save to DB,
- correctly,
- sensibly,
- good,
- better,
- appropriate.

They can be used only when a specific follows right away: a range, a key, a limit, a condition or an effect.

### 3.4. Detailed run order

This section expands the general process map, but it still should not be a book.

A good form:

```text
### 1. Choosing sources

A specific, natural and domain-oriented description. It indicates which data enter the stage, which conditions are applied and what goes further.

### 2. Normalization

A specific, natural and domain-oriented description. It indicates which fields are normalized, what is rejected and what data model is produced.
```

We do not enforce the `Input / Rules / Output / Diagnostics` form at every step. Such a format can be used only when it improves readability.

A step is worth splitting into smaller ones if:

- the description mixes several independent rules,
- the stage combines fetching data, a domain decision and saving,
- several diagnostic statuses appear,
- it is hard to write an unambiguous input and output.

### 3.5. Domain rules

In this section we describe only cross-cutting rules that are more important than the run order itself or that come back in several stages.

Examples of rules:

- classification,
- aggregation,
- scoring,
- matching,
- rejecting data,
- diagnostics,
- state transitions,
- protection against degradation,
- fallbacks.

A rule is to be specific and verifiable.

Weak:

```text
The web form is a better source than the partner import.
```

Better:

```text
If the existing e-mail address in the database comes from the web form, the module does not overwrite it with any address from the partner import. If the existing address comes from the partner import, it may be replaced only with an address from the web form and only within the configured time window since the signup.
```

### 3.6. Reconcile and deduplication

This section is mandatory only for modules that save durable state or reconcile data with an existing state.

Describe:

- the reconcile key or keys,
- when there is an insert,
- when there is an update,
- when there is a skip,
- whether an update changes key fields,
- how batch merge or deduplication works, if it exists.

A good level:

```text
The reconcile key for signups is `email + signup_date`.

No record in the DB means insert. A record that matches after normalization means skip. A difference outside the key means update by technical id.

An update does not change key fields.
```

### 3.7. Diagnostics and summary

This section is to be short. We do not turn it into a debugging runbook.

Describe only:

- the most important diagnostics,
- what goes to a separate table or summary,
- what misleading counters mean,
- whether a diagnostic stops the process or only describes it.

A good level:

```text
`rows_loaded` means the number of signups after normalization, not the number of rows in the input file.

A conflict alert is diagnostic. It goes to the conflicts table, but does not stop the import and does not change the reconcile result.

Fileless sources, e.g. the web form, do not increase the `files` counter.
```

---

## 4. `MODULE.md`

### 4.1. Role of the document

`MODULE.md` is for a person who wants to understand how the module is built technically.

After reading this file, the reader should know:

- what the public interface is,
- what the module reads and writes,
- what operating modes it has,
- what files exist,
- what each file is responsible for,
- what the main records are,
- which architectural decisions are important.

`MODULE.md` is not a second algorithm and it is not a step-by-step development guide.

### 4.2. Minimal structure

A standard `MODULE.md` should contain only these sections:

```text
# MODULE_NAME

Document state: YYYY-MM-DD

## Module role

## Public interface

## Technical inputs and outputs

## Operating modes

## File structure

## File responsibilities

## Main records and contracts

## Architectural decisions

## Summary

## Relation to MODULE_ALGORITHM.md
```

A section can be omitted if it makes no sense for a given module. The document should remain concise.

### 4.3. What a standard `MODULE.md` does not contain

By default we do not add:

- the full algorithm,
- the general process map,
- outlier diagnostics,
- example scenarios,
- limitations of the current version,
- development instructions,
- a debugging runbook,
- full record fields,
- testing, unless the module has an unusual test mode that one needs to know about.

---

## 5. Sections of `MODULE.md`

### 5.1. Module role

In 2-4 sentences describe where the module sits in the system, what it is responsible for and what it does not do.

A good level:

```text
`newsletter_import` is step 1 of the marketing pipeline. It imports signups from a web form and from a CSV file from a partner, normalizes them to a common model and feeds the tables of active, pending and rejected signups.

The module does not send welcome e-mails, does not compute campaign statistics and does not perform audience segmentation. These responsibilities belong to later steps of the pipeline.
```

### 5.2. Public interface

Briefly describe:

- the entrypoint,
- what `__init__.py` exports,
- what it returns,
- whether it accepts `deps`,
- whether other public functions exist.

A good level:

```text
The module exports only the `run_once()` entrypoint.
```

If the module needs more than one public entrypoint, you have to describe why. A public API should not come into being by accident.

### 5.3. Technical inputs and outputs

A list of technical sources and targets.

A good level:

```text
Inputs:
- the partner CSV file,
- the web form,
- the import of backlog signups,
- address validation rules.

Writes:
- the active signups table,
- the pending signups table,
- the rejected signups table,
- the file registry,
- the conflicts table.
```

Full names of tables, endpoints and folders must be here. We do not describe the full domain process here.

### 5.4. Operating modes

Describe only the real modes of the module:

- production,
- shadow,
- file pick mode,
- dry-run, if it exists,
- CSV, if it exists,
- degraded mode, if it exists.

Briefly and specifically.

### 5.5. File structure

Show the directory tree of the module.

Do not explain the algorithm here.

### 5.6. File responsibilities

This is the main section of `MODULE.md`.

Each file should have 1-2 sentences of description.

A good level:

```text
`newsletter_import_logic.py` - the orchestrator of one run. It ties together providers, normalization, reconcile, sinks, file statuses and cleanup.

`newsletter_import_records.py` - the typed data model of the module. It holds the raw, normalized, insert/update, existing DB, conflict and summary contracts.

`newsletter_import_helpers_reconcile.py` - the pure reconcile domain. It plans insert, update and skip based on payloads and a ready snapshot of the existing DB.
```

We do not add elaborate `May` and `May not` lists for each file. Exception: a place where the risk of an architectural mistake is high.

### 5.7. Main records and contracts

Describe only the most important records and their role.

Do not describe every field.

A good level:

```text
- `RawSignupRecord` - the common contract after the provider adapters.
- `NormalizedSignupRecord` - a signup after domain normalization.
- `ActiveSignupInsertRecord`, `PendingSignupInsertRecord`, `RejectedSignupInsertRecord` - write payloads per bucket.
- `ReconcilePlanRecord` - the insert/update/skip plan.
- `SignupRunSummary` - the result of the public entrypoint.
```

For difficult modules you can add a flow of models:

```text
raw source row
  -> RawSignupRecord
  -> NormalizedSignupRecord
  -> insert/update payload
  -> DB
```

### 5.8. Architectural decisions

This section is to be short and contain only the decisions that explain the construction of the module.

A good level:

```text
- Providers map sources to the raw contract, but do not classify the bucket in business terms.
- Reconcile is split into a pure domain and an I/O stage.
- The sink executes ready decisions and does not apply domain rules.
- `__init__.py` exports only the public entrypoint.
```

If a decision is a domain rule, its full description should be in `MODULE_ALGORITHM.md`.

### 5.9. Summary

Describe the summary type and the main groups of counters.

The full meaning of the counters, if it is domain-related, should go to `MODULE_ALGORITHM.md`.

A good level:

```text
`run_once()` returns `SignupRunSummary`, which contains a `ProviderRunSummary` per provider.

The most important counters:
- `files`,
- `rows_loaded`,
- `inserted_*`,
- `updated_*`,
- `skipped_*`.
```

### 5.10. Relation to `MODULE_ALGORITHM.md`

One sentence is enough.

A good level:

```text
This document describes the construction of the module. Behavior, domain rules and reconcile are described in `MODULE_ALGORITHM.md`.
```

---

## 6. Definition of Done for module documentation

We consider module documentation ready when:

- `MODULE_ALGORITHM.md` describes behavior without depending on the file structure,
- `MODULE_ALGORITHM.md` has a specific general process map, not a list of keywords,
- `MODULE_ALGORITHM.md` describes the detailed steps, rules, reconcile, diagnostics and summary,
- `MODULE.md` describes the public API, inputs, outputs, operating modes and file structure,
- `MODULE.md` clearly shows the responsibilities of the files,
- `MODULE.md` does not duplicate the algorithm,
- there are no contradictions between the code, `MODULE.md` and `MODULE_ALGORITHM.md`.
