# Logging standard

Document state: 2026-10-03

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

Without an agreed rule, the log level is chosen inconsistently: the same kind of situation - an input data validation error without any exception and a real, caught exception - sometimes lands on the same `error` level, with no distinction between which of these two events requires further attention and which is a normal, expected rejection of bad data. A second, separate problem concerns logging the exception itself: in analogous error handling blocks one place logs the full traceback, and the neighboring one only the exception message as a string - without any rule as to which of these two forms is correct. A traceback lost at that moment does not come back later; the only record of the circumstances of the failure that we could ever have had simply was never created.

The third problem concerns the content of the entry, not its level or form. An identifier that unambiguously points to a specific person - first and last name, e-mail address - gets into the log too easily, because at the moment of writing the code it looks like an ordinary diagnostic field. "I'll only log it at debug" is no protection here if debug is what the runtime environment collects anyway. This is not a theoretical style risk - it is exposure of personal data in a place to which access is sometimes broader than access to the database those data come from.

This standard settles four questions: which log level corresponds to which situation; how to build the entry content so that it is readable and searchable; what data a log entry never contains; and how to log a caught exception so as not to lose the information needed for diagnosis.

## Scope and boundaries

This standard is responsible for:

- the meaning of each log level and the situation it is reserved for,
- the entry content format - the way the message is built,
- the entry contents - what data may, and what data may never, be placed in it,
- the way a caught exception is logged, preserving the information needed for diagnosis,
- the presence of an identifier linking the entries of one run when they span many modules.

What is not here:

- Where the logger comes from and how the central mechanism is configured - handlers, file rotation, routing entries to files per module group, the shared logger name hierarchy - that is `standard_architecture.md`, section Loggers. The sentence that settles the boundary: architecture says where the logger comes from and where the written entry goes; logging says what to write in that entry and how.
- The decision about what happens after an error - retry, aborting the run, degradation - that is `standard_errors.md`. Logging says how to record it, error handling says what to do.
- Where the values controlling logging are stored, such as the level configured for an environment - that is `standard_config.md`, in the environment variables layer. This standard says what a given level means and when to use it, not where its value lives.
- Generating and propagating the run identifier inside the worker as a mechanism - that belongs to `standard_worker.md`. Here there is only the requirement that such an identifier is part of the entry contents.
- Detecting a secret hardcoded directly in the source code - that is `standard_security.md`, the bandit static analysis. This standard guards a different moment: that a secret which is a value at program runtime, even one never written in code as a literal, does not get into the content of a log entry.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

A clarification specific to this standard: the obligation to adapt covers every log entry in a module touched by the change, regardless of whether exactly that function was the goal of the task - in particular replacing exception logging without a traceback with logging with the full traceback, and removing or masking personal data in existing log entries. Personal data logged directly is the only place in this standard where the usual deviation "I will fix it the next time I touch the module" is not a sufficient answer on its own - see section Data in the entry content.

## Log levels

`debug` is the level of detail useful when diagnosing a specific case, but unnecessary for understanding the normal run - the state of a single item in a processing loop, an intermediate value, a decision made by a condition. An entry at this level is not needed by anyone reading the logs in search of the general picture of what happened - it is needed only when you have to understand why one specific case behaved differently than expected.

`info` is the level of checkpoints of the normal run - start and end of a run, an aggregate summary of the number of processed items, confirmation of an operation that succeeded. An entry at this level does not carry the detail of a single processed item - that is the job of the `debug` level. A log made only of `info` entries is to give a readable, concise trace of what was happening, without scrolling through details that nobody cares about in a normal run.

`warning` is the level of degradation and transient situations, already described in `standard_errors.md`: a step that ran, but worse than usual, without aborting the run. This standard does not repeat that definition - it refers to it as the only source of when `warning` is the right level.

