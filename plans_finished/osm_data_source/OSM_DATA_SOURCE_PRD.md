# PRD: Choice of the source of OpenStreetMap data for the MVP

Document state: 2026-10-03

## Business goal

The map of the MVP is not empty before anyone reports anything: OpenStreetMap gives the accessibility attributes of ways and places and the pedestrian network the routes run on from the first minute (`docs/product/specification.md`, M6). Every route, every segment color and every OpenStreetMap fact the demo shows comes from the copy this initiative decides on, so the decision carries the demo for the Kraków brief and the 15% criterion "Data reliability, presentation and updates" (`docs/hackathon/challenge_requirements.md`, section 8 of the task description).

The initiative delivers the decision on where the MVP takes OpenStreetMap data for Kraków from and how that copy is refreshed, together with the rules for OpenStreetMap facts that disappear from or return to a fresh copy. The decision closes `plans/mvp/MVP_PLAN.md` Q-2, so that the MVP plan can be closed and the first import can run on 3 October 2026, before the demo recorded on the morning of 4 October and the Kraków deadline at 11:00 on 4 October 2026.

## Problem and its consequences

Without a decided source there is no first copy, and without it there are no OpenStreetMap facts, no pedestrian network and no route: the main scenario of the brief cannot be shown at all.

A source that does not give the date of the last OpenStreetMap edit of each element makes `plans/mvp/MVP_PRD.md` AC-14 impossible, and a copy without a date of its own makes the app pretend its data is current, which the specification forbids (M6).

OpenStreetMap is edited all the time, and users vote on OpenStreetMap facts (M4). When a fresh copy no longer holds a fact that people have confirmed, the app either silently drops the knowledge of those people or keeps showing as OpenStreetMap data something OpenStreetMap no longer says. Both are wrong, and the specification does not say what happens; the shape interview decided it.

The brief also warns that data published online is not automatically free to fetch automatically, and that the description of every source has to state its origin, terms, freshness and verification method. A source used outside its terms puts the submission at risk.

## Scope

- The choice of the source of OpenStreetMap data for Kraków and of the way the copy is fetched, made in phase B of this initiative and recorded so that it closes `plans/mvp/MVP_PLAN.md` Q-2.
- The refresh in the MVP: one copy fetched before the demo, and a fresh copy triggered by hand by the team.
- What happens to an OpenStreetMap fact, its votes and its status when a fresh copy no longer holds it, and when a later copy holds it again.
- The contribution of these rules to version 3 of `docs/product/specification.md`, in sections M4 and M6 and in Decision provenance, written together with the rules of `plans_finished/osm_barrier_mapping/` as one change approved by the user.
- The facts about this source that the description of the data sources in the submission needs: origin, terms of use, freshness, and how the copy is checked.

## Out of scope

- Building the import and the refresh. The code is a work package of `plans/mvp/`, built together with the backend architecture of `plans/mvp/MVP_PLAN.md` Q-11. Decided by the user on 2026-10-03 (shape, question 1).
- A refresh on a schedule. In the MVP nothing refreshes by itself; a regular refresh, for example once a day, is only described in the plan from prototype to service. Decided by the user on 2026-10-03 (shape, question 3).
- Which OpenStreetMap tags count as which barrier or amenity, with their thresholds, and the rule of when OpenStreetMap contradicts a user fact. That is `plans_finished/osm_barrier_mapping/`; this PRD only applies its contradiction rule.
- How facts and votes are stored, which is `plans/mvp/MVP_PLAN.md` Q-10.
- The routing engine, which is `plans/routing_engine/`. The two initiatives meet at the pedestrian network, described under Dependencies.
- The base map tiles shown under the routes, which are part of `plans_finished/frontend_stack/`.
- Writing anything back to OpenStreetMap. The app never edits OpenStreetMap data.
- Data outside Kraków, because the MVP works only within Kraków.
- A requirement that the chosen source serves another Polish city in the same way as Kraków. The brief asks the team to describe how another city is added, and that description belongs to the plan from prototype to service, not to the choice of the source for the MVP. Decided by the user at the gate of this PRD on 2026-10-03, against an agent proposal that would have narrowed the choice of phase B.

## Functional requirements

FR-1. Coverage. The copy covers the whole area of Kraków with the pedestrian network the routes run on and the accessibility attributes named in M6: wheelchair access, kerbs, incline, surface, smoothness, steps, elevators, toilets and benches.

FR-2. Date of the last edit. For every OpenStreetMap element the copy gives the date of its last edit in OpenStreetMap, so that every OpenStreetMap fact can show it (`plans/mvp/MVP_PRD.md` FR-15, AC-14).

