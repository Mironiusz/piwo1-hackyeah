# Shape: Clarifications and housekeeping of the final checklist

Document state: 2026-10-04, interview in progress
Regulator: C:40

The seed carries no regulator, so the shape starts at C:40 (`MVP.md`, section How the MVP is built).

## Problem

Five checks of set 1 of `FINAL_CHECKLIST.md`, 1.1 - 1.5, are facts and rulings that no document of the repository holds yet, while other checks wait for them: the double submission and the Huawei deadline decide set 8, checks 9.4, 10.3, 10.4 and the Huawei part of 10.5; the Kraków pitch decides checks 10.1 and 10.6; the unmerged branches carry work check 2.2 starts from; the rulings given in place of members of the team stand until those people confirm them; and three entries of `docs/standards/decision_registry.md` block checks 4.2 and 2.2 (`FINAL_CHECKLIST.md`, set 1). None of them is decided by writing code. Each is an answer of the organizers, a merge, or a ruling of a named person, recorded where its check says.

## Recipient and trigger

- Rafał, who carries the clarifications in the division of the work (`TEAM.md`, column Works on; `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22), and who ticks every check of the list (same shape, requirement 17).
- The team, whose checks named in the section Problem wait for the answers.
- Trigger: `plans/final_checklist/` set up this initiative with its seed on 2026-10-04 for checks 1.1 - 1.5 (seed). The interview started at 04:30 on 2026-10-04, six and a half hours before the Kraków deadline of 11:00 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Current state

Verified in the repository and on the remote after `git fetch` at 04:30 on 2026-10-04. `origin/dev` and the branch of this session stand on the same commit, `f8fc67d`.

Check 1.1, the double submission and the Huawei deadline:

- `docs/hackathon/challenge_requirements.md`, Shared facts, says the Huawei deadline is not in the PDFs and has to be checked in the official HackYeah 2026 schedule; Conflicts and open points, item 9, keeps it open.
- None of the four official PDFs in `docs/official/` says whether one team may submit one project to two partner challenges, and the general HackYeah 2026 Rules, to which both sets of rules defer, are not in the repository (`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, section Domain rules or explicit TODO). At 02:53 public sources found by an agent confirmed only that the coding of the whole event ends at 11:00 on 4 October (same shape, Current state).

Check 1.2, the Kraków pitch:

- No document holds the time or the length of the Kraków pitch.
- `docs/hackathon/challenge_requirements.md`, Judging of challenge 1, gives the two Kraków sets of criteria, and Conflicts and open points, item 4, says which one the jury uses is to be asked of the mentors.

Check 1.3, the remote branches not merged into `origin/dev` at 04:30:

- `jmi/odklejka_v1`, five commits, the last at 04:18 by Jakub Mieczkowski: the initiative `schema_first_revision` with its shape, PRD, plan and review, stages A and B implemented - version 13 of the specification with the vote limit by calendar day and a 32-byte hash of a vote without an account, the package `accessibility_db` in `db/` with the first revision and 26 passing tests (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_REVIEW.md` on that branch). Its review leaves commit, push and the Merge Request to a human. A trial merge into `origin/dev` (`git merge-tree`) conflicts in nine files: `MVP.md`, `agent_docs/memory/_cross_cutting.md`, `docs/product/api_contract.md`, `docs/product/specification.md`, `docs/product/user_journeys.md`, `docs/product/views.md`, `docs/standards/decision_registry.md`, `docs/standards/naming_registry.md` and `docs/standards/standard_review.md`. Both sides hold a version 13 of the specification with different content: on `origin/dev` the two notes on the account written for `plans/accounts/`, on the branch the vote limit and the hash length.
- `js/frontend-shape`, one commit of 2026-10-03 17:43 by Jakub Slupczewski: it edits `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, an earlier text of the shape that `origin/dev` holds in `plans_finished/frontend_stack/` with the merged result of both interviews of that initiative. Its content appears superseded; not confirmed with its author.
- `mw-osm-import`, one commit ahead of `origin/dev` at 02:34 by the git user kindaCacti: a merge of `dev` into `mw/osm-import`. Every other commit of the branch is already in `origin/dev`; the files of the merge are older texts of files `origin/dev` holds.
- `mw`, five commits, the last at 01:25 by the git user kindaCacti: the initiative `bus_station_api_integration` (seed, shape, PRD, plan) with a daily import of the stops of MSIP, and `docs/apis/msip_stops.md`. `docs/standards/decision_registry.md`, entry Initiatives outside MVP.md that overlap its initiatives, says Rafał and the owner of the initiative decide whether the stops of MSIP enter the MVP, against the no-periodic-task rule of D-14 and O4 being outside the MVP. Which member of `TEAM.md` the git user kindaCacti is, the repository does not record.
- `main` is one merge commit of `dev` ahead and behind `dev`; it is not a branch carrying work of the day.

Check 1.4, the confirmations (`MVP.md`, section Open decisions and confirmations):

- The division of the work of `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22: Marek, Kuba, Kuber and Adrian.
- Marek for D-9 and D-14; Kuba for D-11, the answers of the interview of `plans_finished/schema_revision/` and the form of the idempotency key of version 12; Kuber and Adrian for the contract of D-12, the pseudonym rule of `docs/product/api_contract.md` included.
- Mateusz for the thresholds and value lists of D-5.
- On `jmi/odklejka_v1` Kuba confirmed D-11, the answers of `plans_finished/schema_revision/` and the form of the idempotency key (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_SHAPE.md` on that branch, questions 6 and 9); the confirmation reaches `MVP.md` on `dev` only with the merge.
- `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7, says Kuber and Adrian confirm that the Huawei submission is mandatory, but `MVP.md`, section Open decisions and confirmations, does not list that ruling, so check 1.4 does not cover it.

Check 1.5, the registry entries:

- When the initiative of O9 starts its code: Rafał and Marek decide. Wording of the public transport segment of O9: Marek and Rafał decide. Check 4.2 depends on both.
- Hash length reported by Kuba: Kuba names the fields and confirms the binary representation. On `jmi/odklejka_v1` Kuba decided that the hash of a vote without an account, `voter_hash`, is 32 bytes, checked by `CK_vote_voter_hash_sha256` in `docs/product/schema.md` and in the first revision `db/accessibility_db/migrations/versions/0001_target_schema.py`. The entry was added on `dev` after the branch forked, so the branch does not hold it and the merge alone does not resolve it. Check 2.2 depends on it.

## Smallest meaningful scope

Following from the seed: checks 1.1 - 1.5 of `FINAL_CHECKLIST.md` carried out until each meets its Done when.

The work is split between the agent and the people (decided by the user on 2026-10-04, question 1 of the interview, against the agent only recording what Rafał brings and against the agent also resolving the conflicts of the merge of `jmi/odklejka_v1` locally):

- The agent prepares: the questions to the organizers and the mentors, the message asking each named person for their confirmation or ruling, and the analysis of every unmerged branch with a recommendation to merge or to close it.
- Rafał asks the organizers, sends the messages, collects the answers, and merges or closes the branches.
- The agent records every answer with its source in the document its check names.

## Out of scope

- Check 1.6, the consistency of the repository, which belongs to `plans/repository_consistency/` (seed).
- Ticking a check, which only Rafał does (`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 17).