`error` is reserved for a situation in which an operation or a step actually failed - a caught exception or a violated condition that prevented completing that specific piece of work. `error` is not the level for an expected, handled rejection of bad input data, if that rejection is a normal, foreseen result of validation and not a failure - such an entry, if it is needed at all, belongs to `info` or `warning`, depending on whether the fact of the rejection itself requires someone's attention. This distinction is not a matter of style: the `error` level used for both situations at once takes away from the person reviewing the logs the ability to tell something that requires a reaction from something that simply happens.

`critical` is reserved for a failure after which the process or the run cannot continue in any form - not the next step or item, but the whole run. This is a narrower meaning than `error`: a step that failed, but after which the run could move on to the next step or finish with degradation, is `error`, not `critical`. A situation in which the process terminates abnormally before it has done anything useful is `critical`. This distinction makes sense only if `critical` is actually used rarely and consistently for this narrower situation - a level used interchangeably with `error` stops carrying additional information and becomes just another name for the same thing.

## Entry content format

The log message is built with the lazy placeholders of the logging mechanism (`logger.info("x=%s", x)`), never by interpolating into a string before the call (an f-string or `.format()` pasted into the message argument). A lazy placeholder postpones building the final string until the moment the entry is actually written at the configured level - a message assembled by an f-string is always built, even when the given level is disabled and the entry will be discarded anyway, which is an unnecessary cost repeated at every call regardless of whether anyone ever sees it.

This particular rule is the only one in this standard that is checked automatically: the `G` rule in `ruff check .`, listed in `standard_code_quality.md`, detects an f-string and `.format()` passed directly to a logger call. The rest of this document - levels, data content, exception logging - stays with review, because no tool today distinguishes an expected rejection of bad data from an actual failure, nor recognizes an identifier pointing to a specific person.

The message content describes the operation in words and attaches variable data in the form `key=value` through successive placeholders - for example the entity name, its identifier and the number of processed items, each as its own pair. This shape is searchable: finding in the log all entries concerning a specific identifier or operation does not require parsing free prose, only searching for the key name. An entry made of bare prose without separated pairs carries the same information, but makes it incomparably harder to find in a growing log file.

A log entry is not a dump of an entire data structure in one argument - neither a ready JSON string pasted in as the message, nor the result of `str()` on a complex object. The exception is an entry created explicitly as data for machine processing, not for reading by a human - such an entry is explicitly marked as something other than an ordinary narrative log and is not a pattern to copy when writing the next ordinary entry.

## Logging a caught exception

A log entry created inside a block handling a caught exception logs the full traceback, not only the exception message as a string. The logging mechanism has a dedicated method for this (`logger.exception(...)`, or equivalently `exc_info=True` with another method) - omitting it and logging only the exception content (`logger.error("...: %s", exc)`) behaves similarly from the outside, but loses the trace of where in the code and through what call path the exception actually originated. That trace cannot be reconstructed later - it is available only at the moment when the exception is still caught, and only when the one doing the logging asks for it.

Logging without a traceback is acceptable only when there is no longer a live exception to log at that place - for example an entry reconstructed from the durable attempt counter described in `standard_errors.md`, where what gets logged is the error class and content read from the database, not the exception object itself from the moment it occurred. In such a case the entry carries at least what the durable attempt counter has to store anyway - the error class and its content - so as not to be limited to the bare fact that "something failed" without any detail.

## Data in the entry content

A secret - a password, an API key, a token, a connection string - does not get into the content of a log entry in any form and at any level, regardless of whether it exists in code as a literal or only passes through a variable at program runtime. This complements the rule from `standard_security.md`: static analysis detects a secret hardcoded in code, but does not detect a secret that was never a literal and only got into the log content as a runtime value - for example a token read from an external system's response and written to the log while debugging an integration. The only protection against this second case is this rule, enforced while writing and during review, not any automatic tool.

