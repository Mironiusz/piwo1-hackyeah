# Time and time zone standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

The service stores every point in time as a pair of columns: `timestamptz(3)` with the instant alone and `<column>_utc_offset_minutes` with the zone offset that was in force at the moment of writing. This pair answers two different questions - "which instant is it" and "what time did the person who entered it see" - and its whole value depends on both columns being written together. A half that was written is not missing data. It is a row that looks correct, has a valid instant and renders a wall-clock time that never existed.

The second reason is separate from the first: `timestamptz` stores neither a zone nor an offset. It normalizes the value to UTC on write and renders it in the session's zone on read. Code that does not know this writes correct queries and gets values that depend on the server configuration, not on the data.

This standard settles four questions: which time column type to choose for a new value; what exactly a value read from the pair means and how to write it safely; where to take "now" from on the database side and on the Python side; and how to compute day boundaries when the local day does not coincide with the UTC day.

## Scope and boundaries

This standard is responsible for:

- choosing the time column type in PostgreSQL for a new value (`timestamptz` versus `date`, and `timestamp` without a zone as a closed type),
- the semantics of the instant plus offset pair - what it stores, how to read and write it from Python through psycopg,
- the convention for the value "now" on both sides: `now()` versus `clock_timestamp()` in SQL, functions from one place instead of a bare `datetime.now()` in Python,
- day and month boundaries computed relative to local time in the time windows of queries and reports.

What is not here:

- The schedule of periodic task runs, run windows, locks and frequency - that is `standard_worker.md`. The deciding sentence: this standard says what a given time value means; the worker standard says when a task starts at all.
- A timeout on a call to the database or to an external system - that is `standard_errors.md`. This is a different sense of the word "time": there it is about how long to wait for a response, here about what a date value stored in the data means.
- The windowed duplicate in idempotency, that is silencing a repeated event within a short time window - that is `standard_idempotency.md`. There the window is a mechanism for silencing a duplicate, not a topic of time representation.
- The single way of opening a database connection and the general rule of one place of definition for a shared mechanism - that is `standard_database.md` and `standard_architecture.md`. This standard only names which zone option is to be set on such a connection and why; it does not establish the rule of a single point of definition itself.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

The narrowing specific to this standard concerns database columns: every migration that adds or changes a time column also covers its offset column. You cannot add an instant "without the pair for now" and come back to it later - the rows written in the meantime have nowhere to recover the wall-clock time from.

## Three time types in PostgreSQL and choosing between them

- `timestamptz` (`timestamp with time zone`) - the only type for a point in time. Despite its name it does not store a zone: on write it converts the value to UTC and remembers only the instant, on read it renders it in the session's zone. The precision is `(3)`, that is milliseconds, consistent with the format the programming interface exposes externally.
- `timestamp` without a zone - a naive date and time, with no information about which instant it refers to. A closed type for a new column. Reason: at a clock change one hour a year is genuinely ambiguous and nothing in the value itself says which of the two readings is meant. This type appears only as the result of an expression, not as a column: `created_at AT TIME ZONE 'Europe/Warsaw'` returns exactly a `timestamp`, and that is what reports need.
- `date` - a calendar date alone, without a time and without a zone. Appropriate where the value really is a day, not an instant. The requirement to provide an offset at the interface input concerns an instant, not a date - extending it to a `date` value starts rejecting valid requests.

On top of that, one domain shared by the whole schema:

```sql
CREATE DOMAIN utc_offset_minutes AS smallint
    CONSTRAINT CK_utc_offset_minutes_range CHECK (VALUE BETWEEN -840 AND 840);
```

The range from `-840` to `840` is the full range of real UTC offsets, from `-14:00` to `+14:00`. A value outside it is not a zone, but a bug in whatever computed it. The domain is the one place that says this for all pairs in the schema, instead of a condition repeated at every column.

So the choice for a new value is not a choice between types - it is a choice of whether the value is an instant or a day. An instant is always a pair: `timestamptz(3)` plus `utc_offset_minutes`. A day is `date` and nothing more.

## The instant plus offset pair: what it stores and why it is a pair

