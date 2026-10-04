# Shape: Final checklist whose completion means the project is finished

Document state: 2026-10-04, interview closed, amended after the interview with requirements 22 - 25
Regulator: C:40

## Problem

The team has no single list that says when the project is finished. The work of the day is spread over twelve initiatives of `MVP.md`, the deliverables of two challenges in `docs/hackathon/challenge_requirements.md`, open decisions in `docs/standards/decision_registry.md` and a presentation that has no document yet. Without one list nobody can see what is left, what can be dropped and in what order to do it, and the request says what the team does today depends on it.

The result is `FINAL_CHECKLIST.md`: sets of tasks, each with a few checks. A set is one large initiative, a check is one small initiative or a fragment of a large one, split so that there are not too many of either (seed).

## Recipient and trigger

The team of `TEAM.md`, led by Rafał, on the last day of the hackathon, 4 October 2026. The trigger is the request of the seed, made at 02:53 with about eight hours left to the Kraków deadline of 11:00. After the list is written, the team parallelizes its checks among its six people (requirement 11).

## Current state

Verified in the repository and on `origin/dev` at 02:53 on 2026-10-04:

- There is no product code yet: no `frontend/`, no `api/`, `service/`, `data/` or `worker/` on `origin/dev`. What exists is `valhalla/` with its image workflow, the core gates in `tests/architecture/` and the documentation (`README.md`, section What is inside: "There is no product code yet").
- The twelve initiatives of `MVP.md`, section Initiatives, each hold only a seed in `plans/<name>/`, except `plans/frontend_app/`, which also holds the draft `FRONTEND_APP_PACKAGES.md`.
- Unmerged work on remote branches: `origin/md/fast-setup` and `origin/mw-osm-import` carry a shape and a PRD of `backend_skeleton` and a full chain of a task `osm_importer` (seed, shape, PRD, plan) that overlaps `osm_import`; `origin/jmi/odklejka_v1` carries a shape and a PRD of `schema_first_revision`; `origin/mw` carries an initiative `bus_station_api_integration` outside `MVP.md`, with `docs/apis/msip_stops.md`; `origin/js/frontend-shape` changes one file.
- The design briefs and mocks of four views are in `.impeccable/briefs/views/`.
- The deliverables of both challenges are listed in `docs/hackathon/challenge_requirements.md`; the Kraków submission is due at 11:00 on 4 October on HackTribe. The Huawei deadline is not in the PDFs (Conflicts and open points, item 9); public sources found by the agent at 02:53 confirm only that the coding of the whole event ends at 11:00 on 4 October.
- The four official PDFs of the challenges were added by the user on 2026-10-04 to `docs/official/` (untracked at 03:20): `KRYTERIA Kraków Bez Barier.pdf`, `RULES Cracow Without Barriers.pdf`, `CRITERIA Imagine What_s Next.pdf` and `RULES Imagine What_s Next.pdf`. The agent read all four on 2026-10-04; what they add to `docs/hackathon/challenge_requirements.md` is in the section Domain rules or explicit TODO.
- Open decisions that touch the submissions: the HarmonyOS port and the Huawei submission, waiting for a go/no-go time, and the intellectual property between the two challenges and the repository licence, waiting for the organizers (`docs/standards/decision_registry.md`).

Verified again at 03:56 on 2026-10-04, after the merge of `md/fast-setup` into `dev` and into this branch:

- `plans/osm_importer/` is an initiative of the repository, owned by Mateusz, with its plan in progress; it builds the importer and the walking data of the routing engine, while `osm_import` keeps the reading of the copy and the loading program (`MVP.md`, section How the MVP is built; `docs/standards/decision_registry.md`, resolved entry OpenStreetMap importer ownership and Valhalla data preparation).
- `plans/backend_skeleton/` holds a shape, a PRD and a plan in progress; `plans/accounts/` holds a shape and a PRD awaiting confirmation; `plans/repository_consistency/` holds only a seed. There is still no product code.
- Unmerged work on remote branches: `origin/jmi/odklejka_v1` (the shape and the PRD of `schema_first_revision`), `origin/js/frontend-shape` (one file), `origin/mw` (`bus_station_api_integration`, outside `MVP.md`) and `origin/mw-osm-import` (one commit over the merged work).
- `docs/setup/EMULATOR_SETUP.md` describes the setup of the HarmonyOS toolchain and emulator, but the application directory, the `Makefile` and the version script it names are not in the repository.
- `docs/standards/decision_registry.md` has a new open entry, Hash length reported by Kuba.