An identifier that unambiguously points to a specific person - first and last name, full e-mail address, phone number, an employee's external identifier - does not get into the content of a log entry in full form. When the log really has to refer to such an identifier for diagnosis to be possible, the entry refers to it through a masked form (for example a few trailing characters) or through an internal, technical identifier (a database key, a record identifier), not through the full value. The masked form is enough to link the log entry to a specific, known record by a person who has access to that record from another side, for example from the database, and at the same time it does not turn the log file itself into a second source of personal data, with a separate, weaker set of access safeguards than the database those data come from. The identifier of a person's account assigned by an external identity provider, for example `sub` from a token, is an external identifier and goes into the log only masked.

An external system's response, logged on an integration error, is not logged in full as a raw dump of the response body. The response content of a system we do not control can carry arbitrary content - including fragments of personal data or content that should not end up in the log file just because it happened to be in the error response. The entry carries the status code and a deliberately chosen, limited set of fields from the response, not the whole.

This rule has no transition period here and is not subject to relaxation for legacy code, once such code appears. The reason: personal data written to the log is an active risk from the moment of writing, not a cost deferred to the next change, and a log entry cannot be reverted the way a code change can.

## Run context

Every request gets an identifier in the input layer, sanitized and attached to the content of every log entry related to that request, in the same `key=value` pair that section Entry content format above talks about. Thanks to this, all entries concerning one request, regardless of which layer wrote them, can be found with one search by the shared value.

The mechanism lives in `config/logging.py`, not in the input layer: that is where the context variable holding the identifier lives, along with the filter inserting it into every entry, the pair of entry points through which the input layer sets and resets this value, and the scope manager for places that log outside the request context. That last one is not a convenience: the framework registers the handling of an uncaught exception higher than the middleware assigning the identifier, so that handling runs after the value has already been reset, and without explicitly setting the scope the entry with the call trace could not be linked to the response the caller received. The reason is architectural - a log entry from a probe in the data layer is to carry the same identifier, and that layer has no right to know that a request exists (`standard_architecture.md`, section Layer boundary). The value originates in the input layer: it is copied from the `X-Request-Id` header when the caller provided it and when it passes sanitization, and otherwise it is generated. An entry outside a request - at process startup and in the worker - gets the `-` character in this field, so that the format does not fall over on a non-existent field.

Sanitization means a specific rule here, not general caution: only a value made of alphanumeric characters, hyphens and underscores, no longer than 128 characters, is let through. A value outside this set is replaced with a generated one, not truncated - the header comes from the caller and ends up in every log line, so a newline character in it inserts into the log an entry that looks like an entry of the service.

A run of a worker periodic task that touches more than one layer is to get the same kind of identifier, attached to the content of the log entry in every place this run touches - not only where the run starts. Without a shared identifier, entries concerning one specific run, written by different modules, can be linked only after the fact, by guessing from similar write times - which in a log covering many parallel or frequent runs is not a reliable method. The mechanism for generating and propagating such an identifier inside the worker is the topic of `standard_worker.md`; this standard only requires that such an identifier, once it exists, gets into the content of the log entry.

## Checklist

- Does the `debug` level carry only detail that is not useful for understanding the normal run, and not a run checkpoint?
- Does the `info` level carry checkpoints and summaries, not the detail of a single processed item?
- Is the `error` level reserved for an actual failure of an operation or a step, not for an expected, handled rejection of bad data?
- Is the `critical` level used only for a failure that prevents continuing the whole process or run, not for a failing step?
- Is the new log message built with the lazy placeholders of the logging mechanism, never with an f-string or `.format()` pasted into the argument?
- Is the variable data in the message attached as `key=value` pairs, and not as free prose or a dump of an entire structure?
- Does an entry created inside a block handling a caught exception log the full traceback (`logger.exception` or `exc_info=True`), not only the exception message as a string?
- Is the entry content free of secrets - password, key, token, connection string - regardless of whether they come from a literal or from a runtime value?
- Is the entry content free of identifiers that unambiguously point to a specific person in full, unmasked form?
- Does an external system's response logged on error carry the status code and selected fields, not the whole raw dump of the response body?
- Does a run touching more than one module carry a shared identifier in the log entry content of each of these modules?
