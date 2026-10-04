# PRD: Official requirements of both challenges

Document state: 2026-10-04, approved by the user

## Business goal

Both juries score more than the running prototype. In the criteria of the Kraków task description, data reliability, presentation and updates weigh 15%, deployment potential and scalability 20% and the business model 20%, and the Kraków submission on HackTribe asks, in Polish and before 11:00 on 4 October 2026, for the description of the data sources and a business model proposal. The Huawei jury scores technical execution and the reproducibility and transparency of the workflow, may run an automated technical pre-review of the repository first, and needs a public repository, a concise architecture and implementation description, the pre-existing and third-party components and `AI_WORKFLOW.md` (`docs/hackathon/challenge_requirements.md`, Judging and Formal deliverables of challenge 1, Use of AI, Deliverables and Judging of challenge 2).

The team needs those descriptions in the repository in English, their Polish text ready for the Kraków form, and a repository that can be made public without publishing a secret or personal data nobody agreed to publish. The deck of check 10.1 and both submissions of check 10.5 then take their content from one source (shape, Recipient and trigger).

## Problem and its consequences

- No document of the repository gathers the data sources with their terms, freshness, reliability and unavailability, the architecture for the submission, the business model, the running of the service outside the infrastructure of the city with its costs, or the licences of the data and components in one list. The facts are scattered over the decided plans of `plans_finished/` (shape, Current state). Without these documents the fields of the Kraków form on the data and the business model have nothing to take, and the deck of check 10.1 has no source.
- The brief asks for two lists: what works and what still needs work in the accessibility of the main scenario, and the known limitations of the whole prototype with a plan to remove them. Check 6.5 delivers only the first.
- The repository holds two `AI_WORKFLOW.md` files that describe the work separately, and the root file has no place for the failed approaches and the lessons learned the Huawei brief names. A jury or an automated pre-review would find the description of the workflow split and incomplete.
- The repository is to be public, and a public repository publishes its whole history. The history holds the signing material of the HarmonyOS client, the e-mail addresses of five authors and the local user names of two members of the team. What is published cannot be taken back.
- The product carries three names in the repository: not chosen, AccessWay and, decided by the user, EnableMe. A description that used another name would contradict the submission.

## Scope

- The description of the data sources and the architecture of check 9.1, in English, written from what is decided and compared with the built state before check 10.5.
- The description of the business and the operation of check 9.2, in English, with the business model chosen by Rafał out of two or three variants the agent drafts, and the estimated running costs.
- The list of what works and what still needs work of check 9.3, in English, with both parts the brief asks for.
- The Polish text of the descriptions of checks 9.1 - 9.3, ready to be pasted into the HackTribe form.
- The Huawei description of check 9.4: the architecture and implementation description in English, the pre-existing and third-party components, the pointers to the tests of the key scenarios, and one complete `AI_WORKFLOW.md` in the root of the repository that takes over the content of the file of the HarmonyOS client.
- The public repository of check 9.5: the search for secrets and personal data repeated on the last state, the ruling of Kuber on the signing material of the HarmonyOS client, the confirmations of the five authors whose e-mail addresses stand in the history, and the repository made public by a person.

## Out of scope

- Filling and sending the HackTribe form of Kraków - the title, the slogan, the team ID, the main description of the project, the checklist of the fields of the form, the deck and the video - which stays with check 10.5 of `stage8_materials_and_pitch`. This initiative gives that form only the Polish text of the descriptions of checks 9.1 - 9.3 (shape, Out of scope and Functional requirements, item 7).
- The accessibility check of the main scenario itself, check 6.5 of `frontend_app`.
- The HarmonyOS client, its instructions and its emulator run, set 8 of `stage5_harmonyos_port`.
- The tests of the key scenarios, delivered by the initiatives that build them; this initiative only points to them.
- The choice of the licence of the repository, which waits for the answer of the organizers (`docs/standards/decision_registry.md`, entry Intellectual property between the two challenges and the repository licence).
- Settling the share-alike terms of the ODbL for a database that combines OpenStreetMap data with the facts of users, which stays open in `MVP.md`, section Open decisions and confirmations.
- Renaming the product in the documents that do not belong to this initiative, which is the effect of check 1.6 of `repository_consistency` (shape, Domain rules or explicit TODO, the item on EnableMe).
- Rewriting the history of any branch, removing the local user names of two members of the team from the tracked files, and removing the official PDFs of `docs/official/`, all three decided by the user against (shape, Domain rules or explicit TODO, and Functional requirements, item 6).

