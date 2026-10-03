# Shape: MVP of the accessibility app

Document state: 2026-10-03, interview closed
Regulator: C:60

## Problem

People who meet physical barriers on the way - wheelchair users, parents with baby strollers, people with walking difficulties - cannot judge in advance whether a walking route in Kraków is passable for them. Information about stairs, kerbs, surfaces or closed sidewalks is scattered and incomplete, and its freshness and reliability are unknown. The initiative builds the MVP of a community app that combines open data with reports and confirmations from people and plans routes matched to barrier preferences. The MVP is also the prototype submitted to the HackYeah 2026 challenge "Kraków bez barier", and possibly to "Imagine What's Next" (`docs/hackathon/challenge_requirements.md`).

## Recipient and trigger

- A person from the target group (`docs/product/specification.md`, section Target group) planning a walking route in Kraków. Trigger: they set their preferences and ask for a route from A to B.
- Any user, logged in or not, who sees a barrier, an amenity or an inaccessible area on the way. Trigger: they report it, or confirm or deny an existing one.
- A moderator, a member of the team whose role is assigned by hand. Trigger: a user flags a report, a geozone or a photo.
- The jury of the challenges, who receive the demo of the main scenario. Trigger: the presentation on 4 October 2026.

## Current state

- No product code. The repository holds the agentic workflow, the standards and the documentation.
- `docs/product/specification.md`, version 1 of 2026-10-03, was the result of the first part of this interview, held before the initiative was created: the target group, the split into mandatory and optional features, simple geozones, light accounts with anonymous reports, and points with the ranking as optional. Version 2 of the same day carries the decisions of the rest of this interview.
- The technology stack is an open entry in `docs/standards/decision_registry.md`, to be chosen in phase B of `plan-prd` for this initiative. Until then the Python profile of the standards stays in force.
- The HarmonyOS port and the Huawei submission are an open entry in `docs/standards/decision_registry.md`.
- Deadline: the Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).
- Layout of the initiative, decided by the user: one task for the whole MVP, flat in `plans/mvp/` with the prefix `MVP`. Consequence: the implementation plan has to split the work into packages that several people can build in parallel.
- Language of the seed, decided by the user: the request was made in Polish and the repository is written in English, so the seed keeps the Polish original verbatim with an English translation by the agent next to it.

All decisions recorded in this document were made by the user on 2026-10-03, unless the item says otherwise.

## Smallest meaningful scope

The mandatory features M1-M11 of the specification, version 2, are the smallest meaningful scope: without any of them the main scenario or a requirement of the Kraków brief is missing from the demo.

The initiative also covers the optional queue O1-O8: the PRD and the plan describe the optional features as later work packages in the order of the specification, so that the architecture anticipates them, and they are built only after M1-M11 work. Moving the profile with a QR code was added to the queue during the interview and put first, before photos, because it is simpler to build.

Changed by the user in phase A of `plan-prd`: the PRD and the plan of this initiative describe in full only M1-M11 and the interface. The optional queue O1-O8 has only sketches in the specification, and with about 19 hours to the deadline the core comes first; the optional features get their own pass of `plan-prd` when M1-M11 meet their acceptance criteria - entry in `docs/standards/decision_registry.md`.

Area: routes work in the whole of Kraków on OpenStreetMap data. The demo, with its sample reports and geozones marked as sample data, takes place in the district of the Tauron Arena, the venue of HackYeah - Czyżyny according to the agent's knowledge, to be checked on the map.

## Out of scope

The section Out of scope of the specification applies. Added in this interview:

- Sending user reports back to OpenStreetMap. It would need an OpenStreetMap account for every reporter, or an import that follows the rules of the OpenStreetMap community; it stays as a development idea for the presentation.
- A layout tuned for desktop browsers - the app only must not break there.
- Aging of facts: a status does not change with time alone; the date of the last confirmation is visible and the user judges it.
- The optional queue O1-O8 (QR transfer of the profile, photos, points and ranking, open city data, geozone corrections, place cards, live alerts, voice), taken out of this PRD and plan by the user in phase A of `plan-prd`. Three items of the seed - points with the ranking, geozone corrections and voice - therefore have no executor in this initiative; they stay in the queue of the specification, with the condition for coming back recorded in `docs/standards/decision_registry.md`.

