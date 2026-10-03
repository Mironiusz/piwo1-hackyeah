# Idempotency and data reconciliation standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

The service accepts writes that by their nature can repeat: a client retries a request after a network error, a periodic task of the worker runs every minute and can be started twice, a batch import is fired a second time after an incident. Each of these repetitions is to have the same effect as the first execution - not a duplicated effect.

The risk is not theoretical and does not live in the network. It lives in the technique: a check in Python before the write - read whether the record already exists, and decide - is correct in a single, sequential run and lets a duplicate through when two runs of the same operation run into each other. Without one place that names this, the technique looks sufficient, because in tests it always is.

This standard settles three questions: what makes two executions "the same operation"; where the final protection against a duplicated effect lives; and how to choose between the available write techniques depending on the nature of the operation.

## Scope and boundaries

This standard is responsible for:

- the reconciliation key - what makes two executions the same logical operation,
- the place of the final protection against a duplicated effect,
- the choice of write technique (upsert, dedup) depending on the nature of the operation,
- the idempotency of a call to an external system, when that call can be retried.

What is not here:

- Data access, query structure and the database connection - that is `standard_database.md`. The sentence that settles the boundary: the database standard says how to reach the data, idempotency says how not to duplicate the effect.
- The decision whether and when to retry an operation after an error, the durable attempt counter, timeouts - that is `standard_errors.md`. The settling sentence: errors say whether to retry, idempotency says that the retry is safe once the decision to retry has been made.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

A clarification specific to this standard: a new write mechanism that can be called more than once for the same logical operation - through a retry, a second scheduler run or a manual resend - has duplicate protection from day one. It is not acceptable to add it "without dedup for now, we will fix it after observing duplicates in production" - this reverses the order in which this problem should be solved.

## Reconciliation key

The key that makes two executions the same operation is a deterministic function of the business identity of that operation - not of a technical identifier assigned at execution time, such as an auto-increment value or a random identifier generated anew on every attempt. Two independent executions of the same logical operation must compute an identical key - otherwise "reconciliation" has no point of reference and comes down to guessing whether a given write has already happened.

The convention adopted in this repository: the column carrying such a key is called `idempotency_key`, and its value is a hash (SHA-256) of the operation's business identity fields - the operation type and the identifiers of the entities it concerns, together with every other field that distinguishes this operation from another, logically different one. A change of one of these fields is a change of the operation's identity and is to give a different key; re-executing the same operation is to give the same key as the first execution.

A manual resend of an operation after an incident may and should carry its own, new attempt tracking identifier - to tell which of several manual attempts it was - but the final write of the effect still goes through the same reconciliation key as an automatic retry of the same operation. The tracking identifier answers the question "who tried and when"; the reconciliation key answers the question "does the effect of this operation already exist".

## Backstop against duplicates

A check in Python before the write - reading whether the record already exists, and on that basis deciding to insert or update - is an optimization, not protection. Two parallel runs of the same operation can both pass this read before either of them manages to write, and both conclude that the record does not exist yet. The final protection against a duplicated effect lives in the database, in one of two ways:

- a unique constraint or unique index on the reconciliation key - the database itself rejects a second write of the same key, and the code catches this conflict and treats it as an "operation already performed" signal, not as an error to report further;
- a transaction with a lock - `SELECT ... FOR UPDATE` on the row that represents the window, or an advisory lock (`pg_advisory_xact_lock`) when there is no row to lock yet - checking existence and performing the write atomically in one step. Used when the write itself is not a permanent state but a time window, see the section below.

Code that reacts to a uniqueness conflict instead of propagating it as an unexpected error does it correctly: such a conflict is not a situation described in `standard_errors.md`, it is an expected, correct result of concurrency - the backstop has just done what it was introduced for.

How to react to it is settled on PostgreSQL, not a matter of choice. A constraint violation brings down the whole transaction: the session enters an error state and no further statement in that transaction will execute. Catching the exception and continuing work, which is a correct pattern on other engines, would here require a `SAVEPOINT` around every such write - solely to keep the transaction alive. That is why the default form is `INSERT ... ON CONFLICT`: the conflict is then reported as a missing row in `RETURNING`, without an exception and without anything to roll back. `ON CONFLICT DO NOTHING` means "already exists, do not touch", `ON CONFLICT DO UPDATE` means "overwrite the state", and both are one statement that cannot lose a race. Catching the exception remains only where the conflict really is an error to report further.

