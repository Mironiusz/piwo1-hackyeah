# Plan: Final checklist whose completion means the project is finished

Document state: 2026-10-04, plan closed

## Goal

Deliver `plans/final_checklist/FINAL_CHECKLIST_PRD.md` (FR-1 - FR-13, AC-1 - AC-9): write `FINAL_CHECKLIST.md` in the repository root, set up the five new initiatives with their seeds, give every initiative of `plans/` its `STAGE.md`, and bring `MVP.md`, `TEAM.md`, `docs/hackathon/challenge_requirements.md`, `docs/standards/decision_registry.md`, `docs/standards/standard_agentic_workflow.md` and `AI_WORKFLOW.md` in line with them. No code changes; every change is a markdown document.

## Facts

F-1. `plans/` holds fifteen initiative directories - `accounts`, `address_search`, `backend_skeleton`, `community_facts`, `deployment_config`, `final_checklist`, `frontend_app`, `map_tiles`, `osm_import`, `osm_importer`, `public_transport_routing`, `repository_consistency`, `route_planning`, `sample_data`, `schema_first_revision` - and none of them holds a file `STAGE.md`. | cmd:`ls plans/` -> the fifteen names; cmd:`ls plans/*/` -> no `STAGE.md` | 2026-10-04
F-2. No directory whose name starts with `stage` exists in `plans/` or `plans_finished/`. | cmd:`ls plans/ plans_finished/` -> no name starting with `stage` | 2026-10-04
F-3. The table of `MVP.md`, section Initiatives, has the columns Initiative, Owner, Builds and Waits for and twelve rows, the row of `osm_importer` with Mateusz (import) included, added by another session on the same tree before 04:06, after this plan was written; it gives `accounts` and `community_facts` to Marek and `frontend_app` and `map_tiles` to Kuber and Adrian. | doc:`MVP.md` section Initiatives; cmd:`git diff MVP.md` -> the row of `osm_importer` added over `HEAD` | 2026-10-04
F-4. `MVP.md`, section How the MVP is built, records the handoff of the importer and of the walking data of the routing engine to `osm_importer`, and since 04:05 the row of `osm_importer` builds the importer, the import side of D-5 and the import side of D-9, while the row of `osm_import` builds only `read_osm_copy` and the one loading program, which runs the importer of `osm_importer`. | doc:`MVP.md` section How the MVP is built; doc:`MVP.md` section Initiatives | 2026-10-04
F-5. The handoff gives `osm_importer` the importer, the mapping, the reconciliation, their tests and the matching routing data, and leaves `read_osm_copy` and the common loading program with `osm_import`. | doc:`plans_finished/mvp/MVP_PLAN.md` D-20; doc:`plans/osm_importer/OSM_IMPORTER_PLAN.md` D-20 and D-21 | 2026-10-04
F-6. `MVP.md`, section Goal and deadline, calls the prototype the base of a Huawei submission "if the team goes for it". | doc:`MVP.md` section Goal and deadline | 2026-10-04
F-7. `MVP.md`, section Order and critical path, orders the initiatives in five steps by the code of other initiatives, and the sentence under the table of the section Initiatives starts the deployment configuration "once the backend skeleton of `backend_skeleton` exists". | doc:`MVP.md` section Order and critical path; doc:`MVP.md` section Initiatives | 2026-10-04
F-8. `MVP.md`, section Open decisions and confirmations, lists the rulings given in place of Marek, Kuba, Kuber and Adrian and the thresholds of D-5 to be confirmed by Mateusz. | doc:`MVP.md` section Open decisions and confirmations | 2026-10-04
F-9. `TEAM.md`, section Members and roles, has the columns Person, Role and Works on, and gives Kuber and Adrian together the web frontend and the HarmonyOS port. | doc:`TEAM.md` section Members and roles | 2026-10-04
F-10. `docs/hackathon/challenge_requirements.md`, section Provenance, says the PDFs are not stored in the repository; its Huawei section says nothing of an invitation to present, and its Kraków section, Formal deliverables, puts in Polish only the title, the team ID and the description. | doc:`docs/hackathon/challenge_requirements.md` section Provenance; doc:`docs/hackathon/challenge_requirements.md` section Challenge 2, Judging; doc:`docs/hackathon/challenge_requirements.md` section Challenge 1, Formal deliverables | 2026-10-04
F-11. The four official PDFs are tracked by git in `docs/official/`. | cmd:`git ls-files docs/official` -> `CRITERIA Imagine What_s Next.pdf`, `KRYTERIA Kraków Bez Barier.pdf`, `RULES Cracow Without Barriers.pdf`, `RULES Imagine What_s Next.pdf` | 2026-10-04
F-12. The Huawei rules let the jury invite selected teams to present, and the Kraków rules require the whole task solution in Polish. | doc:`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md` section Domain rules or explicit TODO | 2026-10-04
F-13. The registry entry HarmonyOS port and the Huawei submission lists three variants, the last being no Huawei submission, and waits for a go/no-go time. | doc:`docs/standards/decision_registry.md` section Open decisions, entry HarmonyOS port and the Huawei submission | 2026-10-04
F-14. The registry holds the open entries When the initiative of O9 starts its code, Wording of the public transport segment of O9, Hash length reported by Kuba and Initiatives outside MVP.md that overlap its initiatives, the last now about `mw` only. | doc:`docs/standards/decision_registry.md` section Open decisions | 2026-10-04
F-15. `docs/standards/standard_agentic_workflow.md` describes, in its glossary and in section 3.2, only the five chain artifacts of a task as the files of an initiative, and leaves the format of those artifacts to `docs/standards/standard_agent_docs.md`. | doc:`docs/standards/standard_agentic_workflow.md` section 2. Glossary; doc:`docs/standards/standard_agentic_workflow.md` section 3.2. Five task artifacts | 2026-10-04
F-16. `docs/standards/standard_agent_docs.md` is the source of the format of the five chain artifacts and of a memory entry only. | doc:`docs/standards/standard_agent_docs.md` section Why this document exists | 2026-10-04
F-17. A seed quotes a request in another language verbatim, message by message, each with an English translation marked as not part of the record. | doc:`docs/standards/standard_agent_docs.md` section SEED format | 2026-10-04
F-18. The seeds set up by the MVP plan quote the messages of the user and the closed questions of the agent with the chosen answers, under `Source: conversation with the user` and the date. | doc:`plans_finished/mvp/MVP_PLAN.md` D-19; doc:`plans/deployment_config/DEPLOYMENT_CONFIG_SEED.md` section Verbatim content | 2026-10-04
F-19. `AI_WORKFLOW.md`, section Log, holds dated entries with the items Tools, Request, What was done, Why and Note, and `CLAUDE.md` asks that a change to the workflow be recorded there. | doc:`AI_WORKFLOW.md` section Log; doc:`CLAUDE.md` section Task cycle and the agentic system | 2026-10-04
F-20. The prose gate scans every markdown file of the tree, and markdown is formatted by prettier through the make targets `lint-docs` and `format`. | code:`makefile` targets `lint-docs` and `format`; doc:`docs/standards/standard_formatting.md` section Emphasis in prose | 2026-10-04
F-21. No architecture test checks which files an initiative directory holds; the plan contract test reads only plan files. | cmd:`grep plans tests/` -> only `tests/architecture/test_prose_style.py` and `tests/architecture/test_plan_document_contract.py`; code:`tests/architecture/test_plan_document_contract.py` constant `PLAN_GLOB_PATTERNS` | 2026-10-04
F-22. At 03:56 the remote branches with work not in this branch are `jmi/odklejka_v1`, `js/frontend-shape`, `mw` and `mw-osm-import`. | cmd:`git rev-list --count HEAD..<branch>` for every remote branch -> 2, 1, 5 and 1, every other branch 0 | 2026-10-04
F-23. `docs/setup/EMULATOR_SETUP.md` names the application directory `accessway/`, a `Makefile` and `scripts/env.sh`, none of which exists in the repository. | cmd:glob `accessway/**/oh-package.json5`, `Makefile`, `scripts/env.sh` -> no files found | 2026-10-04
F-24. The tile archive of Kraków, the map fonts and the sprites were produced on 2026-10-03 and are kept outside the repository. | doc:`plans/frontend_app/FRONTEND_APP_PACKAGES.md` section Inputs | 2026-10-04
F-25. A point report farther than 15 m from every stretch is shown on the map and changes no route. | doc:`docs/product/specification.md` M3 | 2026-10-04
F-26. The loading program loads the copy with its routing data, the tile archive and the sample reports, and its step is finished when the map of Kraków shows at the public link. | doc:`docs/deployment/hosted_demo.md` section Loading the data | 2026-10-04
F-27. `plans/accounts/` holds a shape and a PRD awaiting confirmation, `plans/backend_skeleton/` a plan in progress, and `plans/osm_importer/` a plan in progress owned by Mateusz. | doc:`plans/accounts/ACCOUNTS_PRD.md` section Business goal; doc:`plans/backend_skeleton/BACKEND_SKELETON_PLAN.md` section Goal; doc:`plans/osm_importer/OSM_IMPORTER_PLAN.md` section Goal | 2026-10-04
F-28. `README.md`, section What is inside, and `CLAUDE.md` with `AGENTS.md` name the documents of the root without `FINAL_CHECKLIST.md`, and `CLAUDE.md` and `AGENTS.md` describe the five chain artifacts of an initiative. | doc:`README.md` section What is inside; doc:`CLAUDE.md` section Task cycle and the agentic system | 2026-10-04

