# PRD: MVP of the accessibility app

Document state: 2026-10-03

## Business goal

By 11:00 on 4 October 2026 the team has a working prototype that demonstrates the main scenario of `docs/product/specification.md` in Kraków and meets the requirements of the "Kraków bez barier" brief. The prototype is the core of the Kraków submission - the demo, the video and the presentation are built on it - and the base of a Huawei submission if the team goes for it.

It serves the judging criteria of the Kraków task description directly: usefulness for the chosen group and ease of use (25%), quality and completeness of the prototype (20%), reliability, presentation and updates of the data (15%). The community model - reports, confirmations, moderation - is what the business and scaling story of the presentation (40% together) rests on, so it has to work, not only be described.

## Problem and its consequences

Wheelchair users, parents with baby strollers and people with walking difficulties cannot judge in advance whether a walking route in Kraków is passable for them. The consequences are concrete: a person in a wheelchair turns back at a staircase or a high kerb nobody warned about, a parent carries a stroller down steps, a person who cannot walk far finds no place to rest. The data that exists - mostly OpenStreetMap - is incomplete, its freshness is unknown, and nobody keeps it current. A map that shows missing data as accessible is worse than no map, because it misleads exactly the people who rely on it. Without reports and confirmations from people the data goes stale, and without a visible source, date and status nobody can judge how far to trust it.

## Scope

- The mandatory features M1-M11 of the specification, version 7, with the rules decided in `plans/mvp/MVP_SHAPE.md`.
- The interface requirements of the specification: Polish and English, designed for a phone.
- Privacy information inside the app, required by the section Personal data of the specification.
- Area: the whole of Kraków for routes; the demo in the district of the Tauron Arena, with sample data marked as such.

## Out of scope

- Everything in the section Out of scope of the specification.
- The optional features O1-O8 (QR transfer of the profile, photos, points and ranking, open city data, geozone corrections, place cards, live alerts, voice). The user decided in phase A of this PRD to plan in full only the mandatory core: the optional features have only sketches in the specification, and with about 19 hours to the deadline the core comes first. They get their own pass of `plan-prd` when this PRD is met - entry in `docs/standards/decision_registry.md`. Requirements that mention a photo (flagging, the summary before saving) apply to photos only once O2 exists.

## Functional requirements

FR-1. Preference profile (M1). The user sets barriers to avoid and amenities needed, from the closed list of the specification, or picks one of three presets that fills them in as the specification's table says; every item can then be changed. The profile works without an account, is kept only on the device and never reaches the account.

FR-2. Planning a route (M2). The user picks a start - the current location after the browser asks for consent, an address or a point on the map - and a destination - an address or a point on the map - within Kraków, and gets a walking route. The route avoids barriers from the profile known from OpenStreetMap, confirmed user barriers from the profile and geozones whose type is in the profile, unless they are outdated or hidden by a moderator. Rest places are shown along the route but do not change its course. The current location is not stored, not logged and not linked to the account.

FR-3. Alternative route around unverified barriers (M2). When the route crosses an unverified or disputed barrier from the profile that OpenStreetMap does not contradict, the route keeps it, its segment is red, and the app proposes an alternative route that avoids it, naming the barrier and its status as the reason.

FR-4. No route without barriers (M2). When every way to the destination crosses a barrier from the profile or a matching geozone, the app shows the route with the fewest such barriers, says plainly that no route without barriers exists, and lists where the barriers are.

FR-5. Point report (M3). A user, with or without an account, reports a barrier or an amenity: a point on the map, a type from the closed list, an optional description, and for stairs an optional number of steps. Before saving, the app shows the existing facts of the same type within about 15 m, OpenStreetMap facts included, and asks whether it is the same; yes turns the report into a confirmation of that fact. Then the user approves a summary. A saved report cannot be edited by anyone.

FR-6. Confirmations and denials (M4). A user, with or without an account, confirms that a fact is still there or reports that it is gone, for every fact including OpenStreetMap facts. A person votes on the same fact again only after a day, and only the latest vote of a person counts.

