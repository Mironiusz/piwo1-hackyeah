# Final checklist

Document state: 2026-10-04

## How to read this list

- The project is finished when check 10.6 is ticked.
- A check is done when its effect works and a person has verified it; the artifacts of the chain - a PRD, a plan, a review, a move to `plans_finished/` - are not a condition. Who verifies and ticks a check is set in `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirements 9 and 17. A check is ticked by turning its `- [ ]` into `- [x]`.
- The list is flat: no check has an owner, a priority or an intermediate time, and the only times it names are the deadlines of the challenges. Who carries which initiative is in `MVP.md`, section Initiatives, and in `TEAM.md`.
- Check 4.2 is the only optional check; it does not condition the end of the project.
- Every check names its effect and, where a set has more than one initiative, the initiative that delivers it. Done when is the effect a person verifies. Waits for names the checks whose effect it needs before its own effect can be verified. Before that says what of the check can be done at once and which documents it starts from.
- A stage tells when the effect of an initiative can be verified, never when its work starts: the work of every stage starts at once on documents.
- A reference MVP AC-n is an acceptance criterion of `plans_finished/mvp/MVP_PRD.md`, Valhalla AC-n one of `plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md`, and D-n a technical decision of `MVP.md`.
- The source of this list is `plans_finished/final_checklist/`.

## Stages

An initiative waits for another when one of its checks waits for a check of the other; its stage is one more than the highest stage of the initiatives it waits for, and 1 when it waits for none, so the initiatives of one stage never wait for each other and can be carried out in parallel. Each initiative holds its stage in its `STAGE.md`.

| Stage | Initiatives                                                                                     | Waits for, at the stage below                                        |
| ----- | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| 1     | `backend_skeleton`, `schema_first_revision`, `stage1_clarifications`, `final_checklist`         | Nothing.                                                             |
| 2     | `address_search`, `accounts`, `osm_importer`, `community_facts`                                 | `backend_skeleton`, `schema_first_revision`.                         |
| 3     | `osm_import`, `route_planning`, `community_facts_api`                                           | `osm_importer`, `accounts`, `community_facts`.                       |
| 4     | `sample_data`, `map_tiles`, `frontend_app`, `public_transport_routing`, `stage5_harmonyos_port` | `osm_import`, `route_planning`, `community_facts_api`.               |
| 5     | `deployment_config`, `stage6_official_requirements`                                             | `sample_data`, `map_tiles`, `frontend_app`, `stage5_harmonyos_port`. |
| 6     | `stage7_demo_scenario`, `repository_consistency`                                                | `deployment_config`, `stage6_official_requirements`.                 |
| 7     | `stage8_materials_and_pitch`                                                                    | `stage7_demo_scenario`.                                              |

## Set 1. Clarifications and housekeeping

Initiatives: `stage1_clarifications`, `repository_consistency`.

- [ ] 1.1 Double submission and the Huawei deadline (`stage1_clarifications`)
  - Done when: Whether one team may submit one project to both partner challenges, and the Huawei submission deadline, are recorded with their source in `docs/hackathon/challenge_requirements.md`.
  - Waits for: Nothing.
  - Before that: Everything, at once. Depending on the answer: set 8, checks 9.4, 10.3 and 10.4 and the Huawei part of 10.5.
- [ ] 1.2 The Kraków pitch (`stage1_clarifications`)
  - Done when: The time and length of the Kraków pitch and which of the two Kraków sets of criteria the jury uses are recorded with their source in the same document.
  - Waits for: Nothing.
  - Before that: Everything, at once. Depending on it: checks 10.1 and 10.6.
- [ ] 1.3 Unmerged branches (`stage1_clarifications`)
  - Done when: Every remote branch carrying work of the day is merged into `dev` or closed - on 2026-10-04 at 03:56 these were `jmi/odklejka_v1`, `js/frontend-shape`, `mw-osm-import` and `mw` - and the registry entry on the initiatives outside `MVP.md` is settled for `mw`.
  - Waits for: Nothing.
  - Before that: Everything, at once. Check 2.2 starts from the shape and the PRD on `jmi/odklejka_v1`.
- [ ] 1.4 Confirmations (`stage1_clarifications`)
  - Done when: Every ruling `MVP.md`, section Open decisions and confirmations, lists as given in place of a member of the team, the division of the work included, and the thresholds of D-5 are confirmed or changed by the people that section names - among them the contract of O9 in `docs/product/api_contract.md`, confirmed by Marek, Adrian and Kuber, and the two rulings of O9, the parallel start and the wording of the exception, confirmed by Marek.
  - Waits for: Nothing.
  - Before that: Everything, at once.
- [ ] 1.5 Decisions that block checks (`stage1_clarifications`)
  - Done when: The registry entries on when the code of O9 starts, on the wording of its public transport segment and on the hash length are resolved by the people they name, or the dependent check is recorded as dropped.
  - Waits for: Nothing.
  - Before that: Everything, at once. Check 4.2 depends on the first two. The third was resolved on 2026-10-04 by `schema_first_revision`, so check 2.2 no longer waits for this check (`docs/standards/decision_registry.md`, entry Hash length reported by Kuba). The first two were resolved on 2026-10-04 by Rafał in `public_transport_routing`, Marek's confirmation still to come in check 1.4 (`docs/standards/decision_registry.md`, entries When the initiative of O9 starts its code and Wording of the public transport segment of O9).
- [ ] 1.6 Consistency of the repository (`repository_consistency`)
  - Done when: At the moment of the submissions the repository and its documentation contradict each other nowhere, or every contradiction left is recorded.
  - Waits for: 7.1, 9.4, 9.5.
  - Before that: A first pass at once on the current state, repeated on the last documents of the day.

## Set 2. Backend foundation

Initiatives: `backend_skeleton`, `schema_first_revision`, `accounts`, `address_search`.

- [ ] 2.1 `backend_skeleton`
  - Done when: The backend of D-1 and D-14 starts locally with the local database of D-7 and its revision tooling, and the critical tests of the local database that do not check the first revision pass.
  - Waits for: Nothing.
  - Before that: Everything, from its plan.
- [x] 2.2 `schema_first_revision`
  - Done when: The first revision builds the target schema of `docs/product/schema.md` on an empty local database, and its tests and the critical tests that check it pass.
  - Waits for: Nothing.
  - Before that: The revision and its tests written from `docs/product/schema.md` and D-11.
- [ ] 2.3 `accounts`
  - Done when: On the running service an account is created, logged into, read and deleted (MVP AC-11), an invalid or expired session is refused, and a moderator request is refused for an account without the role.
  - Waits for: 2.2.
  - Before that: The code written from `docs/product/api_contract.md`, sections Sessions and actors and Accounts, D-8 and the PRD of `accounts`. The way other operations recognize the actor and the moderator role is written down first, because checks 5.1 and 5.3 start from it.
- [ ] 2.4 `address_search`
  - Done when: An address in Kraków is found through the service, and an unavailable search gives its plain message (the address part of MVP AC-2).
  - Waits for: 2.1.
  - Before that: The code written from D-3 and `docs/product/api_contract.md`, section Address search.

## Set 3. Open data

Initiatives: `osm_importer`, `osm_import`, `sample_data`, and the loading step of `map_tiles`.

- [ ] 3.1 `osm_importer`
  - Done when: The copy of the OpenStreetMap data of Kraków is imported with the barriers and amenities of D-5, and the walking data of the routing engine are prepared from it, as `plans_finished/osm_importer/` decides.
  - Waits for: 2.2.
  - Before that: The code written from its plan, D-4 and D-5; the form of the data check 4.1 reads agreed with it.
- [ ] 3.2 `osm_import`
  - Done when: The date of the copy is readable through the service, and the one loading program of `docs/deployment/hosted_demo.md` loads the copy with its routing data.
  - Waits for: 3.1.
  - Before that: The form of a step of the loading program written down first, because checks 3.3 and 3.4 add their steps to it.
- [ ] 3.3 `sample_data`
  - Done when: The sample reports and geozones of the demo district Czyżyny, marked as sample data, are loaded by the loading program, including the contradiction between OpenStreetMap and a user report that the demo scenario needs (MVP AC-17).
  - Waits for: 3.2.
  - Before that: The data written from `docs/product/schema.md` and from the demo scenario of check 7.2.
- [ ] 3.4 `map_tiles`, the loading step
  - Done when: The loading program loads the tile archive.
  - Waits for: 3.2.
  - Before that: The archive, the style, the fonts and the sprites of check 6.4 exist.

## Set 4. Routes

Initiatives: `route_planning`, and O9 through `public_transport_routing`.

- [ ] 4.1 `route_planning`
  - Done when: On the running service a walking route in Kraków is planned for a profile, with the segment states, the alternative around unverified barriers, the case without a route that avoids the barriers, the list for the route and the plain message when routing does not answer (MVP AC-2 - AC-4, AC-9, AC-10, AC-16; Valhalla AC-1 - AC-7, AC-12).
  - Waits for: 3.1.
  - Before that: The code written from `plans_finished/valhalla_routing/` and `docs/product/api_contract.md`, section Route.
- [ ] 4.2 `public_transport_routing`, optional
  - Done when: A route with the public transport of ZTP Kraków is planned on the running service (Valhalla AC-8 - AC-11, AC-13). The check does not condition the end of the project.
  - Waits for: 4.1, 3.1, 1.5.
  - Before that: Its interface written into `docs/product/api_contract.md`; the code as far as check 1.5 lets it start.

## Set 5. Community facts

Initiatives: `community_facts_api` in three fragments, on the data layer of `community_facts`.

- [ ] 5.1 Reports and geozones
  - Done when: On the running service a point report and a geozone are saved once even when the save is repeated, and are shown with their source, date and status (MVP AC-5, AC-7, AC-14 for reports).
  - Waits for: 2.2, 2.3.
  - Before that: The code written from `docs/product/api_contract.md`, section Facts, `docs/product/schema.md`, the recognition of the actor written down in check 2.3 and the data operations written down by `community_facts`.
- [ ] 5.2 Votes and statuses
  - Done when: Confirmations and denials, with and without an account, change the status of a fact by the rules of M4 (MVP AC-6, AC-12).
  - Waits for: 2.2, 5.1.
  - Before that: The rules of the statuses written from D-11 and `docs/product/schema.md`.
- [ ] 5.3 Flags and moderation
  - Done when: A fact is flagged, a moderator sees it without anything about its author, hides it and restores it (MVP AC-13).
  - Waits for: 2.3, 5.1.
  - Before that: The code written from `docs/product/api_contract.md`, section Moderation.

## Set 6. Web frontend

Initiatives: `frontend_app` together with `map_tiles`.

- [ ] 6.1 Route screens (`frontend_app`)
  - Done when: The profile of needs, the search, the route result and the list work in the browser against the running service (MVP AC-1 - AC-4, AC-9, AC-10, AC-16).
  - Waits for: 4.1, 2.4.
  - Before that: The screens built against `docs/product/api_contract.md`, `docs/product/views.md`, `docs/product/interface_texts.md` and the mocks of the views.
- [ ] 6.2 Reports, votes and geozones (`frontend_app`)
  - Done when: Reporting, voting and the geozones work in the browser against the running service, with source, date, status and the sample data mark (MVP AC-5 - AC-7, AC-14, AC-17).
  - Waits for: 5.1, 5.2.
  - Before that: The same documents as check 6.1.
- [ ] 6.3 Account, moderation, privacy and languages (`frontend_app`)
  - Done when: The account, the moderation, the privacy information and the Polish and English interface work in the browser against the running service (MVP AC-11, AC-13, AC-18, AC-19).
  - Waits for: 2.3, 5.3.
  - Before that: The same documents as check 6.1.
- [x] 6.4 The map (`frontend_app`, `map_tiles`)
  - Done when: The map of Kraków is drawn in the app from the tile archive, the style, the fonts and the sprites served by the project, and nothing is fetched from outside during the demo (D-6).
  - Waits for: Nothing.
  - Before that: Everything; the archive, the fonts and the sprites were produced on 2026-10-03.
- [ ] 6.5 Accessibility of the main scenario (`frontend_app`)
  - Done when: The keyboard, a screen reader, the contrast, the segment states told apart without color, the width of a phone and the switch of the language are checked on the main scenario (MVP AC-15), with the list of what works and what still needs work.
  - Waits for: 6.1.
  - Before that: The path of the check prepared from `docs/product/user_journeys.md`.

## Set 7. Hosted demo

Initiatives: `deployment_config`, `stage7_demo_scenario`.

- [ ] 7.1 `deployment_config`
  - Done when: The hosted demo stands up from its configuration, the loading program loads the data on it, and the map of Kraków shows at the public link (`docs/deployment/hosted_demo.md`, section Loading the data).
  - Waits for: 2.1, 3.2, 3.3, 3.4, 6.1.
  - Before that: The configuration written from `docs/deployment/hosted_demo.md`, D-10 and D-14.
- [ ] 7.2 The main scenario end to end (`stage7_demo_scenario`)
  - Done when: The demo scenario is written - the profile, a route in Czyżyny, the facts with their source, date and status, the sample data marked as such - and runs end to end on the hosted link as the Kraków brief validates it.
  - Waits for: 7.1, 6.1, 6.2.
  - Before that: The scenario written at once; checks 3.3 and 10.2 start from it.
- [ ] 7.3 Contradictory, incomplete or unavailable data (`stage7_demo_scenario`)
  - Done when: On the hosted link the scenario shows the contradiction between OpenStreetMap and a user report and a stretch with incomplete data, and missing information is never shown as accessible; the plain message of unanswered routing is checked outside the hosted link (`MVP.md`, section Known departures from the Kraków brief).
  - Waits for: 7.1, 3.3, 6.2.
  - Before that: The facts that show it chosen in the scenario of check 7.2.

## Set 8. HarmonyOS port

Initiatives: `stage5_harmonyos_port`.

- [ ] 8.1 The choice of the client
  - Done when: The initiative of the port settles the choice between the two variants of the registry entry HarmonyOS port and the Huawei submission, and which operations of the programming interface the client calls; the entry is resolved.
  - Waits for: Nothing.
  - Before that: Everything, at once.
- [ ] 8.2 The client
  - Done when: A client of the same programming interface, using at least one capability of the platform, plans a route for a profile against the running service.
  - Waits for: 8.1, 4.1.
  - Before that: The client built against `docs/product/api_contract.md`.
- [ ] 8.3 The package on an emulator
  - Done when: The `.hap` package runs on an emulator.
  - Waits for: 8.2.
  - Before that: The toolchain and the emulator set up from `docs/setup/EMULATOR_SETUP.md`, after the files it names and the repository lacks are added or the document is corrected.
- [ ] 8.4 The instructions
  - Done when: The build, installation and launch instructions, with versions, reproduce the package from the README alone.
  - Waits for: 8.3.
  - Before that: The instructions written together with check 8.2.

## Set 9. Official requirements

Checked against `docs/hackathon/challenge_requirements.md`. Initiatives: `stage6_official_requirements`.

- [ ] 9.1 Kraków, data and architecture
  - Done when: The data sources with their terms, freshness, reliability and unavailability, and the architecture that separates the acquisition of data from its presentation, with the way to add a source, a category and a city, are described in the repository.
  - Waits for: Nothing.
  - Before that: Everything, from the specification and the decided plans; compared with the built state before 10.5.
- [ ] 9.2 Kraków, business and operation
  - Done when: The business model and the development options, the running and maintenance outside the infrastructure of the city with its costs, the data protection with the known departures of `MVP.md`, and the licences and dependencies, the ODbL included, are described.
  - Waits for: Nothing.
  - Before that: Everything, at once.
- [ ] 9.3 Kraków, what works
  - Done when: The list of what already works and what still needs work, which the brief asks for, is written.
  - Waits for: 6.5.
  - Before that: The items that do not depend on the accessibility check.
- [ ] 9.4 Huawei, the description
  - Done when: The architecture and implementation description in English, the pre-existing and third-party components, the tests of the key scenarios pointed to where their initiatives delivered them, and a complete `AI_WORKFLOW.md`.
  - Waits for: 8.4.
  - Before that: `AI_WORKFLOW.md` and the components, at once.
- [ ] 9.5 Public repository without secrets
  - Done when: The repository is public for the submission and holds no address, host, login, secret or personal data, and the user has decided whether the official PDFs of `docs/official/`, already tracked by git, stay in the public repository.
  - Waits for: Nothing.
  - Before that: The search for secrets at once, repeated before 10.5.

## Set 10. Materials and pitch

Initiatives: `stage8_materials_and_pitch`.

- [ ] 10.1 Deck in Polish
  - Done when: A PDF of at most 10 slides in Polish, both the Kraków submission and the deck of the Kraków pitch.
  - Waits for: 1.2, 9.1, 9.2.
  - Before that: The outline, at once.
- [ ] 10.2 Video in Polish
  - Done when: An mp4 of at most 3 minutes in Polish, in an open repository, showing the main scenario on a running service, hosted or local.
  - Waits for: 6.1, 6.2.
  - Before that: The script, from the scenario of check 7.2.
- [ ] 10.3 Demonstration in English
  - Done when: A recorded demonstration in English of the `.hap` package running on an emulator, which explains what cannot run on the emulator.
  - Waits for: 8.3.
  - Before that: The script, at once.
- [ ] 10.4 Deck in English
  - Done when: A deck in English, ready before 11:00 in case the Huawei jury invites the team to present.
  - Waits for: 10.1.
  - Before that: The outline, at once.
- [ ] 10.5 Both submissions
  - Done when: The Kraków submission in Polish - title, team ID, description, data sources, business model, the deck and the video - is on HackTribe before 11:00, and the Huawei submission in English is on HackTribe before the deadline of check 1.1.
  - Waits for: 10.1 - 10.3, 9.1 - 9.5, 8.4, 1.1.
  - Before that: The texts of the forms prepared. Every part of sending waits, the exception of `plans_finished/final_checklist/FINAL_CHECKLIST_SHAPE.md`, requirement 12.
- [ ] 10.6 The pitch with a live demo
  - Done when: The pitch with a live demonstration has been given before the Kraków jury. Ticking this check finishes the project.
  - Waits for: 7.2, 7.3, 10.1, 1.2.
  - Before that: A rehearsal on the hosted link.