## Functional requirements

FR-1. The repository describes every data source and external service the MVP uses - the OpenStreetMap extract, the address search, the map tiles with their fonts and sprites, the GTFS of ZTP Kraków for the optional O9, and the reports of people - each with its origin, its terms of use, how and how often it is fetched and updated, how its reliability is assessed and shown to the user, and what the user sees when it is unavailable. The description says which of the three city sources named in the brief - the open data portal of Kraków, MSIP and dane.gov.pl - the MVP uses, as `MVP.md`, section Scope, and the answer of `stage1_clarifications` on the stops of MSIP settle it (check 9.1).

FR-2. The repository describes the architecture of the solution: its main components, the data flow, how the acquisition and the updating of data are separated from their presentation, and how a new source, a new category of places and a new city or geographic area are added (check 9.1).

FR-3. Before check 10.5, every statement of the descriptions of FR-1, FR-2 and FR-5 about a source, a component or a part of the architecture is compared with what was built. What was decided and not built is no longer described as built and enters the known limitations of FR-6 (shape, Functional requirements, item 1, and Scenarios, scenario 2).

FR-4. The agent drafts two or three variants of the business model and of the development options, from the brief, from the idea of the venue card of `PRODUCT.md`, section Capabilities and Constraints, and from the optional features O1 - O8 of the specification, each with its estimated running costs. Rafał chooses one variant or composes another, and nothing of the business model enters a description before that choice (check 9.2; shape, Domain rules or explicit TODO).

FR-5. The repository describes the business and the operation of the service (check 9.2):

- the business model and the development options in the variant Rafał chose;
- the running and maintenance outside the infrastructure of the city: who is responsible for the hosting, the updates, the security and the handling of reports, and the running costs, each cost marked as an estimate with its source and the date it was read, and confirmed by Rafał together with the business model;
- the plan from prototype to service the brief asks for during the presentation: who owns the product, how the data are collected and verified, how the hosting and the maintenance are financed, the next steps and the conditions for launching in another city. Agent decision at C:40, without asking: the items of this plan are the items of check 9.2 seen from the presentation, set 9 is checked against `docs/hackathon/challenge_requirements.md`, and without them the deck of check 10.1 would have no source for that part of the pitch;
- the data protection: what data of users are collected, how the reports and the accounts are protected, the secure connections, and that the app asks about no disability, with the known departures of `MVP.md`, section Known departures from the Kraków brief;
- the licences and the dependencies: the licence of every data source and of every component used, the external providers the service depends on, the portability to another infrastructure, the share-alike terms of the ODbL described as raised and not settled together with the way a service after the hackathon would settle them, and the licence of the repository described as waiting for the answer of the organizers.

FR-6. The repository holds the list of what already works and what still needs work, in two parts (check 9.3; decided by the user on 2026-10-04, shape question 6):

- the accessibility of the main scenario, taken from the result of check 6.5;
- the known limitations of the whole prototype, each with a plan to remove it: the departures of `MVP.md`, section Known departures from the Kraków brief, what was decided and not built, and the state of the HarmonyOS client.

The list is written from the built state at the end of the day, after the comparison of FR-3.

FR-7. The descriptions of FR-1, FR-2, FR-5 and FR-6 are written in English first and then in Polish. The Polish text is marked as Polish where it is stored, says the same as the English text, and is ready to be pasted into the HackTribe form of check 10.5 (decided by the user on 2026-10-04, shape question 4).

FR-8. The repository holds a concise architecture and implementation description in English of the solution submitted to Huawei: the HarmonyOS client chosen in check 8.1 and the service it calls (check 9.4).