## Decisions

D-1. Form of the list. `FINAL_CHECKLIST.md` opens with the title and the state line, then the sections How to read this list, Stages and one section per set. A check is a task list item `- [ ] <number> <name>`, ticked by turning it into `- [x]`, with three nested items `Done when: ...`, `Waits for: ...` and `Before that: ...` in the wording of PRD FR-5. Agent decision at C:40, without asking: a task list is the form markdown renders as ticks and keeps one line per check to change, so the file has one writer and no conflicts (PRD FR-4).

D-2. The list names no person (PRD AC-2), while `CLAUDE.md` forbids naming a member of the team by role. Who ticks and when is therefore given by reference: the section How to read this list points to `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirements 9 and 17. Agent decision at C:40, without asking: it keeps both rules without naming anybody.

D-3. Form of `STAGE.md`. Five lines: the heading `# Stage`, an empty line, the stage number alone, an empty line, and `Source: FINAL_CHECKLIST.md, section Stages.` Agent decision at C:40, without asking: the number alone on its line is what the request asks for, and the source line says where it comes from (PRD FR-8).

D-4. Where `STAGE.md` is described. In `docs/standards/standard_agentic_workflow.md`: a glossary item Stage and a paragraph at the end of section 3.2. `docs/standards/standard_agent_docs.md` does not change, because it holds the format of the chain artifacts only (F-16) and `STAGE.md` is not one. Agent decision at C:40, without asking.