## Smallest meaningful scope

One document, `FINAL_CHECKLIST.md`, with ten sets, about forty checks in all, every check with its dependencies and with what of it can be done before they are met; together with the three documents this initiative brings in line with it in the same change: `MVP.md` (requirement 13), `docs/hackathon/challenge_requirements.md` (requirement 20) and the entry HarmonyOS port and the Huawei submission of `docs/standards/decision_registry.md` (section Domain rules or explicit TODO).

The ten sets and the checks they cover, approved by the user on 2026-10-04 (question 12 of the interview); the exact wording of every check, its dependencies and what of it can start at once are settled in the PRD:

1. Clarifications and housekeeping: whether one team may submit to two partner challenges and the Huawei deadline; the time and length of the Kraków pitch and which Kraków set of criteria the jury uses; every unmerged branch with work merged or closed; the rulings still waiting for confirmation in `MVP.md`, section Open decisions and confirmations - Marek, Kuba, Kuber and Adrian, and the thresholds of D-5 confirmed by Mateusz.
2. Backend foundation: `backend_skeleton`, `schema_first_revision`, `accounts` and `address_search`.
3. Open data: `osm_import`, `sample_data` and the step of the loading program that loads the tile archive.
4. Routes: `route_planning`, and O9 through `public_transport_routing`, marked as optional.
5. Community facts, the large initiative `community_facts` in three fragments: reports and geozones; votes and statuses; flags and moderation.
6. Web frontend, `frontend_app` together with `map_tiles`: the route screens (profile, search, result, list); reports, votes and geozones; account, moderation, privacy information and the Polish and English interface; the map (archive, style, fonts); the accessibility check of the main scenario.
7. Hosted demo: `DEPLOYMENT_CONFIG` of `plans/deployment_config/` and the loading of the data; the main scenario end to end on the hosted link; the case of contradictory, incomplete or unavailable data.
8. HarmonyOS port: the initiative of the port with the choice between ArkTS/ArkUI and React Native for OpenHarmony; a client of the same programming interface using at least one capability of the platform; the `.hap` running on an emulator; the build, installation and launch instructions with versions.
9. Official requirements. Kraków: data sources, architecture, business model, running and maintenance, data protection, licences and dependencies, the list of what works and what still needs work. Huawei: the architecture and implementation description in English, `AI_WORKFLOW.md`, the pre-existing and third-party components, the tests of the key scenarios, and a public repository without secrets.
10. Materials and pitch: the four materials of requirement 18; both submissions on HackTribe before the deadline; the pitch with a live demo.

Amended after the interview (requirements 22 - 25): the same change also sets up one new initiative with its seed for every set whose checks no existing initiative covers, gives every initiative of `plans/` a file `STAGE.md` with its stage, and writes the division of the work among the people into `MVP.md` and `TEAM.md`. `osm_importer` joins set 3 and `repository_consistency` joins set 1.

## Out of scope

- Everything after the pitch and the demo before the jury, the deletion of the hosted demo and its data after the results included. The deletion stays a duty of the owner of the repository under `CLAUDE.md`, section Target environment, and is not a check of the list (decided by the user on 2026-10-04, question 2 of the interview).
- The optional features O1 - O8 of the specification (requirement 15).
- Owners of checks, priorities and intermediate times (requirements 8 and 14).
- Doing the work of the checks. The list says what finishes the project; the checks are carried out by their own initiatives or by the people the team assigns, not by this initiative.

## Functional requirements

