# Shape: Mapping of OpenStreetMap tags to the closed list of barriers and amenities

Document state: 2026-10-03, interview in progress
Regulator: C:40

The seed quotes agent questions whose text contains C:20 (an option the user did not pick) and C:40 (the value the user confirmed in answer 3). Neither is a parameter of the request itself; the value in force is C:40.

## Problem

The MVP (`plans/mvp/`) matches OpenStreetMap data against the closed list of barriers and amenities of the specification, but the specification does not say which OpenStreetMap tags, and from which values, count as which barrier or amenity: from what incline a way is a steep incline, what width is a narrow passage, when a kerb is high, which surfaces are poor. Without this mapping the route cannot avoid OpenStreetMap barriers, and the segment states cannot tell a known attribute from a missing one. In phase B of `plans/mvp/` the agent described the mapping as more a product rule than a technical one; the user handed it to the people responsible for it.

## Recipient and trigger

- The owner of the proposal is the import person of the team, because the mapping is applied where OpenStreetMap tags are turned into facts; as a product rule it is approved by the owner of the specification (question 1). The user named five team roles on 2026-10-03 - frontend, db, import, external API, backend - and asked the agent to assign the initiatives to them; this assignment is an agent decision at C:40, without asking, made at that request.
- `plans/mvp/MVP_PLAN.md`, open question Q-8, which waits for this decision. Trigger: the user delegated the decision on 2026-10-03 in phase B of `plans/mvp/`.

## Current state

- The closed list (`docs/product/specification.md`, M3): barriers - stairs, high kerb, poor surface, steep incline, narrow passage; amenities - ramp, elevator, lowered kerb, accessible toilet, rest place (for example a bench), handrail at stairs. The number of steps can be given for stairs.
- OpenStreetMap provides wheelchair access, kerbs, incline, surface, smoothness, steps, elevators, toilets and benches (`docs/product/specification.md`, M6).
- Segment states depend on whether every attribute behind the barriers of the profile is known (`plans/mvp/MVP_PRD.md`, section Domain rules).
- `plans/mvp/MVP_SHAPE.md` scenario 9 counts "asphalt and no steps in OSM" as known attributes and names only the incline and the kerbs as unknown; scenario 6 speaks of a stairs report on a segment "OpenStreetMap says nothing about".
- The Kraków submission closes at 11:00 on 4 October 2026 (`docs/hackathon/challenge_requirements.md`, Shared facts).

## Smallest meaningful scope

Following from the seed: the mapping of OpenStreetMap tags to every item of the closed list, with its thresholds, decided by the right people. As a product rule its result belongs in `docs/product/specification.md`, which is the source of truth for product behavior (`CLAUDE.md`, section What we are building); how it gets there is open (question 1).

## Out of scope

The other decisions delegated in the same conversation have their own initiatives: `plans/api_contract/`, `plans/routing_engine/`, `plans/osm_data_source/`, `plans/frontend_stack/`, `plans/demo_environment/`, `plans/local_database/`, `plans/geocoding/`, `plans/account_sessions/`. The closed list itself is not changed here; it is decided by the specification.

## Functional requirements

1. Every barrier and amenity of the closed list has a rule saying which OpenStreetMap tags and values make it present, absent or unknown.
2. For each barrier, the rule names the attributes that have to be known for a segment to be in the state no barrier (FR-10).
3. The rule says when an OpenStreetMap fact contradicts a user report of the same kind (FR-3, FR-10, `plans/mvp/MVP_SHAPE.md` scenario 4).

## Scenarios: input, flow, expected state after the run

## Challenging own assumptions

- Do scenarios 6 and 9 of `plans/mvp/MVP_SHAPE.md` agree? Scenario 9 treats a way that is not tagged as steps as a known "no stairs", while scenario 6 treats the same situation as OpenStreetMap saying nothing about stairs. Both can hold only if "known for the segment state" and "contradicting a report" are two different rules; this has to be decided, not assumed (questions 3 and 4).
- If width and incline are missing on most OpenStreetMap ways in Kraków, most route segments will be partial data for a wheelchair profile. That is honest, but it shapes the demo; the coverage of these tags is not measured yet.

## Domain rules or explicit TODO

- Missing information is never presented as a confirmation of accessibility (`docs/product/specification.md`, M10).
- A segment without complete data is never green (`docs/product/specification.md`, M7).

## Notes on data, performance and security

- The thresholds decide what a person in a wheelchair, with a baby stroller or with walking difficulties is warned about; a threshold that is too lenient shows a barrier as passable.

## Open questions

1. Does the result go into the specification as version 3, and who approves that change? `Block: no`
2. What are the thresholds: from what incline a way is a steep incline, what width is a narrow passage, from what height a kerb is high, which surface and smoothness values are poor? `Block: no`
3. Does a way not tagged as steps count as a known "no stairs" for the segment state? `Block: no`
4. When does an OpenStreetMap fact contradict a user report, so that the report shows as an unverified report icon instead of making the segment red? `Block: yes` (category: source of truth for data)
5. By when must the decision be made, given the deadline at 11:00 on 4 October 2026? `Block: no`
