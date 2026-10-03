# PRD: Mapping of OpenStreetMap tags to the closed list of barriers and amenities

Document state: 2026-10-03

## Business goal

The route of the MVP avoids barriers known from OpenStreetMap and colors every segment by what is known about it (`plans/mvp/MVP_PRD.md` FR-2, FR-3, FR-10, FR-11). Both need one rule that says, for every barrier and amenity of the closed list of `docs/product/specification.md` M3, which OpenStreetMap tags and values make it present, absent or unknown. This initiative delivers that rule with its thresholds, approved as a product rule by the owner of the specification, so that `plans/mvp/MVP_PLAN.md` Q-8 is closed and the import, the route, the map and the list all read the same result.

It serves the Kraków judging criteria of usefulness for the chosen group (25%) and of data reliability and presentation (15%) directly: the thresholds decide what a person in a wheelchair, with a baby stroller or with walking difficulties is warned about, and the rule of what is unknown decides whether the app keeps its promise never to present missing information as accessible (M10).

## Problem and its consequences

The specification lists five barriers and six amenities, and says that OpenStreetMap provides kerbs, incline, surface, smoothness, steps, elevators, toilets and benches (M6), but not which values count as which item. Without the rule:

- the route cannot avoid OpenStreetMap barriers, because nothing says that `incline=12%` is a steep incline or that `surface=sett` is a poor surface;
- the segment states of M7 cannot tell a known attribute from a missing one, so a segment could turn green on missing data, which is the harm M10 forbids;
- the contradiction between OpenStreetMap and a user report, which the Kraków demo has to show (M10), has no definition, so the same segment could be red for one part of the team and follow OpenStreetMap for another;
- every person writing the import, the route and the list would pick their own thresholds, and the app would contradict itself.

A threshold that is too lenient shows a barrier as passable to exactly the people who rely on the warning; a threshold that is too strict makes most of Kraków red and the route useless.

## Scope

- The rule for each of the eleven items of the closed list: which OpenStreetMap tags and values make it present, absent or unknown, for ways and for points.
- The numeric thresholds and value lists behind the rule, one set common to every profile.
- For each barrier, the attributes that have to be known for a segment to be in the state no barrier, and their names as the list of the route shows them.
- The meaning of "OpenStreetMap contradicts a user report" for each barrier.
- The number of steps and the date of the last OpenStreetMap edit carried by the facts the rule produces.
- The entry of these rules, with their thresholds and value lists, into `docs/product/specification.md` version 3, together with the rules of `plans_finished/osm_data_source/` as one change approved by the user (`plans_finished/osm_data_source/OSM_DATA_SOURCE_SHAPE.md`, section Smallest meaningful scope). This initiative writes the whole of version 3, the rules of `plans_finished/osm_data_source/` included. Decided by the user on 2026-10-03 in phase B, against keeping the thresholds out of version 3 until the import person confirms them and against version 3 waiting for phase B of `plans_finished/osm_data_source/`.
- The decision handed to `plans/mvp/MVP_PLAN.md` as the decision closing Q-8.

## Out of scope

- Building the import that applies the rule. It is a work package of `plans/mvp/`, together with the import and refresh decided in `plans_finished/osm_data_source/` and the backend architecture of Q-11 there, as `plans_finished/geocoding/` and `plans_finished/osm_data_source/` did. Agent decision at C:40, without asking: the same split the user chose for the two sibling initiatives; to be confirmed at the gate of this PRD.
- Changing the closed list itself; it is decided by the specification.
- Thresholds that depend on the profile. The presets only switch barrier types on or off (M1), so a threshold is the same for everyone; a profile that wants a different threshold is a change of the specification, not of this rule.
- Which stretch of way a point report lies on, and within what distance of an opposite kerb fact a report counts as contradicted. Recorded in the shape as a TODO for phase B of `plans_finished/routing_engine/`.
- What happens to an OpenStreetMap fact that disappears from or returns in a fresh copy; decided in `plans_finished/osm_data_source/`.
- Data outside OpenStreetMap, such as an elevation model for the incline or open city data (O4).
- The two defects of the specification noticed in the shape interview - geozones avoided whatever their status, and the rule "disputed" against scenario 3 of `plans/mvp/MVP_SHAPE.md` - which concern the route and the statuses, not the mapping. They were reported to the user and are not settled here.