D-5. Content of a new seed. Each follows F-17 and F-18: `Source: conversation with the user`, `Date: 2026-10-04`, an opening paragraph saying that `plans/final_checklist/` set it up for set N of `FINAL_CHECKLIST.md`, and the section Verbatim content quoting the message of the user that asked for the initiatives and the four closed questions of the agent with the chosen answers, each in Polish with its English translation. The descriptions and previews of the options are left out, and the seed says so. Agent decision at C:40, without asking: it repeats the form of the seeds of the MVP plan.

D-6. `MVP.md` gets a row for `osm_importer`, and the row of `osm_import` keeps only what F-5 leaves it, so that each operation and each decision has one builder (`MVP.md`, section How the MVP is built). Agent decision at C:40, without asking: PRD FR-9 adds the row, and leaving the old text of `osm_import` would give the importer two builders.

D-7. The column Waits for of `MVP.md`, section Initiatives, is renamed Starts from and names documents (PRD FR-9, shape requirement 13). The waits of the effect live in the section Order and critical path as stages. Agent decision at C:40, without asking.

D-8. The PDFs of `docs/official/` are already tracked (F-11), so check 9.5 asks whether they stay in the public repository instead of whether they are committed. Agent decision at C:40, without asking: the decision of the user that the PRD keeps open is the same; only the starting state differs.

D-9. `README.md`, `CLAUDE.md` and `AGENTS.md` do not change (F-28): the PRD does not list them, the chain artifacts they describe stay five, and a missing mention of `FINAL_CHECKLIST.md` is what check 1.6 of the list catches. Agent decision at C:40, without asking.

D-10. `TEAM.md` keeps its columns and gets new text in the column Works on only, plus one sentence under the table pointing to shape requirement 22. Agent decision at C:40, without asking.

## Scope of changes

