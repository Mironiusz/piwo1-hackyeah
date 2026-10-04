# Shape: Clarifications and housekeeping of the final checklist

Document state: 2026-10-04, interview closed
Regulator: C:40

The seed carries no regulator, so the shape starts at C:40 (`MVP.md`, section How the MVP is built).

## Problem

Five checks of set 1 of `FINAL_CHECKLIST.md`, 1.1 - 1.5, are facts and rulings that no document of the repository holds yet, while other checks wait for them: the double submission and the Huawei deadline decide set 8, checks 9.4, 10.3, 10.4 and the Huawei part of 10.5; the Kraków pitch decides checks 10.1 and 10.6; the unmerged branches carry work check 2.2 starts from; the rulings given in place of members of the team stand until those people confirm them; and three entries of `docs/standards/decision_registry.md` block checks 4.2 and 2.2 (`FINAL_CHECKLIST.md`, set 1). None of them is decided by writing code. Each is an answer of the organizers, a merge, or a ruling of a named person, recorded where its check says.

## Recipient and trigger

- Rafał, who carries the clarifications in the division of the work (`TEAM.md`, column Works on; `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22), and who ticks every check of the list (same shape, requirement 17).
- The team, whose checks named in the section Problem wait for the answers.
- Trigger: `plans_finished/final_checklist/` set up this initiative with its seed on 2026-10-04 for checks 1.1 - 1.5 (seed). The interview started at 04:30 on 2026-10-04, six and a half hours before the Kraków deadline of 11:00 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Current state

Verified in the repository and on the remote after `git fetch` at 04:30 on 2026-10-04, and again at 04:59, after the merge of `jmi/odklejka_v1` into `dev` (PR #29, `afe5bc1`, 04:42) and of `dev` into the branch of this session (`0901955`, 04:48). At 04:59 the branch of this session holds every commit of `origin/dev`. `plans/final_checklist/` moved to `plans_finished/final_checklist/` at 04:45.

Check 1.1, the double submission and the Huawei deadline:

- `docs/hackathon/challenge_requirements.md`, Shared facts, says the Huawei deadline is not in the PDFs and has to be checked in the official HackYeah 2026 schedule; Conflicts and open points, item 9, keeps it open.
- None of the four official PDFs in `docs/official/` says whether one team may submit one project to two partner challenges, and the general HackYeah 2026 Rules, to which both sets of rules defer, are not in the repository (`plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, section Domain rules or explicit TODO). At 02:53 public sources found by an agent confirmed only that the coding of the whole event ends at 11:00 on 4 October (same shape, Current state).

Check 1.2, the Kraków pitch:

- No document holds the time or the length of the Kraków pitch.
- `docs/hackathon/challenge_requirements.md`, Judging of challenge 1, gives the two Kraków sets of criteria, and Conflicts and open points, item 4, says which one the jury uses is to be asked of the mentors.

Check 1.3, the remote branches carrying work of the day:

- `jmi/odklejka_v1`, the initiative `schema_first_revision` of Kuba, was merged into `dev` at 04:42 (PR #29). At 04:30 a trial merge conflicted in nine files, and both sides held a version 13 of the specification with different content; the merge joined them into one version 13, as the user decided while merging (`docs/product/specification.md`, Decision provenance, version 13).
- The branches below were still not merged into `origin/dev` at 04:59.
- `js/frontend-shape`, one commit of 2026-10-03 17:43 by Jakub Slupczewski: it edits `plans/frontend_stack/FRONTEND_STACK_SHAPE.md`, an earlier text of the shape that `origin/dev` holds in `plans_finished/frontend_stack/` with the merged result of both interviews of that initiative. Its content appears superseded; not confirmed with its author.
- `mw-osm-import`, one commit ahead of `origin/dev` at 02:34 by Mateusz (git user kindaCacti, answer of the user to question 9 of the interview): a merge of `dev` into `mw/osm-import`. Every other commit of the branch is already in `origin/dev`; the files of the merge are older texts of files `origin/dev` holds.
- `mw`, five commits, the last at 01:25 by Mateusz: the initiative `bus_station_api_integration` (seed, shape, PRD, plan) with a daily import of the stops of MSIP at 03:00 and an import on the start of the application, and `docs/apis/msip_stops.md`. `docs/standards/decision_registry.md`, entry Initiatives outside MVP.md that overlap its initiatives, says Rafał and the owner of the initiative decide whether the stops of MSIP enter the MVP, against the no-periodic-task rule of D-14 and O4 being outside the MVP. A trial merge into `origin/dev` at 05:00 (`git merge-tree`) has no conflict. Its artifacts were written on 2026-10-03 before the MVP was settled: the seed is named `SEED.md` instead of `BUS_STATION_API_INTEGRATION_SEED.md`, they point to `plans/mvp/` and `plans/fact_schema/`, and the plan is a draft marked not ready for implementation, which `tests/architecture/test_plan_document_contract.py`, checking every `*_PLAN.md` in `plans/` and `plans_finished/`, may refuse; the test was not run on it.
- `main` is one merge commit of `dev` ahead and behind `dev`; it is not a branch carrying work of the day.

Check 1.4, the confirmations (`MVP.md`, section Open decisions and confirmations):

- The division of the work of `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22: Marek, Kuba, Kuber and Adrian.
- Marek for D-9 and D-14; Kuber and Adrian for the contract of D-12, the pseudonym rule of `docs/product/api_contract.md` included.
- Mateusz for the thresholds and value lists of D-5.
- Kuba's part is done: since the merge of PR #29, `MVP.md` records that Kuba confirmed D-11, the answers of `plans_finished/schema_revision/` and the form of the idempotency key of version 12 (`plans/schema_first_revision/SCHEMA_FIRST_REVISION_SHAPE.md`, questions 6 and 9). Kuba still confirms the division of the work.
- `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7, says Kuber and Adrian confirm that the Huawei submission is mandatory, but `MVP.md`, section Open decisions and confirmations, does not list that ruling, so check 1.4 does not cover it.

Check 1.5, the registry entries:

- When the initiative of O9 starts its code: Rafał and Marek decide. Wording of the public transport segment of O9: Marek and Rafał decide. Check 4.2 depends on both.
- Hash length reported by Kuba: resolved. Since the merge of PR #29 the entry stands in Resolved decisions of `docs/standards/decision_registry.md`: `voter_hash` of `vote` is 32 bytes, held by `CK_vote_voter_hash_sha256`, in `docs/product/schema.md` and in the first revision `db/accessibility_db/migrations/versions/0001_target_schema.py`. The part of check 1.5 that check 2.2 depends on is met.

## Smallest meaningful scope

Checks 1.1 - 1.5 of `FINAL_CHECKLIST.md` carried out until each meets its Done when (seed), together with what the interview added to them: the question on the intellectual property sent with check 1.1, the confirmation of the mandatory Huawei submission joining check 1.4, and the stops of MSIP brought into the MVP as an optional check once check 1.3 settles `mw` (Functional requirements 5 and 7 - 10).

The work is split between the agent and the people (decided by the user on 2026-10-04, question 1 of the interview, against the agent only recording what Rafał brings and against the agent also resolving the conflicts of the merge of `jmi/odklejka_v1` locally):

- The agent prepares: the questions to the organizers and the mentors, the message asking each named person for their confirmation or ruling, and the analysis of every unmerged branch with a recommendation to merge or to close it.
- Rafał asks the organizers, sends the messages, collects the answers, and merges or closes the branches.
- The agent records every answer with its source in the document its check names.

## Out of scope

- Check 1.6, the consistency of the repository, which belongs to `plans/repository_consistency/` (seed).
- Ticking a check, which only Rafał does (`plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 17).
- Asking the organizers, sending the messages, merging and closing branches: Rafał does them (question 1 of the interview).
- Deciding in place of the people a check names. The agent records a ruling, it never gives one; an answer of the user to a question addressed to another person is recorded as given in that person's place, to be confirmed.
- Building the stops of MSIP and rewriting the PRD and the plan of `bus_station_api_integration` after requirements 9 and 10: the work of that initiative and of Mateusz.

## Functional requirements

1. Whether one team may submit one project to both partner challenges, and the Huawei submission deadline, are recorded with their source in `docs/hackathon/challenge_requirements.md` (`FINAL_CHECKLIST.md`, check 1.1).
2. The time and length of the Kraków pitch and which of the two Kraków sets of criteria the jury uses are recorded with their source in the same document (check 1.2).
3. Every remote branch carrying work of the day is merged into `dev` or closed, and the registry entry on the initiatives outside `MVP.md` is settled for `mw` (check 1.3).
4. Every ruling `MVP.md`, section Open decisions and confirmations, lists as given in place of a member of the team, the division of the work included, and the thresholds of D-5 are confirmed or changed by the people that section names (check 1.4).
5. `MVP.md`, section Open decisions and confirmations, gains an item for the ruling of `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7, that the Huawei submission is mandatory, given by the user in place of the team and to be confirmed by Kuber and Adrian, so that check 1.4 covers it; the question goes in the same message as their other confirmations (decided by the user on 2026-10-04, question 4 of the interview, against leaving the ruling without a confirmation).
6. The registry entries on when the code of O9 starts, on the wording of its public transport segment and on the hash length are resolved by the people they name, or the dependent check is recorded as dropped (check 1.5).
7. The question of `docs/standards/decision_registry.md`, entry Intellectual property between the two challenges and the repository licence - how the copyright transfer of the Kraków prize relates to the Huawei licence and to a public repository - goes to the organizers together with the questions of check 1.1, and the answer is recorded in that entry. It is not a check of set 1; it joins because it goes to the same people as check 1.1 (decided by the user on 2026-10-04, question 3 of the interview, against leaving the entry open until the results). Nothing recorded here is legal advice.
8. The stops of buses and trams of MSIP enter the MVP, settling for `mw` the registry entry Initiatives outside MVP.md that overlap its initiatives (decided by the user on 2026-10-04, question 6 of the interview, against leaving them outside the MVP with the branch closed, which the agent recommended, and against leaving them outside with the branch merged and the initiative archived). The registry names Rafał and the owner of `bus_station_api_integration` as the deciders, so Mateusz, the owner (answer of the user to question 9 of the interview), confirms the ruling; it also changes the work of Mateusz, which `MVP.md` and `TEAM.md` record as unchanged by the division of `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22. In consequence `mw` is merged into `dev`; `MVP.md` brings the initiative into its Scope, Initiatives, with Mateusz as its owner, and Requirements and initiatives; `TEAM.md`, column Works on, adds it to the work of Mateusz; `FINAL_CHECKLIST.md` gains its check and its stage; the initiative gets its `STAGE.md`; and the registry entry moves to Resolved decisions.
9. The stops of MSIP are imported by a one-off step of the one loading program of `osm_import`, run by hand like the OpenStreetMap import; D-14 stays unchanged, and the daily refresh at 03:00 and the import on the start of the application leave the scope of `bus_station_api_integration`. The first daily run would fall on 5 October, after the demo and its data are deleted on 4 October (decided by the user on 2026-10-04, question 7 of the interview, against a daily periodic task that would change D-14). Rewriting the PRD and the plan of `bus_station_api_integration` to match is the work of that initiative, not of this one.
10. The stops of MSIP enter the MVP as a part of the optional feature O4, the way O9 does: `MVP.md`, section Scope, names them next to O9, and their check in `FINAL_CHECKLIST.md` is marked optional and does not condition the end of the project. The exception of `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 15, which applied to O9 alone, now covers O9 and this part of O4, and `FINAL_CHECKLIST.md`, section How to read this list, says so. The specification keeps O4 optional and needs no new version for the status (decided by the user on 2026-10-04, question 8 of the interview, against a mandatory check, which needs a new version of the specification moving the stops into the mandatory features).

## Scenarios: input, flow, expected state after the run

1. A fact found in a publication. Input: at 05:30 the agent finds on an official page of the organizers when the Huawei submission closes and whether a double submission is allowed. Flow: the agent records both in `docs/hackathon/challenge_requirements.md` with the address and the date it was read, and marks the Huawei deadline as waiting for the confirmation of Rafał; at 08:30 Rafał relays the confirmation of the organizers' desk with the time it was given. Expected state: Shared facts and Conflicts and open points, item 9, hold the answer and its source; check 1.1 can be verified.
2. An answer that removes work. Input: the organizers answer that one project may be submitted to one partner challenge only. Flow: the agent records it with its source and names the checks that depend on it - set 8, checks 9.4, 10.3, 10.4 and the Huawei part of 10.5. Expected state: the answer is recorded; what the team does about it is decided by the team, not by this initiative.
3. A confirmation. Input: Marek answers the message prepared by the agent with a confirmation of D-9 and D-14 and the division of the work. Flow: Rafał relays the answer; the agent turns the item of `MVP.md`, section Open decisions and confirmations, into a recorded confirmation with the date, as Kuba's confirmation of D-11 is recorded. Expected state: check 1.4 has one person fewer to wait for.
4. The stops of MSIP. Input: Mateusz confirms that they enter the MVP as an optional part of O4 with a one-off import. Flow: Mateusz brings the artifacts of `bus_station_api_integration` on `mw` into line with the standards, Rafał merges `mw` into `dev` through a Merge Request, and the agent writes requirement 8 into `MVP.md`, `TEAM.md`, `FINAL_CHECKLIST.md`, the `STAGE.md` of the initiative and the registry. Expected state: `mw` is merged, the registry entry is resolved, and the list shows one more optional check. If Mateusz does not confirm, the ruling stays given in the place of Mateusz and the entry stays open until Rafał and Mateusz agree.
5. A ruling that does not come. Input: at 09:00 Marek has not decided when the code of O9 starts or how its segment is worded. Flow: the entries stay open; check 4.2 is recorded as dropped only when the team decides so and Rafał relays it. Expected state: check 1.5 is met by the dropped check, and nothing in the repository says O9 was decided.

## Challenging own assumptions

- Is a shape, a PRD and a plan worth it for work that is mostly messages and records, at 05:00 with six hours left? A check is done when its effect works, not when the chain is complete (`FINAL_CHECKLIST.md`, section How to read this list). The chain is the default of the repository; how far it goes is the user's call at the gate after this interview.
- Are the facts of the organizers stable? A publication read at night may be changed in the morning. That is why the two facts whose mistake costs a submission or the pitch are confirmed with the organizers (Domain rules), and every record carries the date it was read.
- Does the merge of `mw` keep the repository compliant? Not as the branch stands: its artifacts predate the MVP, describe a daily import that requirement 9 removes, and its draft plan may fail the plan document test. The repository applies its standards in full from the first commit (`CLAUDE.md`, section Full compliance with the standards), so the merge waits until the architecture tests pass on the branch; the agent runs them on the branch and says what fails, Mateusz fixes it. Agent decision at C:40, without asking: it follows from that rule.
- Does the ruling on the stops of MSIP fit the load of the day? Mateusz already carries `osm_importer`, on the critical path, with `osm_import`, `address_search` and `sample_data` (`MVP.md`, section Order and critical path). The check is optional (requirement 10), so it never blocks the end of the project, but the time Mateusz spends on it is taken from the critical path. The cut, if needed, is the team's during the day.
- Is the hash length really settled? Yes, verified at 04:59: the entry is in Resolved decisions of `docs/standards/decision_registry.md` and `CK_vote_voter_hash_sha256` is in the first revision.
- Is the confirmation of Kuba fully done? Only for D-11, the interview of `plans_finished/schema_revision/` and the idempotency key; the division of the work still waits for Kuba too (Current state).
- Are `js/frontend-shape` and `mw-osm-import` safe to close? The analysis says their content is superseded by `dev`, but only their authors know whether anything on them was meant to survive. The recommendation goes to Rafał, who closes them after asking their authors.

## Domain rules or explicit TODO

- Changes enter `dev` only through a Merge Request, and the agent creates no commit and pushes nothing (`CLAUDE.md`, section Working with git). A branch is merged into `dev` or closed by a person.
- What counts as a source for checks 1.1 and 1.2. The agent first searches the official publications of the organizers - the HackYeah 2026 site, the general rules, the schedule, the announcements - and records what it finds at once, with the address and the date it was read. The Huawei submission deadline and the time of the Kraków pitch are also confirmed by Rafał with the organizers or the mentors, because a mistake in either costs a submission or the pitch; every other fact is closed by the publication alone. What no publication holds goes to the organizers or the mentors as a question (decided by the user on 2026-10-04, question 2 of the interview, against a publication alone and against a direct answer alone).
- A source of an answer is cited without personal data. The repository becomes public for the Huawei submission and must hold no personal data (`FINAL_CHECKLIST.md`, check 9.5), and `docs/hackathon/challenge_requirements.md` already names the mentors of the Kraków challenge only by pointing to the task description. A person outside the team is cited by role, channel and time, never by name. Found in the repository, not asked (category: personal data).
- The check of the stops of MSIP goes into set 3, Open data, next to the other imports, and its stage follows the rule of `FINAL_CHECKLIST.md`, section Stages: its effect needs the loading program of `osm_import` (stage 4) for its one-off step (requirement 9), so it is stage 5, like `sample_data` and the loading step of `map_tiles`. Agent decision at C:40, without asking: it follows from requirements 9 and 10 and the stage rule. The exact wording of the check is settled in the PRD.
- A check that depends on an unresolved entry is recorded as dropped only when the team decides so and Rafał relays it; the agent never records a drop on its own. Agent decision at C:40, without asking: `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 8, leaves what is dropped to the team.
- TODO for `bus_station_api_integration`, not settled here: what the app shows of the stops of MSIP is not described by the specification, and product behavior it does not describe goes to the user (`CLAUDE.md`, section What we are building); O4 itself requires checking on what terms the datasets of MSIP can be used before they are used (`docs/product/specification.md`, O4), and the shape of that initiative records the terms as not verified; and the stops need a table of their own in the target schema, which is part of the specification, and an operation of `docs/product/api_contract.md`.

## Notes on data, performance and security

- No address, host, login or secret of the hosted demo enters any document this initiative writes (`CLAUDE.md`, section Target environment).
- The questions to the organizers and the messages to the team carry no secret and no personal data; they are prepared by the agent and sent by Rafał.
- No question of this interview decided a contract, a schema, data or a permission. The stops of MSIP touch three blocking categories - the database schema (a new table), the programming interface contract (a new operation) and the source of truth for data (a new source with unverified terms) - but they are decided in the chain of `bus_station_api_integration`, not here (Domain rules, TODO).
- The repository becomes public for the Huawei submission, so every record is written to be published.

## Open questions

None. Question 5 of the first list, who resolves the conflicts of the merge of `jmi/odklejka_v1` and how the two versions 13 are numbered, `Block: yes` (category: database schema), was withdrawn unasked: the user merged the branch at 04:42 and joined the two versions into one version 13 (Current state). Question 9, the owner of `bus_station_api_integration`, was answered in plain text: Mateusz.
