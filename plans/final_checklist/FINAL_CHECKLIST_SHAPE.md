# Shape: Final checklist whose completion means the project is finished

Document state: 2026-10-04, interview in progress
Regulator: C:40

## Problem

The team has no single list that says when the project is finished. The work of the day is spread over twelve initiatives of `MVP.md`, the deliverables of two challenges in `docs/hackathon/challenge_requirements.md`, open decisions in `docs/standards/decision_registry.md` and a presentation that has no document yet. Without one list nobody can see what is left, what can be dropped and in what order to do it, and the request says what the team does today depends on it.

The result is `FINAL_CHECKLIST.md`: sets of tasks, each with a few checks. A set is one large initiative, a check is one small initiative or a fragment of a large one, split so that there are not too many of either (seed).

## Recipient and trigger

The team of `TEAM.md`, led by Rafał, on the last day of the hackathon, 4 October 2026. The trigger is the request of the seed, made at 02:53 with about eight hours left to the Kraków deadline of 11:00.

## Current state

Verified in the repository and on `origin/dev` at 02:53 on 2026-10-04:

- There is no product code yet: no `frontend/`, no `api/`, `service/`, `data/` or `worker/` on `origin/dev`. What exists is `valhalla/` with its image workflow, the core gates in `tests/architecture/` and the documentation (`README.md`, section What is inside: "There is no product code yet").
- The twelve initiatives of `MVP.md`, section Initiatives, each hold only a seed in `plans/<name>/`, except `plans/frontend_app/`, which also holds the draft `FRONTEND_APP_PACKAGES.md`.
- Unmerged work on remote branches: `origin/md/fast-setup` and `origin/mw-osm-import` carry a shape and a PRD of `backend_skeleton` and a full chain of a task `osm_importer` (seed, shape, PRD, plan) that overlaps `osm_import`; `origin/jmi/odklejka_v1` carries a shape and a PRD of `schema_first_revision`; `origin/mw` carries an initiative `bus_station_api_integration` outside `MVP.md`, with `docs/apis/msip_stops.md`; `origin/js/frontend-shape` changes one file.
- The design briefs and mocks of four views are in `.impeccable/briefs/views/`.
- The deliverables of both challenges are listed in `docs/hackathon/challenge_requirements.md`; the Kraków submission is due at 11:00 on 4 October on HackTribe. The Huawei deadline is not in the PDFs (Conflicts and open points, item 9); public sources found by the agent at 02:53 confirm only that the coding of the whole event ends at 11:00 on 4 October.
- The four official PDFs of the challenges were added by the user on 2026-10-04 to `docs/official/` (untracked at 03:20): `KRYTERIA Kraków Bez Barier.pdf`, `RULES Cracow Without Barriers.pdf`, `CRITERIA Imagine What_s Next.pdf` and `RULES Imagine What_s Next.pdf`. The agent read all four on 2026-10-04; what they add to `docs/hackathon/challenge_requirements.md` is in the section Domain rules or explicit TODO.
- Open decisions that touch the submissions: the HarmonyOS port and the Huawei submission, waiting for a go/no-go time, and the intellectual property between the two challenges and the repository licence, waiting for the organizers (`docs/standards/decision_registry.md`).

## Smallest meaningful scope

From the seed: one document, `FINAL_CHECKLIST.md`, with sets of tasks and a few checks in each, covering at least the current initiatives, the things still to be done, a check against the official requirements and the pitch presentation.

## Out of scope

- Everything after the pitch and the demo before the jury, the deletion of the hosted demo and its data after the results included. The deletion stays a duty of the owner of the repository under `CLAUDE.md`, section Target environment, and is not a check of the list (decided by the user on 2026-10-04, question 2 of the interview).

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

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

## Domain rules or explicit TODO

- TODO: the decision of question 3 removes the variant "no Huawei submission" from `docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission, while the choice between a native ArkTS/ArkUI client and a React Native for OpenHarmony client stays open there. The entry has to say so before `FINAL_CHECKLIST.md` is published, so that the two documents do not contradict each other.
- TODO: no initiative of `MVP.md` builds the HarmonyOS client, so the port has no owner document yet; the list has to name that gap instead of pointing to an initiative that does not exist.
- The official PDFs in `docs/official/` against `docs/hackathon/challenge_requirements.md`, read by the agent on 2026-10-04. The summary is accurate on the deliverables, the deadlines, the languages and the judging criteria. What it misses or what has changed:
  - Signal 4: its section Provenance says the PDFs are not stored in the repository, which stopped being true when the user added them to `docs/official/`.
  - `RULES Imagine What_s Next.pdf`, section 5: the Huawei jury may invite selected teams to present or demonstrate their solutions. A live Huawei presentation is therefore by invitation only, while the Kraków rules, point 7, say the competition is to present the solutions and `KRYTERIA Kraków Bez Barier.pdf`, section 6, describes a working demonstration during the presentation.
  - `RULES Cracow Without Barriers.pdf`, point 5: the whole Kraków task solution is submitted to HackTribe in Polish, which covers the PDF and the video as well as the description.
  - `CRITERIA Imagine What_s Next.pdf`, Quality of the demonstration: what cannot run on the emulator (positioning, sensors) is explained in the demo, and mentors have devices on site.
  - None of the four PDFs says when the pitch takes place, how long it is, or whether one team may submit one project to two partner challenges; the general HackYeah 2026 Rules, to which both sets of rules defer, are not in the repository. Whether a double submission is allowed decides whether requirement 7 is possible at all, so it is a fact to verify, not a decision of this initiative.

## Notes on data, performance and security

## Open questions

12. Which sets the list has and which checks go into each. `Block: no`