## Functional requirements

Numbers M and O follow the specification, version 2.

1. M1 Preference profile - barrier and amenity preferences, three presets, no disability asked or stored, works without logging in. The profile is kept only locally, per device, and never enters the account.
2. M2 Route matched to the profile - a walking route from A to B within Kraków. The start can be the current location (after the browser asks for consent; not stored), an address or a point on the map. The route avoids barriers from the profile known from OpenStreetMap, confirmed barriers from the profile and geozones whose type is in the profile. Rest places are shown along the route but do not change its course.
3. M2, an unverified or disputed barrier from the profile that OpenStreetMap does not contradict: its segment is red, the route does not avoid it, and the app proposes an alternative route that avoids it and says why, naming the barrier and its status.
4. M2, no route without barriers: when every way to the destination crosses a barrier from the profile or a matching geozone, the app shows the route with the fewest such barriers, says plainly that no route without barriers exists, and lists where the barriers are.
5. M3 Point reports - a point with a type from the closed list and an optional description. Before saving, the app shows the existing facts of the same type within about 15 m, OpenStreetMap facts included, and asks whether it is the same barrier; yes turns the report into a confirmation of the existing fact. Then the app shows a summary that the user has to approve. Once saved, nobody edits a report, the author included.
6. M4 Confirmations and reliability statuses - still there or gone, for every barrier and amenity, OpenStreetMap facts included, with the statuses, weights and threshold from the section Domain rules.
7. M5 Simple geozones - a point, chosen on the map or by searching an address, with a radius chosen from a list (for example 10, 25, 50 or 100 m), and a barrier type from the same list as point reports. It can be created with a keyboard alone, needs an approved summary before saving, is judged with the mechanism of M4 and is not edited after saving.
8. M6 Open data at start - OpenStreetMap with its licence and attribution. When fresh data cannot be fetched, the app works on the last fetched copy and shows its date.
9. M7 Route colors - four segment states: red (a prevailing barrier from the profile), green (every attribute relevant to the profile is known and none is a barrier), partial data (the known attributes are not barriers, but some relevant ones are missing) and grey dashed (no data). Only barriers from the profile appear on the map and in the colors; barriers outside the profile are hidden from the map so they do not clutter it. A user report that contradicts OpenStreetMap and has not reached the threshold appears as an unverified report icon. Each state also has an icon or a line pattern; the exact styles are a design matter of the plan.
10. M8 Barrier list for the route - two groups: barriers matching the profile, and additional barriers outside the profile. Each item has its type, place, source, date and reliability status. For a segment with partial data or no data the list names the missing attributes.
11. M9 Accounts and anonymous reports - a pseudonym and a password, without an email address. Reports and votes can be made without an account, with the weights from the section Domain rules. Deleting an account removes the account, the pseudonym and the points; reports and votes stay, detached from the person, with their weight.
12. M10 Requirements of the Kraków brief - every fact shows its source (OpenStreetMap, city data, user report), the calendar date it was obtained or last confirmed and its reliability status; missing information is never shown as accessible; keyboard, screen reader, contrast and a text form of the map; the demo shows a contradiction between OpenStreetMap and a user report, and an unavailable source; sample data is marked as sample data.
13. M11 Flagging and moderation - anyone can flag a report, a geozone or a photo. A moderator sees the flagged content in a simple view and can hide it; hidden content disappears for everyone. This also answers the brief's question about who handles reports.
14. Interface - Polish and English, with the default taken from the browser settings and a switch in the app. Designed for a phone only; on a desktop browser it must not break.

## Scenarios: input, flow, expected state after the run