## Functional requirements

FR-1. Rule for every item. Every barrier and amenity of the closed list has a rule, given in the section Domain rules, that turns OpenStreetMap tags into the state present, absent or unknown on the stretch of way or at the point the tags belong to. Where an item has no OpenStreetMap value that means absent, the rule says so, and the item is then only present or unknown.

FR-2. Common thresholds. The thresholds and value lists of the rule are one set for all profiles. A change of a value changes the result in the same way for every profile and comes into effect with the next import.

FR-3. Attributes behind the segment state. For each barrier, the rule names the attributes that have to be known for that barrier to count as known on a segment. A segment is in the state no barrier for a profile only when every barrier of the profile is known on it and none is present; when some are known and not present and the others unknown, it is in the state partial data, and the list of the route names the unknown attributes by the names given in the section Domain rules.

FR-4. Stairs known by default. A way not tagged as steps counts as a known "no stairs" for the segment state.

FR-5. Contradiction. OpenStreetMap contradicts a user report of a barrier only by an opposite fact of the closed list (a lowered kerb against a high kerb) or by an explicit tag value on the same stretch that the rule classifies as not a barrier. The absence of a tag never contradicts a report, so in particular a way not tagged as steps never contradicts a report of stairs.

FR-6. Number of steps. A stairs fact from OpenStreetMap carries the number of steps when OpenStreetMap gives it.

FR-7. Source and date. Every fact the rule produces carries the source OpenStreetMap and the date of the last edit of the OpenStreetMap element its tags belong to, as a calendar day in the Europe/Warsaw zone (`plans/mvp/MVP_PRD.md` AC-14).

FR-8. Unmapped values. A tag value the rule does not list leaves the item unknown; it never makes a barrier absent and never makes an amenity present.

FR-9. No data. A segment is in the state no data when none of the barriers of the profile is known on it other than by the default of FR-4. A segment whose only known attribute is the default "no stairs" is therefore grey, not partial data. Decided by the user on 2026-10-03 at the gate of this PRD, against keeping the literal reading under which the state no data could not occur for any preset.

FR-10. Way marked as not accessible. A way tagged `wheelchair=no` in OpenStreetMap is never in the state no barrier, for any profile: when no barrier of the profile is present on it, it is at most partial data, and the list of the route says that OpenStreetMap marks the way as not accessible for wheelchairs. The tag adds no barrier, so the route does not avoid the way because of it. Decided by the user on 2026-10-03 at the gate of this PRD, against ignoring the tag and against adding a barrier to the closed list.

FR-11. Recorded in the specification. The rules of FR-1 - FR-10 and FR-12 and the contradiction rule enter `docs/product/specification.md` version 3, sections M2, M4, M6, M7 and M8 and Decision provenance, together with the rules of `plans_finished/osm_data_source/`, approved by the user. The thresholds and value lists of the section Domain rules enter the same version 3 as the values approved by the user on 2026-10-03; a value the import person changes before the demo is recorded enters a later version. Decided by the user on 2026-10-03 in phase B, replacing the earlier wording under which the thresholds entered only the version that follows their approval.

FR-12. Ways for motor traffic. On a way for motor traffic the surface, the smoothness and the width of the way describe the carriageway, so they count for a person on foot only when the way has no sidewalk and the person walks on the carriageway. When the way carries its sidewalk as tags of the way, the surface, the smoothness and the width come from the tags of the sidewalk; without them, and when the way says nothing about a sidewalk or says that the sidewalk is mapped as a separate way, these attributes are unknown. The incline of the way counts in every case, and every other walking way is read by its own tags. Decided by the user on 2026-10-03 in phase B, against never reading the carriageway and against reading the tags of the way as they are, which would show a sidewalk as without barriers on the strength of the tags of the road (M10).

## Acceptance criteria

