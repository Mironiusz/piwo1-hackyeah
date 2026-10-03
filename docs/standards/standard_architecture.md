# System architecture standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

Code that does not belong to one specific unit - because it is shared infrastructure or a mechanism that cuts across many places at once - has no natural owner, so decisions about it are made separately and quietly drift apart. This standard gives them a common point of reference.

The second reason concerns cross-cutting rules, that is rules called from many places, such as permissions and read visibility. A rule called from many places has one source, because two copies drift apart silently: it fails without an error when someone recreates its condition in an endpoint instead of calling it. This standard sets a rule for them before the first endpoint exists.

## Scope and boundaries

This standard is responsible for the architectural style above a single code unit: the service layer boundary, one place for cross-cutting rules, shared helpers, loggers, cache, library consistency and calls to external systems.

What is not here:

- the internal architecture of a single layer, that is the split of responsibilities between the files in its directory - the set of standards has no separate document on this topic;
- the format, levels and content of a log entry - that is `standard_logging.md`, here only where the logger comes from;
- what happens after an error - that is `standard_errors.md`;
- the location and format of configuration - that is `standard_config.md`, here only the requirement of one source of truth;
- who exactly has which permissions - that is decided by the product specification pointed to in `CLAUDE.md`, here only the rule about where this knowledge lives.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## Layer boundary

The service has three layers with separate responsibilities.

The input layer accepts the request: it validates its shape, establishes who is acting, and translates the result into a response. It contains no domain rules. An endpoint that checks a domain condition on its own violates this boundary - even when the condition is a one-liner, because a one-line condition is exactly what someone will copy into a second endpoint when it is needed a second time.

The rules layer decides what is allowed and what will happen. All state transition conditions, permissions and domain validation live here. This layer does not know that it was called from a request - the same call must be correct when made from a periodic task of the worker.

The data layer writes and reads. It does not decide whether a write may be performed.

The dependency direction is one-way: input calls rules, rules call data. The data layer does not know that the input layer exists.

## One place for cross-cutting rules

A cross-cutting rule, that is one called from many places - for example the permission matrix or the read visibility predicate - lives in one module and is called, never recreated.

A rule called from many places has one source, because two copies drift apart silently. It is easy to make a change in one place and not make it in the other - and then both behaviors coexist, depending on which call you happen to hit. A condition computed in two places from two different data sets will drift apart at the first change of the rule.

Practical consequence: the listing query and the detail query use the same visibility predicate, not two similar ones. If they differ for performance reasons, this difference is explicit, described and covered by a test on both sides.

## Shared helpers

Infrastructure code used in more than one place - database access, building configuration, shared clients - has one place of definition that everyone uses. Its logic is not copied, not even in a small, improved version. When the same mechanism exists in two places, a fix in one will not reach the other, and the users of the same mechanism start to differ silently - until the day when precisely the copy that was not updated fails.

When a shared helper already exists, using it is mandatory. Manually recreating its logic at a lower level - by calling the raw library mechanism - is allowed only when the helper genuinely does not cover the given case, never for convenience. A partial recreation, missing one of the helper's safeguards, creates a silent exception to a rule that applies everywhere else.

Secrets and configuration data have one source of truth - see `standard_config.md`.

## Loggers

The repository has one central mechanism for providing a logger, shared by all layers and both process entry points. No place configures its own parallel logging mechanism next to the central one - neither its own handler nor its own global configuration call. A parallel mechanism means that those logs end up somewhere other than the rest, and when diagnosing a failure, exactly that one, unpredictably silent part of the picture is missing.

The logger always comes from this mechanism, with a name in one shared hierarchy whose root is the project name. A logger outside this hierarchy does not inherit the central configuration, even when running in the same process.

A deliberate fallback for working outside the full application environment is allowed, but it must be explicit and narrow - limited to the situation where the central mechanism is unavailable, not to every possible import error.

## Cache