1. Main scenario. Input: a user with the preset "I use a wheelchair", the current location and a destination in Kraków. Flow: the user asks for a route. Expected state: a route avoiding the barriers and geozones from the profile, segments in the four states, and a list of barriers in two groups, each item with its source, date and status.
2. Duplicate report. Input: a user without an account at a crossing 8 m from an existing report of a high kerb. Flow: the user chooses the type high kerb; the app shows the existing report; the user answers that it is the same barrier and approves the summary. Expected state: no new report; the existing one has one more anonymous confirmation weighing 0.5, and the hash of the voter is stored for 30 days.
3. Status run. Input: a barrier reported at point Z. Flow: 10:00 an anonymous report; 10:20 a logged-in confirmation; 10:40 an anonymous confirmation; 12:00 a logged-in denial. Expected state after each step: unverified (0.5), unverified (1.5), confirmed (2.0), disputed.
4. Contradiction with OpenStreetMap. Input: OpenStreetMap has a lowered kerb at crossing X; an anonymous report of a high kerb at 10:00 and a logged-in confirmation at 10:30. Flow: a user with a wheelchair profile plans a route through X at 11:00. Expected state: the segment color follows OpenStreetMap, an unverified report icon stands at X, and the list shows the report among the barriers from the profile as unverified. After one more anonymous confirmation the report reaches 2.0 and prevails: the segment is red and the route avoids X.
5. Denying an OpenStreetMap fact. Input: OpenStreetMap has stairs at S. Flow: denials at 10:00 (anonymous), 10:30 and 11:00 (logged in). Expected state: until 10:30 the OpenStreetMap fact stands with an icon saying it was reported as gone; from 11:00, with denials weighing 2.5, the fact is outdated.
6. Unverified barrier without contradiction. Input: an anonymous report of stairs on a segment that OpenStreetMap says nothing about. Flow: a user with a wheelchair profile plans a route through it. Expected state: the segment is red, the route goes through it, and the app proposes an alternative route avoiding it, with the reason.
7. Geozone. Input: a logged-in user marks a point with a radius of 25 m and the type poor surface. Flow: the user approves the summary. Expected state: the geozone is saved as unverified with weight 1, and routes for profiles that avoid poor surface go around it.
8. No route without barriers. Input: the only access to a destination leads up stairs; the profile avoids stairs. Expected state: the route with the fewest barriers, a plain statement that no route without barriers exists, and the list of the barriers.
9. Partial data. Input: segment Y has asphalt and no steps in OpenStreetMap, without incline or kerb data; nobody reported anything. Expected state for a wheelchair profile: the segment is in the partial data state, and the list says that the incline and the kerbs are unknown.
10. Unavailable sources. Input: the routing service does not answer. Expected state: a plain message that a route cannot be planned right now, with no guessed route. Input: fresh OpenStreetMap data cannot be fetched. Expected state: the app works on the last fetched copy and shows its date.
11. Moderation. Input: a report whose description contains another person's surname. Flow: a user flags it; the moderator sees it in the moderator view and hides it. Expected state: the report is hidden for everyone.
12. Account deletion. Input: the account "wozek_krk" with 30 reports, 12 of them confirmed. Flow: the person deletes the account. Expected state: the account, the pseudonym and the points are gone; the 30 reports stay, detached from the person, and the 12 confirmed facts stay confirmed.

## Challenging own assumptions

- Does "rating spots" in the seed mean a score? The Kraków brief asks for concrete barriers and amenities instead of an accessible / not accessible label, so it became reports of concrete facts (M3). The user accepted this before the initiative was created.
- Does "notification" in the seed mean a push notification while walking? Assumed a summary shown after the route is planned (M8), with live alerts as O7. The user accepted this before the initiative was created.
- Is the split into mandatory and optional decided by the briefs alone? No: the briefs decide what the demo cannot do without, and the time to the deadline decides how much else fits. The order of the optional queue reflects value for the judging criteria and, for the QR transfer, the effort.
- Does the third group, people with walking difficulties, bring a routing need the usual route engines do not support? Yes, a rest place at a given distance. Resolved in the specification: rest places are shown along the route but do not change its course.
- Is one task for the whole MVP too large for one PRD and one plan? Possibly. The user chose it for one coherent architecture and data model; the risk is a long plan, mitigated by splitting it into work packages.
- Does hiding whether an author was logged in conflict with the brief, which asks for the source of every fact? No: the source user report together with the reliability status distinguishes data from people from confirmed data, which is what the brief asks for. The weights stay inside the system.
- Does OpenStreetMap prevailing until the threshold expose a user to a barrier that people reported? Yes, for a while: in scenario 4, at 11:00 the segment follows OpenStreetMap although reports weighing 1.5 say there is a high kerb. The unverified report icon and the item on the list are the chosen mitigation.
- Is a vote with a hash of the IP address and browser characteristics still anonymous? Not in the sense of the GDPR - it is pseudonymized personal data, hence the 30-day retention and the duty to state it in the privacy information. In the interface "anonymous" means "without an account".
- Does hiding barriers outside the profile from the map contradict the rule that the user judges on their own? No, because the list from M8 keeps them in a separate group.
- Will four segment states be understood on a phone screen? Not certain. The legend, the icons and the list carry the meaning; the accessibility check of the main scenario has to cover it.
- Is 15 m the right radius for the duplicate hint? Unknown; it comes from the option the user chose, and the plan may tune it with the user's consent.