AC-1 (FR-1, FR-6). A way tagged `highway=steps`, `step_count=12`, `handrail:right=yes` gives the barrier stairs with 12 steps and the amenity handrail at stairs. A way tagged `highway=steps` with `ramp:wheelchair=yes` also gives the amenity ramp.

AC-2 (FR-1, FR-3). A footway tagged `surface=paving_stones`, `incline=4%`, `width=2` that does not meet a carriageway is in the state no barrier for each of the three presets.

AC-3 (FR-3). Segment Y of `plans/mvp/MVP_SHAPE.md` scenario 9 - asphalt, no steps, no incline, no kerb data, no width - is in the state partial data for the preset "I use a wheelchair", and the list names the incline, the kerbs and the width as unknown. For the preset "Walking is difficult for me" it is partial data with only the incline unknown.

AC-4 (FR-1). `incline=8%` and `incline=-8%` give a steep incline; `incline=5%` gives no steep incline; `incline=up` leaves the incline unknown.

AC-5 (FR-1). At a crossing, `kerb=raised` gives a high kerb; `kerb=lowered`, `kerb=flush` and `kerb:height=0.02` give a lowered kerb; `kerb=rolled` without a height and `kerb=yes` leave the kerb unknown.

AC-6 (FR-1). `surface=sett` without a smoothness gives a poor surface; `surface=sett` with `smoothness=intermediate` gives no poor surface; `surface=asphalt` with `smoothness=bad` gives a poor surface.

AC-7 (FR-1). `width=0.8` gives a narrow passage; `width=1.2` gives none; a `barrier=kissing_gate` on the way gives a narrow passage whatever the width.

AC-8 (FR-1). `amenity=toilets` with `wheelchair=yes` gives an accessible toilet; `amenity=bench` gives a rest place; `highway=elevator` gives an elevator. `amenity=toilets` without a wheelchair tag gives no accessible toilet and leaves it unknown.

AC-9 (FR-5). The run of shape scenario 1 (report of poor surface on a way tagged `surface=asphalt`) gives a contradicted report from 10:00 to 11:20 and a red segment avoided by the route from 11:20. The run of shape scenario 2 (report of stairs on a way without steps) gives a report that is not contradicted, a red segment, and an alternative route.

AC-10 (FR-2). Changing the threshold of the steep incline from 6% to 8% and importing again turns a way tagged `incline=7%` from a steep incline into no steep incline for the presets "I use a wheelchair" and "Walking is difficult for me" alike.

AC-11 (FR-7). A fact from a way last edited in OpenStreetMap at 23:30 UTC on 2 October 2026 shows the date 3 October 2026.

AC-12 (FR-8). A way tagged `surface=unknown_value` has the surface unknown, and a segment made of it is never in the state no barrier for a profile that avoids poor surface.

AC-13 (FR-9). A footway with none of `surface`, `smoothness`, `incline`, `width` and no crossing, not tagged as steps, is in the state no data for each of the three presets. The same footway with `surface=asphalt` is partial data.

AC-14 (FR-10). A footway tagged `wheelchair=no`, `surface=asphalt`, `incline=2%`, `width=2`, without a crossing, is partial data for each of the three presets, the list names the `wheelchair=no` marking, and the route does not avoid it when it is the shortest way.

AC-15 (FR-11). `docs/product/specification.md` version 3 states the contradiction rule, the stairs default, the thresholds being common to all profiles, the rule of the state no data and the `wheelchair=no` marking in sections M2, M4 and M7, the tag rules with their thresholds and value lists and the rule of ways for motor traffic in section M6, the rules of `plans_finished/osm_data_source/` in sections M4 and M6, and its Decision provenance names this initiative and `plans_finished/osm_data_source/`.

AC-16 (FR-12). A way tagged `highway=residential`, `sidewalk=both`, `surface=asphalt`, `width=7`, without any sidewalk surface or width tag, has the surface and the width unknown and is never in the state no barrier. The same way tagged `sidewalk=no` instead has no poor surface and no narrow passage. The same way tagged `sidewalk=both` and `sidewalk:both:surface=sett` has a poor surface.

## Domain rules