The `timestamptz` column stores the instant. The offset column stores the number of minutes of the UTC offset at the moment this instant was written. Together they reconstruct the wall-clock time the person saw: `2026-07-14T06:00:00+02:00` in July and `2026-01-14T06:00:00+01:00` in January, even though both instants are stored as UTC.

Consequence: two rows of the same column, written in different seasons, have different offsets, and that is correct, not a data error.

Why an offset and not a zone name. The programming interface receives an offset and only an offset as input - `+02:00` in July is Warsaw, Stockholm, Paris and a dozen or so other places. Storing a zone name would require guessing a fact the caller never sent, and that is exactly what `CLAUDE.md` forbids. Where a zone name is a real input, for example in a cron expression, it has its own column.

Comparison and sorting go by the `timestamptz` column alone. No `WHERE` condition, no index and no `ORDER BY` in the service reads the offset column - it is a fact about rendering, never about filtering. In particular, a report must not be grouped by the offset column: it says what the clock showed, not which zone the clock was in.

## Writing the pair: one value, not two columns

The pair is mapped as one attribute through `composite()` in SQLAlchemy. This is not a convenience, it is the only thing that makes writing half a pair impossible: since there is no attribute for the offset alone, there is no assignment that updates the instant and leaves the old offset. SQLAlchemy keeps a mapped attribute for every column of a composite, so the shared model of `db/accessibility_db/tables.py` maps the two columns of a pair under private keys starting with an underscore, which no code outside the model assigns.

The `CK_<table>_offset_pairs` condition in the database rejects a pair in which exactly one column is `NULL`. It will not catch, however, an offset left over from a previous write, because then neither column is `NULL`. That is why the defense has three stages, and each stage guards something different: `composite()` in the model does not allow writing such code, the condition in the database catches half a pair, and a periodic control task of the worker recomputes the offsets and reports the rows that no zone in use explains. The third stage exists for the case where someone writes raw SQL or a migration bypassing the model.

Code that writes an instant never computes the offset from the configuration "along the way". For a value provided by the client, the offset is whatever came in as input. For a value stamped by the server, it is the offset of the business zone at that moment, and the business zone comes from the configuration, not from a literal in the code or in the DDL.

The rule in the sentence above knows no exception for a write that was not triggered by a human. A write from a periodic run, from a synchronization with an external system, from seed data and from a test query is stamped the same way as a write from a command - with the offset of the business zone in force at the moment of writing. A zero written directly to mark a machine write does not mark anything: it is a valid universal time offset, so on read it cannot be told apart from a row really written in such a zone. An exception would therefore not be a marker, only the introduction of an unrecognizable value - and the same applies to any other conventional value inserted in place of the offset. The meaning of this column is one across the whole service, regardless of what triggered the write.

## Reading: a session pinned to UTC

psycopg decodes `timestamptz` to an aware `datetime` in the session's zone, not in the zone of the write - because there is no zone of the write in this column. An unpinned session means that the value on the Python side depends on the server's `postgresql.conf`, not on the data.

So every connection sets `options=-c timezone=UTC`, in one place, where the connection is created (`standard_database.md`). The `datetime` read back is then boringly predictable: always aware, always in UTC. The wall-clock time for a person comes from this instant and from the stored offset, never from whatever the session happens to be set to.

This is the first thing to check when timestamps come back shifted. The round-trip test checks it directly when it runs the read on a session deliberately set to a different zone.

## The time "now": on the database side and on the Python side

In SQL there are two functions and they differ in meaning, not in precision:

- `now()` returns the instant the transaction started and does not change during it. This is the default choice: all rows written by one command have the same timestamp, and a periodic task run evaluates all rows against one instant, so "overdue as of 03:15:00" is a true statement about the whole batch.
- `clock_timestamp()` returns the real clock at the moment of the call. Appropriate only where elapsed time is measured inside one transaction, for example how long a task run took.

Confusing these two does not produce an error, it produces a measurement equal to zero or a timestamp that only looks odd in the log.

In Python, the value of `datetime.now()` without a given zone is naive and depends on the operating system zone of the process that called it - not on anything visible in the code itself. The same call on a machine with a different system zone gives a different result for the same line, without any change in the repository.