FR-7. Reliability statuses (M4). Every fact, OpenStreetMap facts included, has the status unverified, confirmed, disputed or outdated, derived from its votes by the rules of the section Domain rules. A status never changes with time alone.

FR-8. Simple geozones (M5). A user marks an inaccessible area as a point, chosen on the map or by an address, with a radius from a list, and a barrier type from the closed list. The whole creation works with a keyboard alone. The user approves a summary before saving; a saved geozone cannot be edited. Geozones get votes and statuses like point reports.

FR-9. Open data at start (M6). OpenStreetMap accessibility data for Kraków is available from the first use, with the OpenStreetMap attribution visible. When fresh data cannot be fetched, the app works on the last fetched copy and shows its date.

FR-10. Route segment states (M7). Every segment of a planned route is in one of four states - barrier, no barrier, partial data, no data - according to the section Domain rules. Each state has its own color and its own icon or line pattern, and a legend explains them. The map shows only barriers from the profile; a user report that contradicts OpenStreetMap and has not reached the threshold shows as an unverified report icon.

FR-11. List for the route (M8). After planning, the app shows a text list in three groups: barriers from the profile, additional barriers outside the profile, and amenities from the profile near the route. Each item has its type, place, source, date and status. For a segment with partial data or no data, the list names the missing attributes.

FR-12. Accounts (M9). A user creates an account with a case-insensitive unique pseudonym and a password, logs in and out, and can delete the account. Passwords have a minimum length of 5 characters, accept printable ASCII characters, spaces and Unicode, allow a maximum length of at least 64 characters, and have no character-composition or periodic-change rules. Common or breached passwords are not rejected. There is no password recovery. After login, the session expires 24 hours after the last activity, including read-only requests, and survives closing and reopening the browser. Deleting the account removes it and the pseudonym; the person's reports and votes stay, detached, with their weight.

FR-13. Contributions without an account (M9). Reports, confirmations and denials without an account have the lower weight of the section Domain rules. To tell one person without an account from another for the vote limit and the latest votes of five persons of the section Domain rules, such a vote keeps only an irreversible identifier derived from the IP address and browser characteristics, never the raw values, kept until the demo and all its data are deleted on 4 October 2026; the vote itself keeps its weight. Nothing about the author of any report, vote or geozone is shown to other users.

FR-14. Flagging and moderation (M11). Any user flags a report, a geozone, a fact converted from OpenStreetMap, or a photo if optional feature O2 is implemented. A moderator, whose role the team assigns by hand, sees flagged content without information about its author and can hide it and restore it; hidden content disappears for everyone. Removing the moderator role revokes access on the account's next request, even when its session remains active.

FR-15. Source, date and status (M10). Every fact shown anywhere carries its source - OpenStreetMap or user report - the calendar date it was obtained or last confirmed, and its status. A user fact shows nothing about its author or about the weights.

FR-16. Accessibility of the main scenario (M10). Setting the profile, planning a route, reading the result, reporting a barrier and voting work with a keyboard alone and with a screen reader, with sufficient contrast, and every piece of information on the map is also available as text.

FR-17. Unavailable sources (M10). When the routing service does not answer, the app says plainly that a route cannot be planned right now and shows no guessed route.

FR-18. Sample data (M10). The demo district has sample reports and geozones prepared by the team, marked as sample data wherever they appear.

FR-19. Interface. The interface is in Polish and English, with the default taken from the browser and a switch in the app. It is designed for a phone screen and touch; on a desktop browser it stays usable without being tuned.

FR-20. Privacy information. The app has a page that states which personal data it keeps (the pseudonym and password of an account, the 30-day identifier of a vote without an account), for what purpose and for how long, and which data it does not keep (the profile, the current location, an email address, any information about a disability). It states that the identifier of a vote without an account is pseudonymized personal data, not anonymous data, and that the text of an address search is handed from the server of the project to an address search service outside the project without anything that identifies the person, while the project writes that text to no log and no database and never links it to the person. In the hosted demo the page also states, in Polish and English, that the demo and all its data are deleted on 4 October 2026, after the results are announced.