The rules of the section Domain rules of `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md` hold. The tag rules and the thresholds below were proposed by the agent for the import person, from common OpenStreetMap tagging practice and the OpenStreetMap wiki definitions, not checked against Kraków data. The user approved them on 2026-10-03 at the gate of this PRD as default values: the import runs on them, and the import person confirms or changes them before the demo is recorded, so that the demo runs on approved values (shape question 5). The kerb as an attribute only at crossings and the width as an attribute required for the narrow passage were decided by the user at the same gate, against inferring "no narrow passage" from a missing width and against requiring the kerb on every segment.

Barriers:

| Item           | Present                                                                                                            | Absent (explicit, can contradict a report)                                                     | Known absent by default                                  | Unknown                                                      | Attribute named in the list |
| -------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------ | --------------------------- |
| Stairs         | the way is `highway=steps`, or a point `barrier=step` on it; number of steps from `step_count`                     | never                                                                                          | the way is not `highway=steps` and has no `barrier=step` | never                                                        | -                           |
| High kerb      | at a point where the way meets a carriageway: `kerb=raised`, or `kerb:height` above 0.03 m                         | the opposite fact lowered kerb                                                                 | -                                                        | `kerb=rolled` or `kerb=yes` without a height, or no kerb tag | kerbs                       |
| Poor surface   | `smoothness` of `bad` or worse; without `smoothness`, a `surface` from the poor list                               | `smoothness` of `intermediate` or better; without `smoothness`, a `surface` from the good list | -                                                        | neither tag, or a value on neither list                      | surface                     |
| Steep incline  | numeric `incline` steeper than 6% in either direction, degrees converted to percent                                | numeric `incline` of at most 6%                                                                | -                                                        | no `incline`, or only `up` or `down`                         | incline                     |
| Narrow passage | `width` below 0.9 m, or a point `barrier=kissing_gate`, `turnstile`, `stile` or `full-height_turnstile` on the way | `width` of at least 0.9 m and no such point                                                    | -                                                        | no `width`                                                   | width                       |

- Poor surface list: `sett`, `unhewn_cobblestone`, `cobblestone`, `gravel`, `pebblestone`, `grass`, `grass_paver`, `dirt`, `earth`, `ground`, `mud`, `sand`, `rock`, `woodchips`, `stepping_stones`.
- Good surface list: `asphalt`, `concrete`, `concrete:plates`, `paving_stones`, `compacted`, `fine_gravel`, `metal`, `wood`, `rubber`.
- `smoothness` wins over `surface` when both are given, because it describes the passability of the actual stretch: the OpenStreetMap wiki defines `intermediate` as usable by a wheelchair and `bad` as not.
- The kerb is an attribute only of a segment where the walking way meets a carriageway, that is at a crossing; on a stretch of pavement without a crossing there is no kerb to know.
- Ways for motor traffic are those with `highway` of `trunk`, `primary`, `secondary`, `tertiary`, their `_link` ways, `unclassified`, `residential` and `service`. On them `surface`, `smoothness` and `width` count only when the way has no sidewalk on either side (`sidewalk=no`, `sidewalk=none` or `sidewalk:both=no`). With a sidewalk tagged on the way (`sidewalk` or `sidewalk:both` of `both`, `left`, `right` or `yes`) they are read from `sidewalk:surface`, `sidewalk:both:surface`, `sidewalk:smoothness`, `sidewalk:both:smoothness`, `sidewalk:width` and `sidewalk:both:width`. In every other case, `sidewalk=separate` and a missing sidewalk tag included, they are unknown. `incline` counts on every way (FR-12).

Amenities:

| Item               | Present                                                                                                        | Absent                                                         | Unknown              |
| ------------------ | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | -------------------- |
| Ramp               | `ramp:wheelchair=yes` or `ramp=yes` on steps or an entrance                                                    | `ramp=no` or `ramp:wheelchair=no`                              | otherwise            |
| Elevator           | a point `highway=elevator`                                                                                     | never                                                          | otherwise            |
| Lowered kerb       | `kerb=lowered`, `kerb=flush`, `kerb=no`, or `kerb:height` of at most 0.03 m                                    | the opposite fact high kerb                                    | as for the high kerb |
| Accessible toilet  | `amenity=toilets` with `wheelchair=yes` or `wheelchair=designated`, or any place with `toilets:wheelchair=yes` | `wheelchair=no`, `wheelchair=limited`, `toilets:wheelchair=no` | otherwise            |
| Rest place         | `amenity=bench`, `leisure=picnic_table`, or a stop or shelter with `bench=yes`                                 | `bench=no`                                                     | otherwise            |
| Handrail at stairs | on `highway=steps`: `handrail=yes` or `handrail:left`, `handrail:right` or `handrail:center` set to `yes`      | `handrail=no`, or every given side `no`                        | otherwise            |

The thresholds in short: steep incline above 6%, narrow passage below 0.9 m, high kerb above 0.03 m, poor surface by smoothness `bad` or worse and otherwise by the surface lists.

## Dependencies and impact on other modules

- No product code exists, so nothing in the repository is changed indirectly. The decision closes `plans/mvp/MVP_PLAN.md` Q-8 and feeds Q-10 there, the domain model of facts, which depends on Q-8.
- `plans_finished/routing_engine/` reads the result: a profile, the user facts and the contradiction rule on top of a per-segment present, absent or unknown. The engine does not change the rule, and the rule does not depend on the engine (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, section Challenging own assumptions).
- `plans_finished/osm_data_source/` decides the copy the rule runs on and the fate of facts that disappear or return; its scenarios use this rule (`surface=sett` as poor surface, a way without steps as not contradicting stairs) and its rules enter the same version 3 of the specification, written by this initiative (FR-11).
- `plans/mvp/MVP_PRD.md` AC-10 and `plans/mvp/MVP_SHAPE.md` scenario 9 name only the incline and the kerbs as unknown for segment Y; with this rule a wheelchair profile also misses the width (AC-3 here), so AC-10 there gains the width. Scenario 9 also has to be read with segment Y meeting a carriageway, because the kerb is an attribute only at crossings.
- `plans/mvp/MVP_PRD.md` FR-10 and its section Domain rules define the state no data as "nothing known"; FR-9 here makes the default "no stairs" not count, and FR-10 here adds the `wheelchair=no` marking. Both reach the MVP through version 3 of the specification.
- `plans/api_contract/` and the list of the route show the attribute names of the section Domain rules.

## Risks and notes

- Coverage: `incline` and `width` are rare on Kraków footways. Measured on 2026-10-03 in phase B (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md`, section Facts): of 5 505 `incline` tags on the foot ways of Kraków 5 415 are only `up` or `down`, 2 295 foot ways have a `width`, and 80 have a surface, an incline and a width together. With this rule the presets "I use a wheelchair" and "Walking is difficult for me" will see almost no green segment outside the sample data of the demo district. That is the honest result the shape accepted, but the demo has to explain it.
- `wheelchair=no` is applied to every profile, also to the stroller and the walking-difficulty presets, for which a wheelchair marking may be stricter than needed. The user chose this at the gate as the safer reading of M10; the cost is fewer green segments.
- `surface=sett` covers a large part of the Old Town; without a smoothness it is a poor surface, so routes in the centre will avoid much of it for every preset. That is consistent with `plans_finished/osm_data_source/` scenario 2, but it shapes the demo.
- `kerb=rolled` is left unknown rather than classified, because a rolled kerb may or may not be passable for a wheelchair depending on its height.
- `wheelchair=limited` on toilets counts as absent: limited is not a confirmation of accessibility (M10).
- Amenity reports contradicted by OpenStreetMap - for example a report of a lowered kerb where OpenStreetMap has `kerb=raised` - are not covered by the contradiction rule of the shape, which concerns barrier reports. With the closed list the only such pair is the kerb, where the same rule read in the other direction applies. Agent decision at C:40, without asking: the kerb is the one pair of opposite items of the closed list, so the rule is symmetric by construction.
- The thresholds are default values until the import person confirms them; if that does not happen before the demo is recorded, the demo runs on values approved only by the owner of the specification.