The solution is two functions in one shared place, returning respectively the current instant in UTC and the current instant in the business zone, both as an aware value. Code picks one of them, matched to what the time is needed for: the UTC version for a technical timestamp, the local version where the value makes sense in relation to a day or a wall-clock time. Never a bare `datetime.now()`.

A naive `datetime` reaching the database session is a bug, not data, and it is caught in one place: a validator on the base Pydantic model plus an assertion in `before_flush`. An aware `datetime` in an unexpected zone, on the other hand, is data - the client has the right to send a deadline in its own zone and the service has the right to store it that way.

The only time zone library is `zoneinfo` from the Python standard library, not `pytz`. `zoneinfo` resolves daylight saving and standard time from the system's current IANA database, without its own, potentially outdated copy of zone data. Zone names are the same on both sides, because PostgreSQL also uses IANA names - this is the only reason why the schema and the code do not have two different notations for the same zone.

## Arithmetic on instants

Every addition and subtraction on an instant goes through UTC: convert to UTC, add or subtract there, convert back to the business zone and compute the offset anew.

Arithmetic directly on an aware value is not allowed. `aware - timedelta` in Python is wall-clock arithmetic and carries the original `tzinfo` over unchanged, so with `ZoneInfo` it can produce a local time the zone never had, or one whose offset is an hour out of date. Then the instant itself is wrong, not only the way it is shown - and only for windows that cross a clock change, which is exactly how such a bug slips through tests.

## Time windows in data: local day versus UTC day

The calendar day of the business zone does not correspond to the UTC day - its boundaries in UTC shift by an hour between daylight saving time and standard time. A window filtering "today", "yesterday" or "the last N days" cannot compute these boundaries as plain dates cast to `00:00`, because then it is shifted by an hour in one direction or the other, depending on the season, and systematically loses or adds records from the boundary hour.

On the SQL side the tool is `AT TIME ZONE` with an IANA name, and the result is a naive `timestamp` in that zone - exactly what you bucket by:

```sql
date_trunc('day', created_at AT TIME ZONE 'Europe/Warsaw')
```

The zone name comes from a query parameter or from the configuration, never from a literal copied into every report. For the `Europe/Warsaw` zone, the difference between the local day and the UTC day is everything that was written between midnight and two in the morning, so it is not a rounding error.

On the Python side, the window boundary goes through an aware `datetime` in the business zone and is converted to UTC only at the very end. Functions operating on plain `date` objects compute boundaries in the calendar, not in a specific zone - they are safe where the window goes into a query on a `date` column without a time component, or where the window is wide by design and a one-hour shift changes nothing.

## UTC values as keys

Wherever an instant is part of an identifier or an idempotency key, its UTC representation is used.

The reason is plainly visible at the autumn clock change: the local representation of the repeated hour `02:30` gives one and the same string for two different instants, so two separate records would collapse into one. A key must be one stable string per occurrence, and only UTC provides that.

## Checklist

- Is a new instant value a pair of columns: `timestamptz(3)` plus `utc_offset_minutes`, and not `timestamptz` alone?
- Is a new time column `timestamptz` or `date`, never `timestamp` without a zone?
- Is the pair mapped as one attribute through `composite()`, without a separate attribute for the offset?
- Does a table with a new pair have the `CK_<table>_offset_pairs` condition?
- Does no `WHERE` condition, index or `ORDER BY` read the offset column?
- Does no report bucket by the offset column instead of by `AT TIME ZONE`?
- Does the offset of a value provided by the client come from the input, not from the configuration?
- Does the offset of a server-stamped value come from the business zone also for a machine write - periodic, synchronizing, seed and test?
- Does the database connection set `timezone=UTC` in the single place in force?
- Does the choice between `now()` and `clock_timestamp()` follow from the meaning of the value, not from habit?
- Does new code use the "now" functions from one shared place, not a bare `datetime.now()`?
- Does new time zone code use only `zoneinfo` and avoid introducing `pytz`?
- Does arithmetic on an instant go through UTC, with the offset computed anew after it?
- Does a window filtering a day on a column with a time component compute its boundaries in the business zone, not from a plain calendar date?
- Is an instant used as a key or identifier rendered in UTC?