Every cache shared between calls has an explicit invalidation strategy: a time to live, a comparison with the source or an explicit invalidating call. Having no strategy at all is allowed only when the source data genuinely does not change during the lifetime of the process - and this assumption must be written down, not implicit. A cache without invalidation does not break loudly: the system keeps working, only drifting further and further from reality, and the symptom appears far from the cause.

A cache never stores the result of a failed attempt as a value to return. A remembered error turns a one-off failure of the source into a permanent failure of the functionality until the process restarts - the exact opposite of why the cache exists.

The lifetime scope of a cache is a deliberate choice matched to how the data is shared, not a consequence of where it was convenient to put the variable. Too wide a scope leaks stale data between independent units of work; too narrow a scope only shifts the cost onto the database it was meant to relieve.

## Library consistency

For a given kind of problem - database access, handling time and zones, data validation and representation, communication with an external system, retrying operations - the repository maintains one tool. A second, parallel way of solving the same problem is not introduced without an explicit, documented migration decision. Two tools for one problem mean that every future fix and every security update has to be considered twice, and it is usually done once - wherever someone happens to be working.

The stack is decided in the product specification pointed to in `CLAUDE.md`, and it is the point of reference for this rule. A new library enters the repository deliberately, not because it was at hand.

When the repository already has a library covering a given problem, new code uses it instead of writing its own parallel implementation of the same logic. Manually rewriting logic that the library solves correctly, together with edge cases that are easy to overlook, introduces the risk of a bug that was found and fixed in the library long ago.

## Calls to external systems

Every external dependency of the service - a third-party service, a third-party database, a token issuer, a shared file resource, an alert channel - is named and has one call site in the data layer. Rules that use a read from an external system call one seam in the rules layer that is responsible for that read, not the data layer module directly.

Every outgoing integration is subject to three requirements: an explicitly decided and documented retry strategy, its own named exceptions instead of raw exceptions of the transport library, and one way of reading configuration. Not retrying is an acceptable strategy if it is written down together with the reason - for example an integration called from an unattended run does not retry within the call, because the next run is the retry.

A read from an external system may be performed only from an unattended run or from an administrative forcing of the same work, never from request handling, because the service's response time would then depend on someone else's service. The exception is a call without which the request cannot be handled at all, for example fetching public keys to verify the caller's token. Such an exception is explicit and limited: it does not retry within the call, because unavailability ends the request with a refusal that the caller retries itself; it has an explicit timeout; its cost is limited by a cache with an explicit time to live that does not remember a failed fetch; and the blocking call goes from request handling through a thread pool.

An event sent to an external system as a consequence of a command is written in that command's transaction, and the transport is performed only by the worker, without an open database transaction while waiting for the response. The transport has one place in the data layer, and the rules for the event content, response classification and retrying have one place in the rules layer.

## Checklist

- Does the change avoid moving a domain rule into the input layer?
- Does the dependency direction between layers stay one-way?
- Does the change call a cross-cutting rule, for example the permission matrix or the visibility predicate, instead of recreating its condition in place?
- Do the listing query and the detail query use the same visibility predicate?
- Does new infrastructure code go to one shared place instead of into another copy?
- Does the change avoid bypassing an existing shared helper without an explicit, justified reason?
- Does the logger come from the central mechanism and from the shared project hierarchy?
- Does the change avoid introducing a parallel logging mechanism next to the central one?
- Does every new cache have an explicit invalidation strategy, avoid storing an error as a result, and have a deliberately chosen scope?
- Does the change avoid introducing a second library for a problem that the repository already solves with another one?
- Does a new outgoing integration have an explicit retry strategy, its own exceptions and one way of reading configuration?
- Is a read from an external system kept off the request handling path, and if it is on it, is it an explicit exception with a timeout, without retrying and with a cache that does not remember a failure?
- Is an event to an external system written in the command's transaction, and does the transport go from the worker without an open database transaction?