FR-9. The repository names the pre-existing and third-party components of the solution, the template of the agentic workflow and the third-party skill Impeccable included, each with its licence, and points to the tests of the key scenarios that their initiatives delivered. A key scenario without a delivered test is not presented as tested (check 9.4).

FR-10. The root `AI_WORKFLOW.md` is the only description of the use of AI of the submission and is complete against the Huawei brief: the models, coding agents, MCP servers, skills and other tools used; the main prompts, the reusable instructions and the configuration; the workflow from the idea and the architecture to the implementation, the testing and the debugging; how generated output was reviewed and validated; the known limitations, the failed approaches and the lessons learned. It takes over the content of the `AI_WORKFLOW.md` of the HarmonyOS client - its tools, workflow, validation and limitations, while its table of third-party components joins FR-9 - and that file becomes a pointer to the root file, only after Kuber, who owns the client, has agreed to the change (check 9.4; decided by the user on 2026-10-04, shape question 7). The additional AI integration documentation the Huawei brief asks for when a solution has an AI feature is written if the client of check 8.1 has one; the specification gives the MVP none.

FR-11. Every description of this initiative names the product EnableMe (decided by the user on 2026-10-04, shape question 8).

FR-12. The search for secrets and personal data is repeated on the last state of the repository before check 10.5, over the tracked files and the history of every local and remote branch, and covers what the first search left out: the metadata of images and other binary files, the directory `presentation/` if it is tracked by then, and which branches hold the commit that added the official PDFs (check 9.5; shape, Current state, check 9.5).

FR-13. Kuber rules whether the signing material of the HarmonyOS client is the default material of the public SDK, which may stay in the public repository, or a key of the team, which leaves the repository, its history included, before the repository becomes public (check 9.5; shape, Functional requirements, item 8).

FR-14. Each of the five authors whose e-mail address stands in the commit metadata confirms to Rafał that it may stay in the public repository. An author who does not confirm sets a noreply address for later commits, and the rewrite of the history goes back to the user as a question, with its cost, before the repository becomes public (decided by the user on 2026-10-04, shape question 3).

FR-15. A person makes the repository public once FR-12 - FR-14 are met (check 9.5).

## Acceptance criteria

AC-1. Rafał has read the description of FR-1 and FR-2 and found it complete against the brief: every data source and external service the MVP uses has its origin, terms of use, way and frequency of fetching and updating, assessment and presentation of reliability, and behavior when unavailable; each of the three city sources of the brief is addressed; the components, the data flow, the separation of acquisition from presentation, and the way to add a source, a category and a city are described.

AC-2. At the moment of check 10.5 no description of this initiative presents as built what was not built, and everything decided and not built stands in the known limitations of FR-6.

AC-3. Rafał chose the business model before any part of it entered a description, the description holds that variant, and every number of the running costs is marked as an estimate with its source and the date it was read, and was confirmed by Rafał.

AC-4. Rafał has read the description of FR-5 and found it complete against the brief: the four responsibilities of the running outside the city with the costs, the five items of the plan from prototype to service, the four items of the data protection with both known departures, and the licence of every data source and component with the ODbL share-alike terms as raised and not settled and the licence of the repository as waiting for the organizers.

AC-5. The list of FR-6 holds both parts; its accessibility part matches the result of check 6.5, or says that the check was not done if it was not; every known limitation has a plan to remove it.

AC-6. A Polish text of each description of FR-7 exists, marked as Polish, says the same as the English text at the moment of check 10.5, and Rafał has read it.

AC-7. A person has read the description of FR-8 and the components of FR-9 and found them complete against the Huawei brief, and every pointer to a test leads to a test that exists.

AC-8. The root `AI_WORKFLOW.md` holds every item of FR-10, the content of the file of the HarmonyOS client included; that file only points to the root file; Kuber agreed to the change before it was made; neither file holds a key, a credential or personal data.

AC-9. The repeated search of FR-12 found nothing beyond the exceptions the user accepted, listed in Domain rules.

AC-10. Kuber's ruling on the signing material is recorded, and if it is a key of the team, the material is gone from the repository and its history before the repository becomes public.