1. The checklist covers the current initiatives (seed).
2. The checklist covers the things still to be done outside them (seed).
3. The checklist covers a check against the official requirements of both challenges (seed).
4. The checklist covers the pitch presentation (seed).
5. A set is one large initiative and a check one small initiative or a fragment of a large one, with as few of each as the content allows (seed).
6. The project is finished when the pitch and the live demo before the jury are done; the last set of the list ends there (decided by the user on 2026-10-04, question 2 of the interview).
7. The Huawei submission is mandatory and has a set of its own without a go/no-go condition: a `.hap` package running on an emulator or a device, reproducible build instructions, a recorded demo, a public repository and the documentation in English (decided by the user on 2026-10-04, question 3 of the interview). The ruling was given by the owner of the repository in place of the team, which `docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission, names as the one setting the go/no-go; Kuber and Adrian, who carry both the web frontend and the port (`TEAM.md`), confirm it.
8. The list is flat: no priority levels and no intermediate "done by" times. What is dropped when time runs out is decided by the team during the day, not by the list (decided by the user on 2026-10-04, question 4 of the interview).
9. A check is done when its effect works and a person has verified it, for example an acceptance criterion of `plans_finished/mvp/MVP_PRD.md` on the hosted demo. The artifacts of the chain - a PRD, a plan, a review, a move to `plans_finished/` - are not a condition of a check (decided by the user on 2026-10-04, question 5 of the interview).
10. Zero idle time is the most important assumption of the list: every person of the team can move their work forward at every moment of the day. A check starts on a decision or a plan - a contract, a schema, a written agreement - and never waits for the implementation of another check (stated by the user on 2026-10-04, during question 5 of the interview).
11. Every set and every check is described with its dependencies, so that the team can see how much of the work can run in parallel; the tasks of the list are parallelized after it is written (stated by the user on 2026-10-04, after question 9 of the interview).
12. A dependency is soft, not a gate: next to what a check waits for, the list says what of that check can already be done before the dependency is met. A check whose every part waits is the exception the list names explicitly (stated by the user on 2026-10-04, after question 9 of the interview).
13. This initiative rewrites `MVP.md` in the same change: the column Waits for of the section Initiatives and the section Order and critical path name the documents an initiative starts from - the contract, the schema, a plan - instead of the code of another initiative, consistent with requirement 10. `MVP.md` itself requires that a change making one of its items untrue updates it in the same change (`MVP.md`, section Why this document exists) (decided by the user on 2026-10-04, question 9 of the interview).
14. No check names an owner. The list says what is to be done and what it depends on; who takes which check is settled by the team when the work is parallelized (decided by the user on 2026-10-04, question 10 of the interview).
15. O9, routes with public transport, is a check of the list marked as optional: it does not condition the end of the project. The mark is the only exception to the flat list of requirement 8, and it applies to O9 alone (decided by the user on 2026-10-04, question 6 of the interview). The optional features O1 - O8 are not on the list at all, because `MVP.md`, section Scope, and `docs/standards/decision_registry.md`, entry Optional features of the MVP, put them outside the MVP (Agent decision at C:40, without asking).
16. `FINAL_CHECKLIST.md` lives in the root of the repository, next to `MVP.md` and `TEAM.md`; `plans/final_checklist/` keeps only the artifacts of the chain behind it (decided by the user on 2026-10-04, question 1 of the interview).
17. Only Rafał ticks a check, once he has verified its effect in the sense of requirement 9, so that the file has one writer and no merge conflicts (decided by the user on 2026-10-04, question 7 of the interview).
18. The presentation materials are four: a deck in Polish, a PDF of at most 10 slides, which is both the Kraków submission and the deck of the Kraków pitch; a video in Polish, an mp4 of at most 3 minutes in an open repository, for Kraków; a recorded demonstration in English of the `.hap` running on an emulator, for Huawei; and a deck in English prepared before 11:00, in case the Huawei jury invites the team to present (decided by the user on 2026-10-04, question 8 of the interview, after the official PDFs settled the languages: `RULES Cracow Without Barriers.pdf` point 5 and `RULES Imagine What_s Next.pdf` section 4).
19. The facts no document in the repository holds are checks of the list, not questions of this interview: whether one team may submit one project to two partner challenges, the Huawei submission deadline, the time and length of the Kraków pitch, and which of the two Kraków sets of criteria the jury uses (`docs/hackathon/challenge_requirements.md`, Conflicts and open points 4 and 9). They are verified with the organizers or in the HackYeah 2026 schedule, and the list says which other checks depend on each of them (Agent decision at C:40, without asking).
20. This initiative brings `docs/hackathon/challenge_requirements.md` up to date with the official PDFs in the same change: the section Provenance points to `docs/official/`, the Huawei section says the jury may invite teams to present, and the Kraków section says the whole submission is in Polish. The set of the list that checks the official requirements checks them against the updated document (decided by the user on 2026-10-04, question 11 of the interview).
21. The list has the ten sets of the section Smallest meaningful scope, in that order (approved by the user on 2026-10-04, question 12 of the interview).
22. The work is divided among the people as follows, and this initiative writes the division into `MVP.md`, column Owner, and `TEAM.md`, column Works on; the list itself still names no owner (requirement 14). Marek: `backend_skeleton`, `route_planning`, the reports and geozones of `community_facts`, and `public_transport_routing` last. Kuba: the local setup of `backend_skeleton`, `schema_first_revision`, `accounts`, and the votes, statuses, flags and moderation of `community_facts`. Mateusz: `osm_importer`, `osm_import`, `address_search` and `sample_data`, unchanged. Adrian: `frontend_app` and `map_tiles`, and with Rafał the Polish materials and the pitch. Kuber: the HarmonyOS port, the Huawei part of the official requirements and the English demonstration. Rafał: the clarifications, the deployment configuration and the hosted demo, the demo scenario, the Kraków documents and `AI_WORKFLOW.md`, the decks and the submissions. The division was proposed by the agent to take load off Marek and was accepted by the user on 2026-10-04 after the interview; Marek, Kuba, Kuber and Adrian confirm the change of their work, as `MVP.md`, section Open decisions and confirmations, records for other rulings given in their place.
23. Every set whose checks no existing initiative covers gets one new initiative, set up by this initiative with its seed only: set 1, set 7 for the demo scenario and its run next to `deployment_config`, set 8, set 9 and set 10. The name of a new initiative starts with `stage<N>_`, where N is its stage. Existing initiatives keep their names (decided by the user on 2026-10-04, after the interview, against one initiative for every check without one).
24. Every initiative in `plans/`, the existing ones, the new ones and this one, gets a file `STAGE.md` holding its stage number (decided by the user on 2026-10-04, after the interview; the user chose the English name over `etap.md` of the request, because the repository is written in English).
25. A stage is a level of dependency, so that the initiatives of one stage can be carried out in parallel: an initiative of stage N waits only for initiatives of stages below N, initiatives of one stage do not wait for each other, and stage 1 waits for nothing. A wait is a wait of the effect in the sense of requirement 12 - what an initiative needs before its effect can be verified; the work of every stage starts at once on documents (requirement 10) (decided by the user on 2026-10-04, after the interview, against a stage as a wave of the day and against a stage as a stream of work).

## Scenarios: input, flow, expected state after the run

1. Start of the parallel work. Input: `FINAL_CHECKLIST.md` published in the root, six people, no product code. Flow: every person opens the list and takes a check whose input documents already exist - set 1 needs nothing, set 6 starts on `docs/product/api_contract.md` and `docs/product/views.md`, set 9 on the specification and the decided plans, set 8 on the contract. Expected state: nobody waits; every check names the documents it starts from and what of it can be done right away.
2. A dependency not met yet. Input: at 07:00 `osm_import` has no working import yet. Flow: the check of `route_planning` says what waits for the imported data and what does not - the code against `plans_finished/valhalla_routing/` and `docs/product/api_contract.md`. Expected state: the person on `route_planning` keeps working; the dependency changes what can be verified, not what can be written.
3. A fact that removes work. Input: in the morning the organizers answer that one project may be submitted to one partner challenge only. Flow: the check of set 1 that verifies it names the checks that depend on the answer - set 8, the Huawei part of set 9, the English deck and the English demo of set 10. Expected state: Rafał and the team see at once which checks fall away; the decision what to do about it is theirs, not the list's.
4. Ticking during the day. Input: at 08:30 `plan_route` works on the hosted demo and the result screen uses it, without a PRD or a review of `route_planning`. Flow: Rafał verifies the effect and ticks the check. Expected state: the check is done in the sense of requirement 9.
5. The end. Input: after 11:00 the pitch with a live demo has been given before the Kraków jury; O9 is unticked. Flow: Rafał ticks the last check of set 10. Expected state: the project is finished; the unticked O9 does not change that (requirement 15); the deletion of the demo after the results is outside the list.

## Challenging own assumptions

- Is a list of about forty checks realistic with eight hours left and no product code? The list defines what finishes the project; it does not promise that everything on it gets done. Because it is flat (requirement 8), the cuts are made by the team during the day, and the list has to make each cut visible through the dependencies - otherwise dropping one check silently breaks another.
- Does zero idle time hold for Kuber and Adrian? They carry the web frontend, the map tiles and now the mandatory port (`TEAM.md`, requirement 7). The list has no owners (requirement 14), so it cannot spread their load; it can only show that sets 6 and 8 can run in parallel on the same contract. The load is a risk the team settles when it parallelizes.
- Is "a set is a large initiative" true of every set? Sets 1, 9 and 10 are not initiatives of `MVP.md`; they are the things to be done outside the initiatives that the seed asks for. The rule of the seed is read as "a set is a large piece of work", and the PRD keeps the sets 1, 9 and 10 to the same size as the others.
- Is a double submission allowed at all? Nothing in the repository or in the four PDFs says so. Requirement 7 rests on it, so the list puts the check that verifies it first in set 1, with the checks that depend on it named.
- What does "the effect works" mean for a document? For the checks of set 9 and the materials of set 10 the effect is a document or a file a person has read and found complete against the requirement it serves; the PRD writes that criterion into each such check.
- Does this initiative itself go through the full chain? The repository requires shape, PRD and plan before the implementation, and the list has to be out early to serve the day. The chain is kept; how fast its phases go is the user's call at each gate.
- Is the Huawei deadline 11:00? Probably, because the coding of the whole event ends then, but it is not verified; the list treats it as a fact of set 1, not as a given.

## Domain rules or explicit TODO

- TODO: the decision of question 3 removes the variant "no Huawei submission" from `docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission, while the choice between a native ArkTS/ArkUI client and a React Native for OpenHarmony client stays open there. The entry has to say so before `FINAL_CHECKLIST.md` is published, so that the two documents do not contradict each other.
- No initiative of `MVP.md` builds the HarmonyOS client. Requirement 23 closes the gap: this initiative sets up the initiative of the port with its seed, and the first check of set 8 is the choice its shape makes.
- The official PDFs in `docs/official/` against `docs/hackathon/challenge_requirements.md`, read by the agent on 2026-10-04. The summary is accurate on the deliverables, the deadlines, the languages and the judging criteria. What it misses or what has changed:
  - Signal 4: its section Provenance says the PDFs are not stored in the repository, which stopped being true when the user added them to `docs/official/`.
  - `RULES Imagine What_s Next.pdf`, section 5: the Huawei jury may invite selected teams to present or demonstrate their solutions. A live Huawei presentation is therefore by invitation only, while the Kraków rules, point 7, say the competition is to present the solutions and `KRYTERIA Kraków Bez Barier.pdf`, section 6, describes a working demonstration during the presentation.
  - `RULES Cracow Without Barriers.pdf`, point 5: the whole Kraków task solution is submitted to HackTribe in Polish, which covers the PDF and the video as well as the description.
  - `CRITERIA Imagine What_s Next.pdf`, Quality of the demonstration: what cannot run on the emulator (positioning, sensors) is explained in the demo, and mentors have devices on site.
  - None of the four PDFs says when the pitch takes place, how long it is, or whether one team may submit one project to two partner challenges; the general HackYeah 2026 Rules, to which both sets of rules defer, are not in the repository. Whether a double submission is allowed decides whether requirement 7 is possible at all, so it is a fact to verify, not a decision of this initiative.
- The known departures from the Kraków brief - the hosted demo over plain HTTP and the green public transport segment without data of O9 - stay as `MVP.md`, section Known departures from the Kraków brief, records them; the list checks that the Kraków submission states them, it does not reopen them.

## Notes on data, performance and security

- The list holds no address, host, login or secret of the hosted demo in any form (`CLAUDE.md`, section Target environment; `docs/standards/standard_config.md`). Set 7 names the hosted demo, never where it runs.
- The list names no person (requirement 14) and holds no personal data.
- The repository becomes public for the Huawei submission (requirement 7), so everything the list adds is written to be published. The four PDFs of the organizers in `docs/official/` are untracked at 03:20; whether they are committed into a public repository is a decision of the user, which the check of set 9 on the public repository raises without deciding it. Nothing here is legal advice.
- Whether the repository carries a licence stays with `docs/standards/decision_registry.md`, entry Intellectual property between the two challenges and the repository licence; the list does not add a licence file.
- No question of the interview touched a blocking risk category: the list changes no contract, schema, data or permission.

## Open questions

None. The facts no document holds are checks of set 1 (requirement 19), not open questions of this shape.