## Two kinds of duplicate

A synchronization operation usually protects itself against a permanent duplicate: a record with a given business key, once written, is not to be created a second time, regardless of how much time has passed since the first write. The backstop for this kind of duplicate is a hard unique constraint in the database.

Notifications and alerts protect themselves against a different kind of duplicate - a windowed one: the same event reported a second time within a short time window is a duplicate and is to be silenced, but the same event reported after that window has passed is a new, legitimate report, not a duplicate of the old one. A hard unique constraint on the event key would block every subsequent, legitimate occurrence here forever - that is why the backstop for this kind of duplicate is different: the event key together with the moment until which the duplicate is to be silenced, checked and written atomically in one transaction with a lock, not through a physical constraint on the key itself.

The choice between these two kinds is a deliberate decision when designing a new mechanism, settled by one question: should a repetition of the same event after an arbitrarily long time still count as a duplicate of the old event, or as a new, independent event. A permanent mechanism applied where the event genuinely repeats over time will block every repetition forever after the first one; a windowed mechanism applied where the duplicate is to be permanent will let it through again after the window expires.

## Choosing the write technique

The right write technique depends on two characteristics of the operation: its size (a single record versus a batch) and whether an existing record is to be overwritten, or the data is only appended and a new entry never changes the previous one.

- Batch, append-only data: one `INSERT ... ON CONFLICT (key) DO NOTHING` statement for the whole batch. There is no temporary table and no anti-join - the conflict is resolved by the unique index, not by a query comparing sets, so there is also no window between the check and the write.
- Batch, overwritten state: one `INSERT ... ON CONFLICT (key) DO UPDATE SET ...` statement, not two steps, an update and an insert with an anti-join. `ON CONFLICT DO UPDATE` is one statement, so there are no two steps whose order can be mixed up.
- Single record: the same statement as above, with `RETURNING`, so that the code knows whether it inserted or hit an existing record. A read before the write remains only when the result of the read itself is needed for something else - never as a way of deciding about the write.

The common principle behind these three: the write and the conflict resolution are one statement, not a sequence into which something can squeeze. A mechanism written as a read and a decision for each row separately in Python is both slower and prone to a race - and the latter is more serious, because it does not show up in measurements.

## Idempotency of a call to an external system

A call to an external system that can be retried - through a retry after a network error or through a manual resend - passes a stable, deterministic operation identifier, computed the same way on every attempt, never generated anew (for example as a fresh random identifier) on every call. An external system that recognizes such an identifier and itself performs an upsert under it, rather than only creating a new object, recognizes the retry as a repetition of the same operation, not as a new one - the effect on the other side of the integration is not duplicated, even though the network call actually went out twice.

A call without such an identifier - one that creates a new object on the other side of the integration every time, regardless of whether the previous attempt already succeeded - has no protection against a duplicated effect on retry. This distinction matters in practice precisely on a timeout: a timeout that occurred after the request reached the external system and was executed there, but before the caller received the confirmation, is, from the caller's point of view, indistinguishable from a timeout that occurred before the request arrived at all. A retry after either of these two scenarios has a different, correct result only when the operation identifier is stable - otherwise the first scenario ends with two objects on the integration side instead of one.

## Checklist

- Is the reconciliation key a deterministic function of the operation's business identity, not of a technical identifier assigned at execution?
- Do two independent executions of the same logical operation - an automatic retry, a manual resend - compute an identical reconciliation key?
- Does the final protection against duplication live in the database (a unique constraint or a transaction with a lock), not only in a check performed in Python before the write?
- Does conflict resolution go through `INSERT ... ON CONFLICT`, rather than through a caught exception, which on PostgreSQL brings down the whole transaction?
- Is a uniqueness conflict treated as an expected "operation already performed" signal, not as an error to report further?
- For a windowed duplicate (throttling of repeating events), do the check and the write of the time window happen atomically in one transaction with a lock (`FOR UPDATE` or an advisory lock), not through a hard constraint that would also block a legitimate repetition after time has passed?
- Is the write technique - `ON CONFLICT DO NOTHING` versus `DO UPDATE` - chosen according to whether the state is to be overwritten, not according to the author's habit?
- Does a new call to an external system that can be retried pass a stable, deterministic operation identifier, not one generated anew on every attempt?
- Does the new idempotency mechanism have a test checking that two executions with the same input data give one effect, not two?