FR-3. Date of the copy. Every copy has one date, the calendar day of the state of OpenStreetMap it reflects, and the app shows that date wherever it says how fresh its OpenStreetMap data is. The date of the download is not shown in its place, because a copy downloaded today can reflect an older state of OpenStreetMap and the app never pretends its data is current. Proposed by the agent and confirmed by the user at the gate of this PRD on 2026-10-03, against showing the date of the download.

FR-4. First copy. Before the first use of the app, a copy of OpenStreetMap data for Kraków is in place, fetched before the demo.

FR-5. Refresh by hand. The team can trigger a fresh copy by hand at any time. Nothing triggers one on a schedule.

FR-6. Failed refresh. When a fresh copy cannot be fetched or cannot be completed, the app keeps working on the last complete copy, unchanged, with its date. A copy is used as a whole or not at all: a refresh that fails halfway never leaves the app on a mix of the old and the new copy.

FR-7. Disappearing fact with a majority of confirmations. When an OpenStreetMap fact is missing from a fresh copy and the sum of its confirmations is greater than the sum of its denials, it becomes a user fact. It keeps all its votes, confirmations and denials alike, shows the source "user report" with the date of its last confirmation, and from then on its status follows the rules of a user fact in M4.

FR-8. Disappearing fact without a majority of confirmations. When an OpenStreetMap fact is missing from a fresh copy and has no votes, only denials, or as many confirmations as denials by weight, it becomes outdated with the reason that it was removed in OpenStreetMap. It disappears from the map and from routes, and its votes stay in its history.

FR-9. Returning fact. When a later copy holds a fact of the same type on the same OpenStreetMap element again, it is the same fact again: a converted user fact from FR-7 or an outdated fact from FR-8 becomes an OpenStreetMap fact once more, with the source OpenStreetMap, the date of its last OpenStreetMap edit and all its votes.

FR-10. No merging by distance. An OpenStreetMap fact that appears in a fresh copy where a user fact of the same type already lies is a separate fact; the two are not merged (M3, "Nothing is merged automatically").

FR-11. Contradiction after conversion. Whether a fresh copy contradicts a fact converted by FR-7 follows the contradiction rule of `plans_finished/osm_barrier_mapping/`: a missing tag never contradicts it, an explicit tag value on the passable side does, and then the segment color follows OpenStreetMap until the votes reach the sum of 2.

FR-12. Terms and attribution. The source is used within its published terms of use and the ODbL licence of OpenStreetMap, and the OpenStreetMap attribution is visible in the app (`plans/mvp/MVP_PRD.md` FR-9).

## Acceptance criteria

AC-1 (FR-1). In the copy in use, a route can be planned between the Tauron Arena and the Rynek Główny, and between two points at opposite edges of Kraków, for example Nowa Huta and Bielany; OpenStreetMap facts of stairs, kerbs, surface and toilets appear on the map within Kraków.

AC-2 (FR-2). Every OpenStreetMap fact shown in the app has the calendar date of the last OpenStreetMap edit of its element, in the Europe/Warsaw zone; no OpenStreetMap fact is shown without it.

AC-3 (FR-3). A copy downloaded on 3 October that reflects the state of OpenStreetMap from 2 October shows the date 2 October, not 3 October.

AC-4 (FR-4, FR-5). On the morning of 4 October the app shows OpenStreetMap facts and plans routes without anyone having triggered anything that morning. A refresh triggered by hand replaces the copy in use and its date with the fresh ones.

AC-5 (FR-6). With the source unreachable, a refresh triggered by hand ends without changing anything the user sees: the same facts, the same routes and the same date of the copy. A refresh interrupted halfway leaves the copy from before the refresh in use as a whole.

AC-6 (FR-7). The run of shape scenario 1 gives, at 12:30 on 3 October: stairs on way W is a user fact with the source "user report", the 1.5 of confirmations, the status unverified and the date of its last confirmation, 3 October; for the preset "I use a wheelchair" the segment through W is red, the route keeps W, and an alternative avoiding it is proposed.

AC-7 (FR-8). The run of shape scenario 2 gives, at 12:30 on 3 October: poor surface on way V is outdated with the reason that it was removed in OpenStreetMap, it is on neither the map nor the route for the preset "I walk with a baby stroller", and the anonymous denial stays in its history. The same run without the denial, and the same run with one anonymous confirmation and one anonymous denial, end the same way.

AC-8 (FR-9). The run of shape scenario 3 gives, at 08:00 on 4 October: one stairs fact on way W, an OpenStreetMap fact with the date of its last OpenStreetMap edit and the 2.0 of confirmations, and the route for the preset "I use a wheelchair" avoids W.

AC-9 (FR-10). A user report of stairs 5 m from a way that a fresh copy newly tags as steps leaves two stairs facts after the refresh: the user fact and the OpenStreetMap fact, each with its own votes.