1. New `STAGE.md`, in the form of D-3, in each of these fifteen directories, with this number: `plans/backend_skeleton/` 1, `plans/final_checklist/` 1, `plans/schema_first_revision/` 2, `plans/address_search/` 2, `plans/accounts/` 3, `plans/osm_importer/` 3, `plans/osm_import/` 4, `plans/route_planning/` 4, `plans/community_facts/` 4, `plans/sample_data/` 5, `plans/map_tiles/` 5, `plans/frontend_app/` 5, `plans/public_transport_routing/` 5, `plans/deployment_config/` 6, `plans/repository_consistency/` 7. Nothing else in these directories changes.

2. Five new directories, each with a seed of D-5 and a `STAGE.md` of D-3:
   - `plans/stage1_clarifications/STAGE1_CLARIFICATIONS_SEED.md`, title `# Seed: Clarifications and housekeeping of the final checklist`, set 1; `STAGE.md` 1.
   - `plans/stage5_harmonyos_port/STAGE5_HARMONYOS_PORT_SEED.md`, title `# Seed: HarmonyOS port`, set 8; `STAGE.md` 5.
   - `plans/stage6_official_requirements/STAGE6_OFFICIAL_REQUIREMENTS_SEED.md`, title `# Seed: Official requirements of both challenges`, set 9; `STAGE.md` 6.
   - `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_SEED.md`, title `# Seed: Demo scenario and its run on the hosted demo`, set 7, checks 7.2 and 7.3; `STAGE.md` 7.
   - `plans/stage8_materials_and_pitch/STAGE8_MATERIALS_AND_PITCH_SEED.md`, title `# Seed: Presentation materials, submissions and the pitch`, set 10; `STAGE.md` 8.

   The quoted user message is, verbatim: `wymyśliłem jeszcze dodate do inicjatywy. Chcę, żeby z każdego zadania powstały inicjatywy. Mają mieć na początku dopisek, który równoległy etap realizują. Niezmieniaj nazw istniejących inicjatyw, ale dodaj też do każdej plik etap.md, gdzie będzie numer etapu`. The four questions and answers are those of the agent of 2026-10-04: what the number of a stage means, answered `poziom zależności, czyli etapy mająbyć wykonywalne równolegle`; which new initiatives come from the sets, answered `Jedna na zestaw (Recommended)`; the name of the file with the stage, answered `STAGE.md (Recommended)`; the prefix of a new name, answered `stage1_ (Recommended)`.

3. New `FINAL_CHECKLIST.md` in the repository root, in the form of D-1:
   - Title `# Final checklist` and the line `Document state: 2026-10-04`.
   - Section `## How to read this list`: the project is finished when check 10.6 is ticked; a check is done when its effect works and a person has verified it, and who ticks is in `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirements 9 and 17 (D-2); the list is flat, with no owner, priority or intermediate time, and who carries what is in `MVP.md` and `TEAM.md`; check 4.2 is the only optional one; Waits for names what the effect needs, Before that what can be done at once; a stage tells when the effect of an initiative can be verified, never when its work starts; the source is `plans/final_checklist/`.
   - Section `## Stages`: the table of PRD FR-6, with the rule of FR-6 in one sentence above it.
   - Sections `## Set 1. Clarifications and housekeeping` to `## Set 10. Materials and pitch`, each opening with the line of the initiatives of PRD FR-5 and holding its checks in the wording of FR-5, with D-8 applied to check 9.5.

