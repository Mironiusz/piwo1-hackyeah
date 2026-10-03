# Shape: Mapping of OpenStreetMap tags to the closed list of barriers and amenities

Document state: 2026-10-03, interview closed
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) matches OpenStreetMap data against the closed list of barriers and amenities of the specification, but the specification does not say which OpenStreetMap tags, and from which values, count as which barrier or amenity: from what incline a way is a steep incline, what width is a narrow passage, when a kerb is high, which surfaces are poor. Without this mapping the route cannot avoid OpenStreetMap barriers, and the segment states cannot tell a known attribute from a missing one. In phase B of `plans/mvp/` the agent described the mapping as more a product rule than a technical one; the user handed it to the people responsible for it.

## Recipient and trigger

- The owner of the proposal is the import person of the team, because the mapping is applied where OpenStreetMap tags are turned into facts; as a product rule it is approved by the owner of the specification (question 1). The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-8, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.
- The main consumer of the result is the route: it avoids OpenStreetMap barriers from the profile (FR-2), keeps an unverified barrier not contradicted by OpenStreetMap (FR-3) and gives every segment a state with the missing attributes (FR-10, FR-11), all in `plans/mvp/MVP_PRD.md`. `plans_finished/routing_engine/` therefore depends on this initiative; the map and the list of facts read the same result.

## Current state

- The closed list (`docs/product/specification.md`, M3): barriers - stairs, high kerb, poor surface, steep incline, narrow passage; amenities - ramp, elevator, lowered kerb, accessible toilet, rest place (for example a bench), handrail at stairs. The number of steps can be given for stairs.
- OpenStreetMap provides wheelchair access, kerbs, incline, surface, smoothness, steps, elevators, toilets and benches (`docs/product/specification.md`, M6).
- Segment states depend on whether every attribute behind the barriers of the profile is known (`plans/mvp/MVP_PRD.md`, section Domain rules).
- `plans/mvp/MVP_SHAPE.md` scenario 9 counts "asphalt and no steps in OSM" as known attributes and names only the incline and the kerbs as unknown; scenario 6 speaks of a stairs report on a segment "OpenStreetMap says nothing about".
- A fact from OpenStreetMap "prevails over a contradicting user report, or over denials, until they reach the sum of 2" (`docs/product/specification.md`, M4); an unverified or disputed barrier "not contradicted by OpenStreetMap" is not avoided and its segment is red (`docs/product/specification.md`, M2). Neither section says what "contradicting" means.
- The presets of M1 only switch whole barrier types on or off (`docs/product/specification.md`, M1, table); nothing in the specification makes a threshold depend on the profile.
- The public Geofabrik extracts keep the version and the timestamp of every object and remove only the user name, the user id and the changeset since 3 May 2018 (download.geofabrik.de/technical.html, read on 2026-10-03 by a second-opinion agent of this session, not re-read by the agent writing this). The date of the last OpenStreetMap edit (AC-14) is therefore available for every fact the mapping produces.
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: the mapping of OpenStreetMap tags to every item of the closed list, with its thresholds, decided by the right people. This shape settles the rules of the mapping; the numeric thresholds are proposed by the import person in the PRD phase and approved by the owner of the specification, and until then the code works with default values held in configuration (user decision of 2026-10-03, question 2). As a product rule its result belongs in `docs/product/specification.md`, which is the source of truth for product behavior (`CLAUDE.md`, section What we are building). The rules settled in this shape - the contradiction rule, a missing steps tag as a known "no stairs", thresholds common to all profiles - enter the specification as version 3 once this interview is closed, in sections M2, M4 and M7 and in Decision provenance; the numeric thresholds enter a later version once approved (user decision of 2026-10-03, question 1). The user approves the change, as for versions 1 and 2 (`docs/product/specification.md`, section Decision provenance); the approver was inferred from that history, not named by the user, and the user was asked to correct it if wrong.

## Out of scope

The other decisions delegated in the same conversation have their own initiatives: `plans_finished/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans_finished/demo_environment/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`. The closed list itself is not changed here; it is decided by the specification.

Two defects of the specification were noticed during this interview and reported to the user, but are not of the class of this scope, because they concern the route and the statuses, not the tag mapping:

- Geozones of a type in the profile are avoided whatever their status (`docs/product/specification.md`, M2 and M5), while an unverified point barrier is not avoided (M2). Either a deliberate asymmetry to be written down or a defect; it belongs to the rules of the route.
- The status rule "disputed when neither rule applies" (`docs/product/specification.md`, M4) contradicts scenario 3 of `plans/mvp/MVP_SHAPE.md` and AC-6 of `plans/mvp/MVP_PRD.md`: after the fourth step the confirmations sum to 2.0, so the rule gives confirmed while disputed is expected.

## Functional requirements

1. Every barrier and amenity of the closed list has a rule saying which OpenStreetMap tags and values make it present, absent or unknown.
2. For each barrier, the rule names the attributes that have to be known for a segment to be in the state no barrier (FR-10).
3. The rule says when OpenStreetMap contradicts a user report of a barrier (FR-3, FR-10, `plans/mvp/MVP_SHAPE.md` scenario 4): an opposite fact of the closed list (a lowered kerb against a high kerb) or an explicit tag value on the same stretch that the mapping classifies as not a barrier. The absence of a tag never contradicts a report. Decided by the user on 2026-10-03 (question 4).