AC-10 (FR-11). A poor surface fact converted by FR-7 on way V, after a fresh copy tags V as `surface=asphalt`, does not color the segment through V as poor surface for the preset "I walk with a baby stroller" until its confirmations reach the sum of 2; after that it does.

AC-11 (FR-12). The OpenStreetMap attribution is visible on the map. The description of the data sources states the origin of the copy, its terms of use, how it is refreshed and how it is checked, and nothing in the way the copy is fetched breaks the terms of the source.

## Domain rules

The rules are those of the section Domain rules of `plans_finished/osm_data_source/OSM_DATA_SOURCE_SHAPE.md`. In short, for reading the acceptance criteria:

- Dates are calendar days in the Europe/Warsaw zone; OpenStreetMap edit times given in UTC are converted to that day.
- The app never pretends its data is current: the OpenStreetMap data is always shown with the date of the copy.
- For OpenStreetMap facts a successful fresh copy is authoritative and replaces the stored one; the stored copy is only the fallback while a fresh one cannot be fetched.
- The sums of confirmations and denials use the weights of M4: 1 for a logged-in person, 0.5 for a person without an account. A vote keeps its weight in these sums for as long as the fact exists.
- A fact disappearing from a fresh copy becomes a user fact only with more confirmations than denials by weight; otherwise it becomes outdated with the reason that it was removed in OpenStreetMap.
- "The same OpenStreetMap element" means the element with the same OpenStreetMap identifier. A fact returning on the same element with the same type is the same fact again; this is a match by identity, never by distance.
- Facts are never merged by distance.
- The rules of disappearing and returning facts run on every refresh, and in the MVP every refresh is triggered by hand.

## Dependencies and impact on other modules

- No product code exists, so nothing in the repository is changed indirectly. The decision feeds `plans/mvp/`: it closes `plans/mvp/MVP_PLAN.md` Q-2, and the import with the refresh by hand becomes a work package of that plan, built with Q-11.
- `plans/mvp/MVP_PLAN.md` Q-10 waits for FR-7 to FR-9 of this PRD: the domain model has to keep the votes of a fact across its conversion and return, and keep the weight of an anonymous vote after its 30-day identifier is deleted (M9).
- `plans/routing_engine/` and this initiative both decide where the pedestrian network comes from (`plans/mvp/MVP_PLAN.md`, Risks). Phase B of this initiative checks that the chosen copy can feed the routing engine, and records it as a condition for `plans/routing_engine/`.
- `plans_finished/osm_barrier_mapping/` gives the contradiction rule FR-11 applies, and its rules and these enter version 3 of `docs/product/specification.md` as one change. That change, these rules included, is written by `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` (D-2 there, and D-20 of `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, decided by the user on 2026-10-03).
- `plans/demo_environment/` decided a hosted service at a public link; where the first copy is fetched and where a refresh by hand runs depends on it.
- `plans_finished/geocoding/` depends on this initiative only if it searches an own index built from OpenStreetMap data.
- The HarmonyOS port, an open entry in `docs/standards/decision_registry.md`, uses the same copy through the server; nothing here depends on the client.

## Risks and notes

- The rules of FR-7 to FR-9 were decided by the user answering for the import person, who owns this decision; the ruling of the import person is still to be confirmed. If it changes, version 3 of the specification and Q-10 change with it.
- When OpenStreetMap splits, joins or recreates a way, its parts get new identifiers. By the rules above, a fact on the old identifier then disappears (FR-7 or FR-8) and a new OpenStreetMap fact appears on the new one (FR-10), which can leave a converted user fact next to an OpenStreetMap fact of the same barrier. Phase B and Q-10 decide whether this is accepted for the MVP or handled; the shape left it open.
- A bad edit or vandalism in OpenStreetMap can make many facts outdated in one refresh. In the MVP a refresh runs only by hand, so the team sees the result before the demo; for the service this is a risk of a regular refresh, to be described in the plan from prototype to service.
- On 2026-10-03 two public Overpass API instances did not answer from the machine of the agent's session within 40 s, while the Geofabrik extract for Małopolska was reachable. Phase B checks the candidates again from the environment of `plans/demo_environment/`, because a source that fails on the day of the first import leaves the demo without data.
- OpenStreetMap data is under the ODbL: attribution is required, and a database combining OpenStreetMap data with our own may fall under its share-alike terms (`plans/mvp/MVP_PRD.md`, Risks and notes). Nothing here is legal advice.
- The 15% criterion "Data reliability, presentation and updates" is met in the MVP with the visible date of the copy, the refresh by hand and the description, not with a running schedule; a jury may weigh that lower.
- Time: the decision blocks the closing of the MVP plan and the first import, and every hour it stays open is taken from implementation before 11:00 on 4 October 2026.
