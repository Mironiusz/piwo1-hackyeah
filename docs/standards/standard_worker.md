# Worker and periodic tasks standard

Document state: 2026-10-03

Status: ready - full content.

## Why this document exists

The worker runs unattended, so its bug is not visible right away - it shows up as the absence of something that was supposed to happen. A task that stopped running does not report itself; a task that ran twice in parallel reports itself as duplicated data in a place where nobody looks for the cause in the schedule.

This standard defines the contract that every periodic task fulfills, so that these two cases can be detected and do not depend on the memory of the person adding the next task.

## Scope and boundaries

This standard is responsible for: the periodic task contract, the lock mechanism and convention, task timeouts, the run result and the way of adding a new task.

What is not here:

- what exactly each task does - this is decided by the product specification pointed to in `CLAUDE.md`, and it is the source of truth here, not this document;
- the reaction to an error during a task and the durable attempt counter - that is `standard_errors.md`;
- whether a repeated run duplicates the effect - that is `standard_idempotency.md`;
- the meaning of time values and the zone in which schedule expressions are computed - that is `standard_time.md`;
- the log entry format and the run identifier - that is `standard_logging.md`.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that comes into force on its own.

## One process, one task registry

The worker is a second entry point of the same image, not a separate service and not a separate repository. It shares the rules layer and the data layer with the programming interface - a periodic task calls the same rules as a request does, and has no separate, parallel copy of the domain logic.

There is one registry of periodic tasks and it lives in the rules layer. The worker has its own directory layer `worker/`, which keeps time and runs the tasks from this registry. The layer has not a single domain rule and is not to have one: the only rule it carries is the task's hour window, checked at every start of the task. The dependency runs only from the `worker/` layer to the rules layer: the layer knows neither request handling nor the data layer, and none of the other layers knows it, because the process entry point is nobody's dependency. The project guards this rule with an architecture test that it creates together with the first code of this layer; the template does not contain it.

Consequence: a rule called from a periodic task cannot assume that a caller, its token or its permissions exist. A rule that requires this is written for request handling and needs to be fixed, not worked around by substituting an artificial actor in the worker.

The correctness of a task does not rest on the assumption that the worker runs in a single instance - see the section Locks below. The same database lock protects against a duplicated trigger by the schedule, for example after a restart or with a second trigger instance, and against two processes running the same task: they collide on it just like two instances of one process. When the tasks from the registry are run by more than one process, the split goes by queue or by process, not by a second registry and not by a second entry point.

## Periodic task contract

Every periodic task has all of the following, explicitly, in code:

- a name, unique across the whole repository, used in the log and in the lock;
- a frequency or a schedule expression, computed in the project's business zone (`standard_time.md`);
- an explicit run timeout, not inherited and not a default;
- an explicit lock wait timeout, zero by default - see below;
- a lock name, unique, tied to the task name;
- an hour window in which the task is allowed to start, or an explicit absence of one.

Missing any of these values is not a minor oversight: a task without a timeout can block the next run for hours, and a task without a lock can do its work twice in parallel.

The hour window is optional, but its absence is a value, not an omission: it means a task running at any time of day. The hours count in the business zone, because a nightly task is to be nightly for a human, not for the server - counted in universal time it would shift by an hour twice a year without any change in the repository. The window includes the start hour and excludes the end hour, so two windows where one ends and the other begins have no hour in common. The windows of nightly tasks run by the same process are to be disjoint: the tasks of one single-threaded process execute one after another, so a task starting at the same hour as another one from this process stops having its own time slot. The window must be longer than the run timeout, otherwise the task sometimes gets cut off by the deadline despite the margin in the timeout itself.

## Locks

A periodic task takes a lock before starting work and releases it after finishing, regardless of whether it finished successfully. The lock lives in the database, not in the process memory - an in-memory lock does not protect against a second instance of the process, and that is exactly the scenario it is supposed to protect against.

The lock wait timeout is zero by default: when the lock is taken, the task skips this run, records it and ends. It does not wait in a queue. Reason: a periodic task started every minute that waits for the lock has, after an hour of outage, sixty pending runs that will execute in a cascade one after another - instead of one that would do the same thing once.

Skipping a run because the lock is taken is not an error and is not logged as an error. It is a normal state that is to be visible in the log as information.

## Run result

The run result answers the question whether the attempt took place, not whether it succeeded. It distinguishes two states: a run that was executed and a run that was skipped because the lock was taken. This is a deliberate contract, not a lack of precision - the success of the work itself is told by its own result: how many items were processed, how many were skipped and why.

A run that processed some items and skipped the rest is an executed run with recorded skips, not a failed run. The rules for this record are in `standard_errors.md`.

## Adding a new task

A new periodic task requires: a name and a lock that do not collide with existing ones, both timeouts set explicitly, an entry in `standard_worker.md` if the contract changes, and an update of the task consistency test.

The consistency test checks what a human will not notice when adding the next task: the uniqueness of names and locks and the presence of both timeouts. The project guards this rule with an architecture test that it creates together with the first code of this layer; the template does not contain it. Adding a task without updating the test is a violation of this standard, even if the task itself works correctly.

A task that deletes data requires separate attention. Deleting data by a periodic task is a product rule, not a technical decision: a task deleting anything that the product specification does not explicitly allow requires a decision by the product owner.

## Behavior in production

Changing the frequency, time window, lock or order of steps of an existing task is a change in the behavior of a system running unattended. Such a change belongs to a blocking risk category in the shape phase (`standard_agentic_workflow.md` ch. 3.3) and requires an explicit decision, not a decision made while writing the code.

## Checklist

- Does the new task have a unique name and a unique lock name?
- Does it have an explicit run timeout and an explicit lock wait timeout?
- Does it have an hour window or an explicit absence of one, and if it has one, is it longer than the run timeout and disjoint from the windows of the other nightly tasks of the same process?
- Is the lock wait timeout zero, and if not, is the reason for it recorded?
- Does the lock live in the database, not in the process memory?
- Is skipping a run because the lock is taken logged as information, not as an error?
- Does the run result distinguish an executed run from a skipped one, with the success of the work told by its own result?
- Does the task report the number of processed and skipped items?
- Do the rules called from the task avoid requiring a caller or its permissions to exist?
- Has the task consistency test been updated with the new task?
- Has a change to the frequency, window or lock of an existing task gone through a decision in the shape phase?
- Does the task avoid deleting data whose deletion the product specification does not explicitly allow?