AC-11. Each of the five authors has confirmed the e-mail address, or the user has decided on the rewrite of the history before the repository becomes public.

AC-12. The repository is public, and no description of this initiative names the product other than EnableMe.

## Domain rules

- No address, host, login or secret of the hosted demo enters any document this initiative writes (`CLAUDE.md`, section Target environment; `docs/standards/standard_config.md`).
- Nothing this initiative writes holds personal data; a person outside the team is cited by role and channel, never by name.
- The exceptions the user accepted for the public repository: the four official PDFs of `docs/official/` stay tracked, the names of the three mentors in the Kraków task description included (shape question 2); the e-mail addresses of the authors, once each author confirms (shape question 3); the local user names of two members of the team in the tracked files of the HarmonyOS client and in one fact of the plan of `backend_skeleton` (shape question 9).
- Missing or unverified information is never described as a confirmation of accessibility; the only exception is the one the specification makes for O9, stated as a known departure.
- The known departures from the Kraków brief are stated as `MVP.md`, section Known departures from the Kraków brief, records them: the plain HTTP of the hosted demo and, if O9 is built, the green public transport segment without accessibility data.
- Nothing written about licences, the ODbL or the rights of the two challenges is legal advice, and the descriptions say so.
- The agent creates no commit, pushes nothing and rewrites no history. Removing anything from the history of a branch and making the repository public are done by a person (`CLAUDE.md`, section Working with git).
- The deck of check 10.1 takes the business model and the data sources from the descriptions of this initiative, so the two have one source.

## Dependencies and impact on other modules

- Check 6.5 of `frontend_app` gives the accessibility part of FR-6.
- Check 8.1 of `stage5_harmonyos_port` chooses the client that FR-8 and FR-10 describe, and check 8.4 gives its instructions; check 9.4 waits for 8.4.
- The initiatives that build the key scenarios deliver the tests FR-9 points to.
- `stage1_clarifications` answers whether the stops of MSIP enter the MVP (its shape, Open questions, item 6) and sends the question of the licence of the repository to the organizers; FR-1 and FR-5 state what those answers settle.
- Checks 10.1 and 10.5 of `stage8_materials_and_pitch` wait for checks 9.1 and 9.2, and check 10.5 for all of set 9. The coordinating session of Rafał writes the other fields of the Kraków form and points the fields on the data, the business model and what works to the texts of this initiative.
- Check 1.6 of `repository_consistency` waits for checks 9.4 and 9.5 and takes over the contradiction of the product name in the documents this initiative does not rewrite.
- Kuber, for the ruling on the signing material and the consent to the change of the `AI_WORKFLOW.md` of the HarmonyOS client; the five authors, for the confirmation of their e-mail addresses.

## Risks and notes

- Time. The interview closed at about 05:10 and the Kraków form closes at 11:00. The descriptions of checks 9.1 and 9.2, with their Polish text, are needed early, because the deck of check 10.1 waits for them; the list of check 9.3 can be finished only at the end, from the built state.
- The built state may lag far behind what is decided. The comparison of FR-3 can move a large part of the description of the architecture into the known limitations, and the descriptions have to stay true when that happens.
- Check 6.5 may not end before 11:00. The list of FR-6 then says that the accessibility check of the main scenario was not done, instead of describing a result that does not exist.
- The English and the Polish text can drift apart when the English text changes after the translation; every change after the translation has to reach the Polish text before check 10.5.
- The fields of the HackTribe form may limit the length of a text; the limits are not known in the repository.
- The time by which the repository has to be public is set by check 10.5: the Huawei submission needs it before the deadline of check 1.1, and the Kraków video has to be placed in an accessible, open repository. If that video goes into this repository, the repository has to be public before 11:00, and the confirmations of FR-14 and the ruling of FR-13 before that.
- An author who does not confirm, or a key of the team in the signing material, means a rewrite of the history - every branch rewritten and every member of the team cloning again - which a person has to do in the hours before the repository becomes public.
- The licences and dependencies of FR-5 and the third-party components of FR-9 describe overlapping components, and must not contradict each other.
- The running costs are estimates from public price lists read on one day; they are not offers.