## Acceptance criteria

AC-1 (FR-1). Picking the preset "I walk with a baby stroller" marks stairs, high kerb, poor surface and narrow passage to avoid, and elevator, ramp and lowered kerb as needed, and nothing else. After unticking stairs and reloading the app on the same device, stairs stay unticked. After logging in on another device, the profile there is empty.

AC-2 (FR-2). For a wheelchair profile and two points in Kraków with stairs from OpenStreetMap on the shortest way, the route goes around the stairs. A geozone of type poor surface on the way is avoided for the wheelchair profile and not avoided for a profile without poor surface. With the current location as the start, nothing about that location is stored after the route is shown.

AC-3 (FR-3). An anonymous report of stairs on a segment OpenStreetMap says nothing about: for a wheelchair profile the route goes through it, the segment is red, and an alternative route avoiding it is proposed with the reason naming the stairs and the status unverified.

AC-4 (FR-4). When the only access to the destination leads up stairs and the profile avoids stairs, the app shows a route through the stairs, states that no route without barriers exists, and lists the stairs.

AC-5 (FR-5). A report of a high kerb 8 m from an existing high kerb report shows the existing one and asks whether it is the same; answering yes adds a confirmation instead of a new report. A report of stairs 5 m from stairs in OpenStreetMap shows the OpenStreetMap fact in the same way. No report is saved without the approved summary. No user, the author included, can change a saved report.

AC-6 (FR-6, FR-7). The run of shape scenario 3 gives, after each step: unverified, unverified, confirmed, disputed. The run of shape scenario 5 keeps the OpenStreetMap stairs after the second denial and marks them outdated after the third. A second confirmation of the same fact by the same account within a day is refused; after a day it is accepted, and only the later of the two counts.

AC-7 (FR-8). A geozone can be created from the first focus to the saved state using only the keyboard. A saved geozone gets votes and statuses like a point report and cannot be edited.

AC-8 (FR-9). The OpenStreetMap attribution is visible on the map. When fetching fresh OpenStreetMap data fails, the app keeps working and shows the date of the copy in use.

AC-9 (FR-10). The four segment states can be told apart in a grayscale screenshot. The legend names all four. A barrier outside the profile does not appear on the map. In the run of shape scenario 4, at 11:00 the segment through X follows OpenStreetMap and an unverified report icon stands at X; after the next anonymous confirmation the segment is red and a new route avoids X.

