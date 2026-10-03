# Database standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

The database is the only thing in this service that cannot be released again. Code can be rolled back to the previous version in a minute; a column deleted together with its data is restored from a backup, if someone had one. This asymmetry is the reason why the rules concerning the database are stricter than the rules concerning code.

The second reason is specific to this service: the database belongs exclusively to it. Nothing else reads it or writes to it, and this is a deliberate decision on which the ability to release and replace this service separately rests. A rule that violates this privacy costs much more than it looks.

## Scope and boundaries

This standard is responsible for: separating the source of truth about the schema from the dump of the actual state, the form of schema changes, the privacy of the database, the ban on logic in the database, data access and writing queries.

What is not here:

- the shape of specific tables, columns, indexes and constraints - decided by the product specification pointed to in `CLAUDE.md`; this standard does not repeat them, so that a second source of truth does not arise;
- the choice of time column type and the semantics of the zone offset - that is `standard_time.md`;
- whether a repeated write will duplicate data - that is `standard_idempotency.md`;
- query timeouts - that is `standard_errors.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## Two different documents about the schema and why they must not be confused

The source of truth about what the schema is supposed to be is the repository code: the model definitions and the schema change history. This is the only place whose editing changes the database.

The database schema dump is a picture of the server's actual state - of what really is in the database, together with the date the dump was taken. The dump is produced by a machine, is not to be edited by hand and changes nothing. Editing the dump file does not change the database, it only spoils the only place that tells the truth about the server.

The difference between these two is information in itself: it means that the database has drifted away from the repository. This is not a dump error to correct - it is a discovery to explain.

Before anything that touches a table or a column, you open both: the product specification says how it is supposed to be, the schema dump says how it is.

## Form of schema changes

Every schema change is an Alembic revision and there is no second allowed form. A manual `.sql` file executed on the database, a change made in a graphical client, an `ALTER TABLE` pasted in during an outage - these are not variants of the same thing, but changes that the repository does not see. The database then drifts away from the repository in a way we only learn about at the next dump, if someone takes one.

Revisions form a linear chain. There are no branches and no two revisions with the same predecessor - the order of application is to be single and visible from the file names.

The content of a revision is raw SQL in `op.execute`, one statement per call. We do not use `op.create_table` or generating revisions from models. The reason is practical: reviewing a revision is a line-by-line comparison with the DDL written in the product specification, not reading a translation into the library's interface. The second reason is stronger: generating from models silently omits, without a trace, the objects on which the schema invariants rest - the zone offset domain, the `NULLS NOT DISTINCT` clause, the check conditions on document structure, the `INCLUDE` lists and the partial index conditions. The migration goes through cleanly and produces a schema without that one index that made a duplicate impossible.

SQL inside a revision has no line comments. The explanation lives in the revision's docstring, in English, and says what this revision adds and why exactly at this place in the chain. We also do not add `COMMENT ON` to database objects: the justifications are in the product specification, and a second copy of them in the database would drift away from the first.

Permissions are granted in revisions, not in a script belonging to the local setup. The schema dump omits permissions, so revisions are the only place in the repository that answers the question of who can do what in the database. The script creating the database and the accounts keeps to what a revision cannot do: the database itself and the accounts themselves.

Default privileges cover only objects created after they are set, and only by the same role in the same schema. That is why the target state is additionally recorded by an explicit grant on all objects. This is not a belt-and-braces measure in case of a mistake: the schema version table is created by Alembic itself before it executes the content of the first revision, so default privileges set in that revision do not cover it.

Revisions of the initial database setup have no downgrade - they raise a refusal with a message pointing to the correct path. The supported way of reverting such a bootstrap is recreating the database, and functions dropping the schema would be destructive code that nobody will run and nobody will test. Every revision created later is to have a normal downgrade.

A narrow exception is a later revision that irreversibly merges or splits namespaces, when a faithful downgrade would require keeping a dead copy of the deleted data solely for the purposes of the downgrade. Such an exception must be explicitly resolved in an accepted plan, stop `downgrade()` with `NotImplementedError`, point to restoring from a backup as the supported path, and have a test or a deployment rehearsal confirming the refusal. It does not cover a migration whose reversal is merely laborious.

Alembic does not detect editing of a revision that has already been applied. After every fix in the content of an existing revision, recreating the database from scratch is required, not re-applying. The only thing that catches such a drift after the fact is a comparison with the dump of the actual state - which is one of the reasons this dump exists at all.

A schema change never happens on its own at environment startup, neither locally nor on the server. It is always a human decision, invoked with a separate command.

Before a proposal for a new table, or for a second entity next to an existing one, is made, the cardinality of the relation is checked. A one-to-one relation is a column on the existing row, not a side table. When the reason for a new entity is that a run or a query has to filter by something, the answer is a column.

## The database is private

No other system reads or writes this database. Information the service needs from outside arrives through its own interface, with one narrow exception: the read-only sources named in the product specification, which the service reaches for itself. Writing to a third-party database is forbidden without exception. The read boundary for a source that is an HTTP service rather than a database is in `standard_architecture.md`, in the section about calls to external systems.

Practical consequences that are easy to violate in good faith:

- you do not add a view or procedure "for reporting" on the database side so that someone from outside can conveniently query it - this turns a private database into a shared interface without a contract and without versioning;
- you do not add a column for the needs of another system;
- you do not accept a write from outside, not even a one-off, not even a manual one.

Checking co-ownership before changing an object stops making sense as a question about other systems, but remains as a question about the layers of this service: is this object read by a periodic task, by a list read, by a report.

## No logic in the database

Domain rules live in code, not in the database. Triggers are not added, and procedures and functions contain no domain decisions.

The reason: a rule in a trigger is invisible to a person reading the code, does not go through code review, has no test, and cannot be invoked or checked locally. A record changed by a trigger looks like a record changed for no reason, and the search for the cause starts in the code, where the cause is not.

Integrity constraints are something else and are required: foreign keys, uniqueness, value correctness conditions, domains over a recurring range of values, and constraints checking the document structure in a document column. They do not make decisions - they do not allow writing a state that has no right to exist. The backstop against duplicates must live in the database, not only in code that checks before writing, because two parallel runs will check at the same time and both will pass (`standard_idempotency.md`).

The boundary lies in how much such a condition knows about the domain. Checking that a document has an array under a fixed key, or that a discriminator column matches a field in the document, is integrity - nothing is decided, and a nonsensical state cannot be written. Checking whether a document field is required, or whether its value falls within a range stored in the record's configuration, is already a domain rule and lives in code. A document type with native JSON validation does not move this boundary - it only removes the need for a separate condition for syntax correctness alone.

## Data access

One way of opening a connection in the whole repository, from one place. Code that opens a connection its own way bypasses everything that this one place sets up - including pinning the session zone to UTC, without which the time values read depend on the server configuration, not on the data (`standard_time.md`).

Values go into a query only as parameters. Building a query from text fragments containing data is forbidden without exception - also where the value "surely" comes from a safe source, because that assumption stops being true at the first change of the caller.

A query lists the columns it needs. `SELECT *` binds the code to the current shape of the table in an invisible way: adding a column changes the result of a query that nobody changed.

A read returns data in a typed structure, not in raw rows passed on by position. Code that indexes the result with numbers breaks when the column order changes and does not say what it reads.

One domain operation is one transaction. This applies directly to API commands: each of them is one transaction and guards its own invariants itself. A sequence of writes that must succeed as a whole is not executed as several independent transactions in the hope that they all go through.

## Queries in code

A query in a constant has a name in the shape `<VERB>_<WHAT>_SQL` (`standard_naming.md`).

Dictionary identifiers are not written directly into code. Dictionary values are mapped as enumerations, and the logic uses these enumerations, not numbers. A number written into a condition is correct until the day someone changes the dictionary contents.

Text columns carry the full character range, because the content is in Polish. On PostgreSQL this follows from the database encoding (`UTF8`), not from the choice of type - `varchar(n)` and `text` store the same thing, and the width is a documented length limit, not a decision about the character set.

The collation is a separate decision, and it is not the default one. The database is created with the builtin locale provider and the locale `C.UTF-8`, which means comparison and sorting go by bytes: deterministically, quickly, and in a way that lets an index be used for prefix matching.

The choice of provider, and not just `LC_COLLATE = 'C'`, is the essence here, because collation and character classification are two different matters and both are needed at once. `LC_CTYPE = 'C'` on its own gives byte comparison and at the same time takes away from `lower()` its knowledge of the alphabet: `lower('ŁÓDŹ')` returns `ŁÓDŹ`, so searching by a name fragment stops working for every surname with a Polish character. The builtin provider separates these two matters: comparison stays byte-based, character classification understands UTF-8. It requires PostgreSQL 17 or newer; on an older server the same effect is given by the libc provider with `LC_COLLATE = 'C'` and `LC_CTYPE = 'C.UTF-8'`.

These parameters are irreversible once the database is created: changing them requires rebuilding every index on a text column or setting up the database from scratch. That is why they are checked by behavior, not by declaration - with a critical test on values with Polish characters, not on plain ASCII.

The consequences need to be known, because they are visible to the user. Text comparison is case-sensitive, so the uniqueness of a dictionary code is too - normalizing codes to upper case happens at the API input, not in the database. Polish sorting does not come out of the database and belongs to the presentation layer. Searching by a name fragment goes through `lower()` and an expression index, in one place for all such searches, not through a case-insensitive collation - the latter rules out the use of `LIKE`, which is exactly what the search is needed for.

## Checklist

- Was the change touching a table or column preceded by opening the product specification and the schema dump?
- Does the change avoid editing the schema dump files by hand?
- Was the drift between the dump and the models explained rather than ignored?
- Before proposing a new table, was the cardinality of the relation checked, and did a one-to-one relation go into a column on the existing row?
- Does the change avoid opening the database to another system through a view, a procedure or a column added for its needs?
- Does the change avoid writing to a third-party database?
- Does the change avoid introducing a trigger or a domain decision on the database side?
- Does the backstop against duplicates exist in the database, not only in code that checks before writing?
- Is the connection opened using the only approved way?
- Do all values go into the query as parameters?
- Does the query list columns instead of using `SELECT *`?
- Does the read return a typed structure rather than raw rows indexed by position?
- Does one domain operation execute in one transaction?
- Do dictionary identifiers come from enumerations rather than from numbers written into code?
- Does the new text column have a documented length limit, or deliberately none?
- Does a new search by a text fragment go through `lower()` and an expression index, not through collation?
- Does a new constraint on a document column check structure, not a domain rule?
- Does the schema change take the form described in the section about the form of schema changes: an Alembic revision, raw SQL, in a linear chain?
- Was the new database permission granted in a revision, not in a script belonging to the local setup?
- After editing an already applied revision, was the database recreated from scratch rather than updated?