4. `MVP.md`:
   - Section Goal and deadline: the end of the second sentence, from "and the base of a Huawei submission", says the prototype is the base of the Huawei submission, which is mandatory, with a HarmonyOS client of the same programming interface built by `plans/stage5_harmonyos_port/` (`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7).
   - Section How the MVP is built: a closing paragraph saying that what finishes the project, the checks and the stage of every initiative are in `FINAL_CHECKLIST.md`, and that each initiative holds its stage in its `STAGE.md`.
   - Section Initiatives: the column Waits for renamed Starts from (D-7), with these documents: `backend_skeleton` - its plan, D-1, D-7, D-14; `schema_first_revision` - `docs/product/schema.md`, D-7, D-11; `osm_import` - `docs/deployment/hosted_demo.md` section Loading the data, `docs/product/api_contract.md` section OpenStreetMap copy, D-14; new row `plans/osm_importer/` - its plan, D-4, D-5, `docs/product/schema.md`; `route_planning` - `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md`, `docs/product/api_contract.md` section Route, `docs/product/schema.md`; `address_search` - D-3, `docs/product/api_contract.md` section Address search; `community_facts` - `docs/product/api_contract.md` sections Facts and Moderation, `docs/product/schema.md`, D-11, and the recognition of the actor and of the moderator role written down by `accounts`; `accounts` - its PRD, D-8, `docs/product/api_contract.md` sections Sessions and actors and Accounts, `docs/product/schema.md`; `frontend_app` - `docs/product/api_contract.md`, `docs/product/views.md`, `docs/product/interface_texts.md`, `plans/frontend_app/FRONTEND_APP_PACKAGES.md` and the mocks of the views; `map_tiles` - `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-5 and D-6, and for its loading step the form of a step written down by `osm_import`; `sample_data` - `docs/product/schema.md`, the demo scenario of check 7.2 of `FINAL_CHECKLIST.md` and the form of a step written down by `osm_import`; `public_transport_routing` - `plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-12 and its interface in `docs/product/api_contract.md`, with the start of its code decided in the registry entry When the initiative of O9 starts its code.
   - Section Initiatives, column Owner: `community_facts` - Marek (backend) for the reports and geozones, Kuba (db) for the votes, statuses, flags and moderation; `accounts` - Kuba (db); `frontend_app` and `map_tiles` - Adrian (frontend); the new row `osm_importer` - Mateusz (import). The row `osm_import` builds the operation `read_osm_copy` and the one loading program, consuming `osm_importer` (D-6); the row `osm_importer` builds what F-5 gives it, citing `plans/osm_importer/OSM_IMPORTER_PLAN.md` D-20 and `plans_finished/mvp/MVP_PLAN.md` D-20.
   - The sentence under the table: the deployment configuration is written by Rafał in the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`, starting from `docs/deployment/hosted_demo.md`, D-10 and D-14, and places the services as D-14 decides.
   - Section Order and critical path, rewritten: every initiative starts at once from its column Starts from and none waits for the code of another to begin (shape requirement 10); what an initiative waits for is the moment its effect can be verified, which sets its stage in `FINAL_CHECKLIST.md`, section Stages, and in its `STAGE.md`; then the initiatives of this file by stage, 1 `backend_skeleton`, 2 `schema_first_revision` and `address_search`, 3 `accounts` and `osm_importer`, 4 `osm_import`, `route_planning` and `community_facts`, 5 `sample_data`, `map_tiles`, `frontend_app` and `public_transport_routing`, 6 the deployment configuration of `plans/deployment_config/`. The paragraph on the critical path keeps its sentence on the critical tests of D-8 of `plans_finished/local_database/LOCAL_DATABASE_PLAN.md` and names `osm_importer` next to `backend_skeleton` and `schema_first_revision`.
   - Section Open decisions and confirmations: a new first item, the division of the work of `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22, given by the user in place of Marek, Kuba, Kuber and Adrian, whose work it changes, to be confirmed by them in check 1.4 of `FINAL_CHECKLIST.md`.
   - Section Sources: an item for `FINAL_CHECKLIST.md`.

5. `TEAM.md`, section Members and roles, column Works on (D-10): Rafał - leads the team, merges the work of the others and watches over the whole; the clarifications, the deployment configuration and the hosted demo, the demo scenario, the Kraków documents and `AI_WORKFLOW.md`, the decks and the submissions, and with Adrian the Polish materials and the pitch. Kuber - the HarmonyOS port, the Huawei part of the official requirements and the English demonstration. Adrian - the web frontend and the map tiles, and with Rafał the Polish materials and the pitch. Kuba - the database, the accounts, and the votes, statuses, flags and moderation of the community facts. Marek - the backend skeleton, route planning, the reports and geozones of the community facts, and last the optional routes with public transport. Mateusz - the integrations: the import of open data, the sample data and the calls to external systems. Under the table one sentence: the column follows the division of the work of `plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 22.

6. `docs/hackathon/challenge_requirements.md`:
   - Section Provenance: the sentence "The PDFs are not stored in the repository and they remain the authority." becomes: the PDFs are stored in `docs/official/` since 2026-10-04 and remain the authority.
   - Section Challenge 1, Formal deliverables: a new first item, the whole task solution - the description, the presentation and the video included - is submitted on HackTribe in Polish (RULES, point 5).
   - Section Challenge 2, Judging: a closing sentence, the jury may invite selected teams to present or demonstrate their solutions (RULES, section 5), so a live Huawei presentation happens only on invitation.
   - Section What both challenges need, side by side, row Presentation, column Huawei: not required; a presentation only on the invitation of the jury.

7. `docs/standards/decision_registry.md`, entry HarmonyOS port and the Huawei submission, same title: Affects names the architecture of the HarmonyOS client and the time left for the Kraków deliverables; Variants keeps the native ArkTS/ArkUI client and the React Native for OpenHarmony client, drops no Huawei submission, keeps the sentences on the web build and on the embedding, and adds that the Huawei submission is mandatory since 2026-10-04 (`plans/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 7); Blocks names the choice the shape of `plans/stage5_harmonyos_port/` makes; Condition says the entry moves to Resolved decisions when that shape chooses the client, check 8.1 of `FINAL_CHECKLIST.md`, and keeps the note on the hours a `.hap` package, its instructions and a recorded demo need.

8. `docs/standards/standard_agentic_workflow.md` (D-4): in section 2. Glossary, after the item REVIEW, an item Stage - the level of dependency of an initiative in `FINAL_CHECKLIST.md`, kept in its `STAGE.md`, see section 3.2. At the end of section 3.2, a paragraph: an initiative on the list of `FINAL_CHECKLIST.md` also holds `STAGE.md` with its stage, at which it waits only for initiatives of lower stages; the file is not a chain artifact and no skill writes it; the list is its source, so a changed wait of the list updates it in the same change, and an initiative that enters the list later gets it when it is added; its form is that of D-3; it moves with its initiative (ch. 4.6).

9. `AI_WORKFLOW.md`, section Log: a last entry `### 2026-10-04 - Final checklist, stages of the initiatives and division of the work`, with the items Tools (Claude Code with Claude Opus 5.5, the skills `plan-shape`, `plan-prd` and `plan-implement`), Request summarized from Polish, What was done (the list, the five initiatives, the twenty `STAGE.md` files, the division of the work in `MVP.md` and `TEAM.md`), Why (zero idle time, and a stage per initiative so the team sees what runs in parallel) and Note (`STAGE.md` is described in section 3.2 of the agentic workflow standard).

## Rollout order

1. Scope steps 1 and 2: the twenty `STAGE.md` files and the five seeds.
2. Scope step 3: `FINAL_CHECKLIST.md`.
3. Scope steps 4 and 5: `MVP.md` and `TEAM.md`.
4. Scope steps 6 and 7: `docs/hackathon/challenge_requirements.md` and `docs/standards/decision_registry.md`.
5. Scope steps 8 and 9: `docs/standards/standard_agentic_workflow.md` and `AI_WORKFLOW.md`.
6. `npx --no-install prettier --write` on every file of steps 1 - 9, then `python -m pytest tests/architecture` and `npx --no-install prettier --check "**/*.md"`.
7. Check AC-4 by listing `plans/*/STAGE.md` against the table of PRD FR-6.

Steps of a human:

- Rafał: commit, push and the merge request into `dev`, which the agent does not do (`CLAUDE.md`, section Working with git).
- Marek, Kuba, Kuber and Adrian: the confirmation of the division of the work, check 1.4 of the list.

## Definition of Done

- AC-1 - AC-9 of the PRD hold.
- Twenty `STAGE.md` files exist, each with the number of PRD FR-6.
- The architecture tests and the prettier check pass.
- No existing seed, shape, PRD or plan outside `plans/final_checklist/` changed, and no existing initiative was renamed.
- `plans/final_checklist/FINAL_CHECKLIST_REVIEW.md` records the run.

## Risks

- `MVP.md` and the directories of `accounts`, `backend_skeleton` and `osm_importer` are edited by other sessions at the same time (F-27), so the merge request may conflict in `MVP.md`; the change touches only the sections of scope step 4.
- The prefix of a new initiative is fixed while its stage may change later; the list and `STAGE.md` prevail (PRD, Risks and notes).
- The stage numbers are written by hand in twenty files and two tables; step 7 of the rollout compares them once, and a later change of a wait has to update all of them together (PRD FR-8).
- Check 8.3 starts from a setup document whose files are missing (F-23).

## Open questions

None. The PRD was approved on 2026-10-04 and every decision above follows from it or from the facts.

## Supplementary files

- `plans/final_checklist/FINAL_CHECKLIST_PRD.md`, FR-5 and FR-6: the wording of every check and the table of stages that scope step 3 writes into the list.