AC-10 (FR-11). For a planned route the list has the three groups; every item shows type, place, source, date and status. For the segment of shape scenario 9, read as meeting a carriageway, the list for the preset "I use a wheelchair" says that the incline, the kerbs and the width are unknown (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PRD.md` AC-3).

AC-11 (FR-12). An account is created with a case-insensitive unique pseudonym and a password of at least 5 characters, without an email address. Printable ASCII characters, spaces and Unicode are accepted; the maximum password length is at least 64 characters; and no character-composition, periodic-change, common-password or breached-password rules are applied. After login, read-only requests renew the session's 24-hour inactivity period, and the session survives closing and reopening the browser. After the account is deleted, its pseudonym cannot be found anywhere in the app, and the facts it confirmed keep their statuses.

AC-12 (FR-13). Two votes without an account on the same fact from the same browser and network count once. No screen shows whether an author was logged in. The identifier of a vote without an account is kept until the demo is deleted on 4 October 2026, and no task of the app clears it.

AC-13 (FR-14). A flagged report appears in the moderator view; after the moderator hides it, no other user sees it. A user without the moderator role cannot open the moderator view. After the team removes a moderator role, the next request to the view is denied even if the session remains active.

AC-14 (FR-15). A fact confirmed at 00:30 Polish time on 4 October shows the date 4 October. An OpenStreetMap fact shows the date of its last OpenStreetMap edit.

AC-15 (FR-16). The main scenario - preset, route, list, report, vote - is completed with a keyboard alone and with a screen reader on a phone, and the text and the segment styles meet the WCAG 2.2 AA contrast ratios. The list of what works and what does not, required by the brief, is recorded.

AC-16 (FR-17). With the routing service unreachable, the app shows the plain message and no route.

AC-17 (FR-18). Every sample report and geozone in the demo district carries the sample data mark on the map and on the list.

AC-18 (FR-19). With a browser set to English the interface starts in English, with a browser set to Polish in Polish, and the switch changes the language without losing the planned route. The main scenario works on a phone screen of 360 px width, and on a desktop browser no element is cut off or overlapping.

AC-19 (FR-20). The privacy information page lists every kept item with its purpose and retention, and the not-kept items, in both languages; it calls the identifier of a vote without an account pseudonymized personal data and says how the text of an address search leaves the project; and in the hosted demo it states in both languages that the demo and all its data are deleted on 4 October 2026, after the results are announced.

## Domain rules

The rules are those of the specification, version 7, and the section Domain rules of `plans/mvp/MVP_SHAPE.md`. Where the two differ, the specification prevails: the shape stays the record of its interview and still carries rules that version 4 replaced, among them one vote per fact per person and an OpenStreetMap fact outdated by denials alone. In short, for reading the acceptance criteria:

- Weights: a logged-in person counts 1, a person without an account 0.5, the author included.
- A person votes on the same fact again only after a day, and only the latest vote of a person counts.
- The status of every fact, OpenStreetMap facts included, is derived from the latest votes of the five persons who voted on it most recently: outdated when the denials reach at least 2 and outweigh the confirmations; otherwise disputed when it has both confirmations and denials; otherwise confirmed when its confirmations sum to 2; otherwise unverified.
- An OpenStreetMap fact counts on the map and the route until it is outdated, and prevails over a contradicting report until that report sums to 2.
- Segment states: barrier - a prevailing barrier from the profile, or an unverified or disputed one that OpenStreetMap does not contradict; no barrier - every attribute behind the barriers of the profile is known, none is a barrier, and OpenStreetMap does not mark the way `wheelchair=no`; partial data - the known attributes are not barriers, but some are missing or the way is marked `wheelchair=no`; no data - no attribute behind the barriers of the profile is known other than by the default of no stairs. The attributes, the default and the marking are those of the specification, version 3, M6 and M7.
- Dates are calendar days in the Europe/Warsaw zone.
- Missing information is never shown as accessible, and nothing about a disability is asked or stored.
- Amenities from the profile count as near the route within 50 m of it. Agent decision at C:60, without asking - the shape says only "near the route"; confirmed by the user at the gate of this PRD on 2026-10-03, and part of the specification since version 4, M8.
- Changed after the gate on 2026-10-03, to follow version 4 of the specification approved by the user that day (`plans_finished/consistency_check/`): Scope, FR-2, FR-6, FR-7, FR-13, FR-14, AC-6 and the items of this section on the version, the votes, the statuses and the OpenStreetMap facts. The status order settles the contradiction between version 3 of the specification and AC-6, which expected disputed at the fourth step of shape scenario 3. Scope and the first sentence of this section name version 5 since 2026-10-03, which adds the rules of `plans_finished/routing_engine/` and changes none of this PRD. Scope and the first sentence of this section name version 6 since 2026-10-03, which adds the target database schema of `plans_finished/fact_schema/` and changes none of this PRD. Scope and the first sentence of this section name version 7 since 2026-10-03, which adds the rules of `plans_finished/api_contract/` on a route request and an address search without an account, outdated facts on the map, the pseudonym and an expired session; a route request and an address search carry no account, so they are not requests of the session of FR-12 and AC-11, and nothing else of this PRD changes.
- Changed after the gate on 2026-10-03, when `plans_finished/account_sessions/` was merged: FR-12, FR-14, AC-11 and AC-13 carry the account rules added to version 4 of the specification after its approval - the passwords without recovery, the 24-hour session and the end of moderator access on the next request after the role is removed. The rules of that initiative on vote deduplication were rejected by the user on 2026-10-03 and are not part of this PRD.
- Changed after the gate on 2026-10-03, from `plans_finished/demo_environment/` (FR-4 of `plans_finished/demo_environment/DEMO_ENVIRONMENT_PRD.md`): FR-20 and AC-19 require, in the hosted demo, the statement that the demo and all its data are deleted on 4 October 2026, after the results are announced. Confirmed by the user on 2026-10-03 (`plans_finished/demo_environment/DEMO_ENVIRONMENT_PLAN.md` D-6).
- Changed after the gate on 2026-10-03, to align this PRD with the documents that followed it. FR-20 and AC-19 name the address search, which `plans_finished/geocoding/GEOCODING_SHAPE.md`, section Notes on data, performance and security, left to this PRD, and the pseudonymized identifier of a vote without an account, which section Risks and notes already asked of the privacy information; decided by the user on 2026-10-03. The items of Dependencies on external services and on the task `DEPLOYMENT` and the item of Risks and notes on the ODbL state what phase B of `plans/mvp/MVP_PLAN.md` and its initiatives settled, and change no requirement.

## Dependencies and impact on other modules

- No product code exists, so nothing in the repository is changed indirectly. Every module is new.
- The technology stack was an open entry in `docs/standards/decision_registry.md`, to be chosen in phase B of this PRD, and with it the decision whether the Python profile of the standards stays. It was chosen on 2026-10-03: the backend with the Python profile kept in `plans/mvp/MVP_PLAN.md` D-1, the frontend in D-6 there; the entry stays open until the backend decision lands in code.
- The target environment for the demo was an open entry in the same registry. It was decided on 2026-10-03 in `plans_finished/demo_environment/` (`plans/mvp/MVP_PLAN.md` D-10), and the entry is resolved.
- The HarmonyOS port, an open entry in the same registry, is not part of this PRD; the solution must not prevent a second client from using the same data and rules.
- External services: OpenStreetMap data under the ODbL, and an address search service outside the project, which gets only the typed text, from the server of the project (specification, M2 and Personal data). Routes are computed and the map is served inside the project, so no routing or map service outside it is used (same places). Phase B checked their terms, limits and costs in `plans/mvp/MVP_PLAN.md` D-3, D-4, D-6 and D-9.
- The hosted demo, its secure connection and the way to make routing unavailable during the live demo, which FR-17 and the demo required by M10 need, come from the task `DEPLOYMENT` of `plans/deployment/`.
- The optional features O1-O8 come later through their own pass of `plan-prd`; this PRD does not build them, and the solution must not block them.
- The Kraków deliverables outside the app - presentation, video, business model, description of data sources and architecture - are not part of this PRD but are built on its result.

## Risks and notes

- Time: about 19 hours to the deadline for twenty requirements; the plan has to split the work into packages that several people build in parallel, and order them so that the main scenario works first.
- Data coverage: if few Kraków segments have complete OpenStreetMap attributes, most of the route is partial data or no data. Honest, but the demo has to explain it; the sample data in the demo district softens it.
- OpenStreetMap prevails over people until the threshold, so for a while a segment can follow OpenStreetMap although people reported a barrier there (shape scenario 4); the icon and the list are the chosen mitigation.
- The identifier of votes without an account is pseudonymized personal data, not anonymous data in the sense of the GDPR; FR-20 requires the privacy information to say so.
- The ODbL may impose share-alike terms on a database that combines OpenStreetMap data with ours. Phase B checked it in `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, section Risks: share-alike may extend to the user facts once the demo is publicly used, and it was raised with the user there without being settled. Nothing here is legal advice.
- Four segment states on a phone screen may be hard to read; AC-9 and AC-15 check it.
- The district of the Tauron Arena is Czyżyny: OpenStreetMap gives the arena, at Stanisława Lema 7, the district Czyżyny (`plans_finished/geocoding/GEOCODING_PLAN.md` F-2), which settles the check this note asked for.
- FR-13 and AC-12 were changed on 2026-10-04 by `plans_finished/backend_architecture/`, after version 9 of the specification.