## Functional requirements

1. Whether one team may submit one project to both partner challenges, and the Huawei submission deadline, are recorded with their source in `docs/hackathon/challenge_requirements.md` (`FINAL_CHECKLIST.md`, check 1.1).
2. The time and length of the Kraków pitch and which of the two Kraków sets of criteria the jury uses are recorded with their source in the same document (check 1.2).
3. Every remote branch carrying work of the day is merged into `dev` or closed, and the registry entry on the initiatives outside `MVP.md` is settled for `mw` (check 1.3).
4. Every ruling `MVP.md`, section Open decisions and confirmations, lists as given in place of a member of the team, the division of the work included, and the thresholds of D-5 are confirmed or changed by the people that section names (check 1.4).
5. The registry entries on when the code of O9 starts, on the wording of its public transport segment and on the hash length are resolved by the people they name, or the dependent check is recorded as dropped (check 1.5).
6. The question of `docs/standards/decision_registry.md`, entry Intellectual property between the two challenges and the repository licence - how the copyright transfer of the Kraków prize relates to the Huawei licence and to a public repository - goes to the organizers together with the questions of check 1.1, and the answer is recorded in that entry. It is not a check of set 1; it joins because it goes to the same people as check 1.1 (decided by the user on 2026-10-04, question 3 of the interview, against leaving the entry open until the results). Nothing recorded here is legal advice.

## Scenarios: input, flow, expected state after the run

To be filled in during the interview.

## Challenging own assumptions

To be filled in during the interview.

## Domain rules or explicit TODO

- Changes enter `dev` only through a Merge Request, and the agent creates no commit and pushes nothing (`CLAUDE.md`, section Working with git). A branch is merged into `dev` or closed by a person.
- What counts as a source for checks 1.1 and 1.2. The agent first searches the official publications of the organizers - the HackYeah 2026 site, the general rules, the schedule, the announcements - and records what it finds at once, with the address and the date it was read. The Huawei submission deadline and the time of the Kraków pitch are also confirmed by Rafał with the organizers or the mentors, because a mistake in either costs a submission or the pitch; every other fact is closed by the publication alone. What no publication holds goes to the organizers or the mentors as a question (decided by the user on 2026-10-04, question 2 of the interview, against a publication alone and against a direct answer alone).
- A source of an answer is cited without personal data. The repository becomes public for the Huawei submission and must hold no personal data (`FINAL_CHECKLIST.md`, check 9.5), and `docs/hackathon/challenge_requirements.md` already names the mentors of the Kraków challenge only by pointing to the task description. A person outside the team is cited by role, channel and time, never by name. Found in the repository, not asked (category: personal data).

## Notes on data, performance and security

- No address, host, login or secret of the hosted demo enters any document this initiative writes (`CLAUDE.md`, section Target environment).

## Open questions

4. Whether the confirmation of requirement 7 of `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md` by Kuber and Adrian joins check 1.4. `Block: no`
5. Who resolves the conflicts of the merge of `jmi/odklejka_v1` into `dev`, and which version number the specification of that branch gets next to the version 13 already on `dev`. `Block: yes` (category: database schema)
6. What happens to `mw`: the stops of MSIP in or out of the MVP, and the branch merged or closed. `Block: no`