## Domain rules or explicit TODO

- Missing information is never presented as a confirmation of accessibility (Kraków brief, M10).
- The app does not ask about a disability and does not store one (Kraków brief, M1).
- Every fact carries its source, the date it was obtained or last confirmed, and its reliability status (Kraków brief, M10). The source is OpenStreetMap, city data or user report; nothing about the author of a user report is shown.
- Reliability statuses: unverified, confirmed, disputed and outdated (gone). A user report starts as unverified.
- Weights: a logged-in person counts 1 and a person without an account 0.5, the author included. A vote with a photo weighs 0.5 more (with O2).
- A user fact becomes confirmed when the sum of its confirmations reaches 2. A fact becomes outdated when the denials reach at least 2 and outweigh the confirmations, and disputed when it has both confirmations and denials without either rule applying.
- OpenStreetMap against user reports: a fact from OpenStreetMap shows its source and the date of its last edit in OpenStreetMap. It prevails over contradicting user reports and denials until they reach the sum of 2; then the user fact replaces it in the view, or the OpenStreetMap fact becomes outdated. A confirmation of an OpenStreetMap fact updates its date of last confirmation.
- One vote per fact per person: per account for logged-in users, per hash of the IP address and browser characteristics for others, the hash kept for 30 days.
- Dates are shown as the calendar day in the Europe/Warsaw zone, without the hour. A confirmation at 00:30 Polish time on 4 October is shown as 4 October, although in UTC it is still 3 October; OpenStreetMap edit times, given in UTC, are converted the same way.
- The app never pretends that its data is current: an unavailable routing service gives a plain message and no guessed route, and stale OpenStreetMap data is shown with its date.
- Presets, decided by the user in phase A of `plan-prd`: "I use a wheelchair" avoids stairs, high kerbs, poor surface, steep inclines and narrow passages, and needs elevators, ramps, lowered kerbs and accessible toilets. "I walk with a baby stroller" avoids stairs, high kerbs, poor surface and narrow passages, and needs elevators, ramps and lowered kerbs. "Walking is difficult for me" avoids stairs, poor surface and steep inclines, and needs rest places and handrails at stairs. A preset is only a starting point; the user can change every item, for example untick stairs when a few steps with a handrail are acceptable.
- Amenities from the profile, decided by the user in phase A of `plan-prd`: the amenities the profile needs that lie near the route have icons on the map and a third group on the list from M8, amenities on the route, each with its source, date and status. They do not change the course of the route.

## Notes on data, performance and security

- OpenStreetMap data is under the ODbL: attribution is required, and a database that combines OpenStreetMap data with our own may fall under its share-alike terms. To be checked when the data flow is designed; this is not legal advice.
- Personal data the MVP keeps: the pseudonym and the password of an account; the hash of the IP address and browser characteristics of a vote without an account, deleted after 30 days; photos (O2) with their metadata removed. The privacy information has to state each of them with its purpose and retention.
- Personal data the MVP does not keep: the preference profile (only on the device, because a profile tied to an account practically reveals health information), the current location (only inside a route request, not stored or logged, not linked to the account), the email address, any information about a disability.
- Other users never see who made a report, a confirmation or a geozone. The ranking (O3) shows pseudonyms with their points only.
- Photos can show faces, licence plates or other people's property: the guidance at upload, the removal of metadata and flagging (M11) are the agreed safeguards.
- The number and cost of calls to an external routing or map service, and the keys they need, are settled in phase B. Keys and secrets never enter the repository (`docs/standards/standard_config.md`).

## Open questions

None - every question of the interview is answered and recorded above.