## Scenarios: input, flow, expected state after the run

1. Contradiction by a tag value. Input: way W has `surface=asphalt` in OpenStreetMap, last edited in 2023. Flow: 10:00 an anonymous report of poor surface on W (0.5); 10:30 a user with the preset "I use a wheelchair" plans a route through W; 11:00 a logged-in confirmation (1.5); 11:20 an anonymous confirmation (2.0). Expected state: from 10:00 to 11:20 the report is contradicted - the poor surface dimension of W follows OpenStreetMap and the report shows as an unverified report icon; at 11:20 the report prevails, the segment is red and the route avoids W.
2. No contradiction by a missing tag. Input: way V has no `highway=steps` and no step tags. Flow: 10:00 an anonymous report of stairs on V; 10:30 a user with any preset plans a route through V. Expected state: the report is not contradicted, the segment is red, the route keeps V and an alternative avoiding it is proposed (consistent with `plans/mvp/MVP_SHAPE.md` scenario 6).

## Challenging own assumptions

- Do scenarios 6 and 9 of `plans/mvp/MVP_SHAPE.md` agree? Scenario 9 treats a way that is not tagged as steps as a known "no stairs", while scenario 6 treats the same situation as OpenStreetMap saying nothing about stairs. They agree since the answer to question 4: "known for the segment state" and "contradicting a report" are two different rules. A missing steps tag makes the stairs dimension known for the segment state (scenario 9) but never contradicts a stairs report (scenario 6).
- Would it be safer to treat a way without a steps tag as unknown? Then the stairs dimension would be unknown on practically every way, and since all three presets avoid stairs (`docs/product/specification.md`, M1), no segment could ever be green for any preset. The cost of the chosen reading is that a footway whose steps are not mapped in OpenStreetMap is shown as without stairs until someone reports them.
- If width and incline are missing on most OpenStreetMap ways in Kraków, most route segments will be partial data for a wheelchair profile. That is honest, but it shapes the demo; the coverage of these tags is not measured yet.
- Is the mapping the cost function of the route, so that it has to be decided together with the routing engine? No. The thresholds are the same for every profile (section Current state), so the mapping turns tags into present, absent or unknown once, independently of the profile; the route only adds the profile, the user facts and the contradiction rule. The mapping and the routing engine are tied by the shape of this result, not by the engine. This came out of the coupling analysis of `plans_finished/osm_data_source/`, `plans_finished/routing_engine/` and this initiative on 2026-10-03.
- Is "contradicting" one rule for all five barriers? Not necessarily: in the closed list only the high kerb has an opposite item (lowered kerb). For stairs, poor surface, steep incline and a narrow passage OpenStreetMap can say "not a barrier" only through tag values, not through a fact of the closed list. The choice between these two readings decides whether OpenStreetMap can contradict a report of four of the five barriers at all (question 4).
- Noticed while preparing question 4, outside this scope: geozones of a type in the profile are avoided whatever their status (`docs/product/specification.md`, M2 and M5, scenario 7 of `plans/mvp/MVP_SHAPE.md`), while an unverified point barrier is not avoided (M2). This is a rule of the route, not of the tag mapping, so it is reported to the user and not settled here.

## Domain rules or explicit TODO

- Missing information is never presented as a confirmation of accessibility (`docs/product/specification.md`, M10).
- A segment without complete data is never green (`docs/product/specification.md`, M7).
- OpenStreetMap contradicts a user report of a barrier in two cases only: an opposite fact of the closed list (a lowered kerb against a reported high kerb), or an explicit tag value on the same stretch that the mapping classifies as not a barrier (for example `surface=asphalt` against poor surface, an incline or a width on the passable side of the threshold). The absence of a tag never contradicts a report. Decided by the user on 2026-10-03 (question 4). Which tag values are on the passable side follows from the thresholds (question 2).
- A way not tagged as steps counts as a known "no stairs" for the segment state. Source: `plans/mvp/MVP_SHAPE.md` scenario 9, approved by the user with that shape; recorded without asking once question 4 removed the conflict with scenario 6.
- The thresholds are the same for every profile; a preset only switches barrier types on or off (`docs/product/specification.md`, M1). Their values are a TODO for the PRD phase of this initiative: proposed by the import person, approved by the owner of the specification (user decision of 2026-10-03, question 2), before the import builds the segment states from them on 3 October 2026, so that the demo and its recording run on approved values (user decision of 2026-10-03, question 5).
- TODO for phase B of `plans_finished/routing_engine/`: which stretch of way a point report lies on, and within what distance of an opposite kerb fact a report counts as contradicted, is not settled here. The 15 m of `docs/product/specification.md` M3 concerns duplicates only.

## Notes on data, performance and security

- The thresholds decide what a person in a wheelchair, with a baby stroller or with walking difficulties is warned about; a threshold that is too lenient shows a barrier as passable.

## Open questions

None. Questions 1 to 5 were answered on 2026-10-03; the numbering of the answers above follows the original list.
