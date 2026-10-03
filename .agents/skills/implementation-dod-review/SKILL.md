---
name: implementation-dod-review
description: review of implementation changes against the repository's Definition of Done. use when the user asks for a readiness check, an architecture review, a quality assessment of a code unit, documentation verification, an audit of changed files or preparing a change for merge.
---

# Review process

Assess the implementation against the repository's Definition of Done.

Before reading the code, open `docs/standards/README.md` - the map of all standards, with a separate section for each standard, saying what it is responsible for and what status it has (ready, partial, skeleton). The map replaces any fixed list of standards written out here, so this skill does not go stale as further files are added to the directory.

Also check `docs/standards/decision_registry.md`. The absence of a rule in a given area may be a recorded deferral, not a gap - reporting as missing something that is deliberately postponed together with a reason is noise.

Then look at the changed files. If git context is available, the scope of the review is the current diff. If it is not, the scope is the files or code indicated by the user.

Check the change against every standard from the map in `docs/standards/standard_review.md`, section "Standard - verifying tool map" - not only against those that seem relevant after reading the diff. For a standard with a mapped command, actually run it, via `Bash` or `PowerShell`, instead of judging compliance by eye. The deviation rule is strict until `docs/standards/README.md` records an explicit decision to relax it: a project without legacy code has nothing to protect with a transition period, so non-compliance with a standard blocks the review regardless of who wrote the given fragment and when.

A run weighs more than a review. A known failure of a run within the scope of the change (tests, the chain on an environment, e2e tests) keeps the verdict at not ready, even when the letter of the acceptance criterion is met. Before the verdict, check that no run later than the assessment of the criterion contradicts the scope you are assessing, and assess the code of the target branch, not which initiative was supposed to close a given thing.

Do not invent missing context. If a required file, standard, responsibility boundary, test or document is missing - report it plainly.

What not to report:

- speculative rewrites that the change does not need,
- stylistic preferences without a concrete risk - with the caveat that a rule recorded in a standard is not a stylistic preference: you report a violation of `standard_formatting.md`, for example bold in prose or a character from the forbidden list, normally,
- problems that existed before the change and lie outside its scope, unless they block understanding of the change itself,
- the absence of a rule in an area covered by an entry in the deferred decisions registry.

Report findings in this order:

1. Blockers - things because of which the change is not finished.
2. Risks - things that may be acceptable but require a conscious decision.
3. Improvements - optional cleanups and quality suggestions.
4. Verification - a list of all standards from the map in `standard_review.md`, each with one of three states: not applicable (with a short reason), checked automatically (the command from the map was run, the result or its summary in the report), checked manually (the standard has no mapped command). Skipping a standard without one of these three states is an incomplete Verification.
5. Verdict - one of three: ready, ready after minor fixes, not ready - together with the scope it covers: the whole initiative, one task out of several, the plan alone or the indicated files.

The scope of the verdict decides the further fate of the initiative directory, so name it explicitly: a final `ready` for the whole initiative qualifies it for the `plans_finished/` archive, a `ready` for one task, the plan or part of the code does not (`docs/standards/standard_agentic_workflow.md` ch. 4.6). Report this qualification in the report, but do not move anything - the review stays in read-only mode, and the move belongs to `plan-implement` or to an agent whom the user has explicitly instructed to clean up. A review called on an initiative that is already explicitly finished says so in the report, instead of assessing it anew.

Choose concrete file-level feedback, not general advice.
