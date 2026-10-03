# Error handling standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

An error without an established reaction gets a random reaction - whatever the author happened to come up with in that one place. The effect is visible only from a distance: part of the code aborts the whole operation on an error in one record, part swallows the error and goes on with an incomplete result, and nobody can say which reaction is correct here, because nowhere is it written down how this is decided.

A service with a separate worker process has an additional reason: the same error means two different things depending on what triggered it. A permission refusal while handling a request is a correct response for the caller. The same refusal in a periodic task of the worker is a signal that the data is in a state nobody foresaw - and there is nobody to return it to.

## Scope and boundaries

This standard is responsible for: classifying an error, the reaction in the two execution contexts, mapping a domain error to an API response, the durable attempt counter and timeouts.

What is not here:

- the format for writing an error to the log and the question of whether to log it with a traceback - that is `standard_logging.md`;
- whether a retry will duplicate the effect - that is `standard_idempotency.md`; this standard says whether to retry, that one whether retrying is safe;
- the retry strategy for a single call to an external system - that is `standard_architecture.md`;
- specific API response codes and bodies - they are decided by the product specification pointed to in `CLAUDE.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## Three error classes

Caller error. The request is incorrect or not allowed: a missing field, a wrong format, a missing permission, an attempt at a state transition that the rules do not allow. This is not a failure - it is a normal, expected response. It is not logged as an application error and is not retried.

Transient error. A dropped connection, a transaction deadlock, temporary unavailability of a file resource. The same operation repeated a moment later has a reasonable chance of succeeding. Retrying is allowed, provided that the retry is safe according to `standard_idempotency.md`.

Permanent error. A state the code did not foresee: a violated invariant, data in a shape that is impossible according to the rules, missing configuration. Retrying makes no sense, because it will repeat exactly the same result. It requires recording and reporting, not hiding.

The classification is a decision of the code's author, not a consequence of the type of exception that happened to be raised. The same library exception can be transient or permanent depending on what triggered it.

## Reaction while handling a request

One request is one transaction and one result. There is no partial reaction here: the operation either executed in full or changed nothing.

A caller error is turned into a response describing what is wrong, in the shape set by the specification. The response contains no exception text, table name, query fragment or connection string - this is not theoretical caution, because exactly these channels leak the most information about the system's internals.

A transient error in request handling is not retried forever, nor for longer than the caller is able to wait. A conflict caused by concurrent modification of the same record is a special case: it goes back to the caller as information about stale state, and is not silently overwritten by a retry. A silent retry after such a conflict erases a change that nobody saw.

A permanent error means a failure response, a log entry with full context, and nothing more. There is no attempt to rescue the operation by guessing what the caller might have wanted.

## Reaction in a periodic task

A periodic task has nobody to return an error to, so its reaction is different: what matters is that one broken record does not block the others, and that the fact of skipping it does not disappear.

Three allowed reactions, chosen deliberately:

- continuation - the error concerns one element, the others are independent, so the element is skipped and recorded as skipped. The run ends with a result saying how many elements went through and how many did not;
- abort - the error undermines the point of the whole run (missing configuration, unavailable database), so the run ends without further attempts;
- degradation - part of the work is performed in a narrower scope, explicitly recorded in the log. Allowed only when the narrower scope is a correct state in itself, not a half-done one.

Continuation without recording the skip is not continuation, but silently losing work. A run that skipped half of the elements and ended as successful is worse than a run that crashed - because nobody will find out.

A periodic task that is supposed to alert about a violation reports it through the shared operational alert channel. The log always stays as well, because the alert may not arrive - and a failed delivery is to be recorded as failed, in the run details and in the log. Pretending that the notification arrived is not allowed in either of these two places.

A failure of the whole run is connected to the same channel from the wrapper shared by the whole periodic task registry, so every periodic task alerts about it regardless of whether its own work reports anything. Adding another entry to the registry does not require adding an alert to its work, and an alert for a quality rule remains a decision of that work. The alert reason is part of the deduplication key, so a quality alert does not silence a failure of the same task within the same deduplication window.

## Durable attempt counter

An element that fails repeatedly cannot be retried endlessly on every run - because it takes time away from the following runs and clutters the log with the same error. An element retried between runs has a durable attempt counter with five components: the number of attempts, the error class, the error message, the moment of the first occurrence and the moment of the last one.

The threshold after which an element stops being retried is set per error class, not as one value for everything: a transient error deserves more attempts than a permanent one, which deserves none. An element set aside after exceeding the threshold is not deleted or hidden - it stays visible together with the reason, because the whole point of the counter is that someone can see it and decide.

## Timeouts

Every call that waits for something outside the process - the database, a file resource, a service - has an explicit timeout. No timeout does not mean that nothing will happen; it means that in case of a problem the process will wait until someone kills it, holding on to occupied resources it will not release.

The timeout value is deliberate and follows from how long the caller can wait, not from the library's default value. A periodic task has a timeout for the whole run, so that one hung run does not block the next one.

## Checklist

- Does every new exception handling block have a deliberately assigned error class, rather than a reaction that follows from the type of exception that happened to be raised?
- Is a caller error not logged as an application failure and not retried?
- Does the response body avoid containing an exception, a query fragment, a database object name or a connection string?
- Does a concurrent modification conflict go back to the caller rather than being silently overwritten by a retry?
- Is every reaction in a periodic task one of the three allowed ones, and was it chosen deliberately?
- Is a skipped element recorded as skipped, and does the run report the number of processed and skipped elements?
- Does an element retried between runs have a durable attempt counter with five components and a threshold per error class?
- Does an element set aside after exceeding the threshold remain visible together with the reason?
- Does every call waiting for something outside the process have an explicit, deliberately chosen timeout?
- Does the new periodic task have a timeout for the whole run?
