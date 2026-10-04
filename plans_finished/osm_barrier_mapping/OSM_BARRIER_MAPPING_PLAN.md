# Plan: Mapping of OpenStreetMap tags to the closed list of barriers and amenities

Document state: 2026-10-03, plan closed

## Goal

Implement `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PRD.md` (FR-1 - FR-12, AC-1 - AC-16): write version 3 of `docs/product/specification.md` with the tag rules, their thresholds and the contradiction rule of this initiative and the rules of `plans_finished/osm_data_source/` (FR-11, AC-15), close `plans_finished/mvp/MVP_PLAN.md` Q-8 with the technical decisions the import and the route apply, and bring the MVP PRD and the sibling shapes in line with version 3. No product code is written here: the import that applies the rule is a work package of `plans_finished/mvp/` (PRD, Out of scope), and the acceptance criteria about tags and segments become the tests that D-17 assigns to the work packages there.

## Facts

F-1. The specification is at version 2: M2 keeps an unverified barrier "not contradicted by OpenStreetMap" without defining a contradiction, M4 lets an OpenStreetMap fact prevail over "a contradicting user report", M6 lists the attributes OpenStreetMap provides, M7 defines four segment states, and M8 names the missing attributes. | doc:`docs/product/specification.md` the state line, M2, M4, M6, M7 and M8 | 2026-10-03
F-2. All three presets avoid stairs and poor surface, the wheelchair and stroller presets avoid a high kerb and a narrow passage, and the wheelchair and walking presets avoid a steep incline. | doc:`docs/product/specification.md` M1 | 2026-10-03
F-3. The introduction of the specification describes versions 1 and 2, its Open questions say "None at version 2", and its Decision provenance has entries for versions 1 and 2. | doc:`docs/product/specification.md` section Why this document exists, section Open questions and section Decision provenance | 2026-10-03
F-4. Version 2 of the specification is named in the Scope and Domain rules of the MVP PRD, in the Goal of the MVP plan and twice in the MVP shape. | cmd:`Grep "version 2"` over the repository -> `plans_finished/mvp/MVP_PRD.md` sections Scope and Domain rules, `plans_finished/mvp/MVP_PLAN.md` section Goal and `plans_finished/mvp/MVP_SHAPE.md` sections Smallest meaningful scope and Functional requirements | 2026-10-03
F-5. The MVP plan holds the mapping as open question Q-8, has the decisions D-1 - D-4, D-4 written by the implementation of `plans_finished/osm_data_source/` in a parallel session, and refers to Q-8 in its Risks and in Q-10 with its inputs and caveats. | doc:`plans_finished/mvp/MVP_PLAN.md` D-1 - D-4, section Risks, Q-8 and Q-10 with its inputs and caveats | 2026-10-03
F-6. The MVP PRD says in AC-10 that the list for the segment of shape scenario 9 names the incline and the kerbs as unknown, and defines the state no data as nothing known. | doc:`plans_finished/mvp/MVP_PRD.md` AC-10 and section Domain rules | 2026-10-03
F-7. The PRD of `plans_finished/osm_data_source/` passed its gate, puts its rules into version 3 of the specification in M4 and M6 together with this initiative, and states them as FR-3 and FR-5 - FR-11. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PRD.md` section Scope, section Out of scope, FR-3 - FR-11 and section Dependencies and impact on other modules | 2026-10-03
F-8. The shapes of the routing engine and of the API contract are in the interview and record neither what the route reads from the mapping nor the names of the missing attributes. | doc:`plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md` the state line and section Current state; doc:`plans_finished/api_contract/API_CONTRACT_SHAPE.md` the state line and section Current state | 2026-10-03
F-9. No product code exists, so the rule has no call site, schema object or configuration key yet. | cmd:`git ls-files` -> Python code only under `tests/architecture/` and in the agent hooks; doc:`plans_finished/mvp/MVP_PLAN.md` F-3 | 2026-10-03
F-10. Thresholds and default values of domain rules that are the same in every environment and used in one place belong to the third configuration layer, next to their code. | doc:`docs/standards/standard_config.md` section Three configuration layers and four storage places; doc:`docs/standards/standard_config.md` section Rule for assigning a value to a layer | 2026-10-03
F-11. Unit tests run without a database and without the network, and every domain rule has a test of its positive side and of its refusal. | doc:`docs/standards/standard_tests.md` section Test layers; doc:`docs/standards/standard_tests.md` section Coverage scope | 2026-10-03
F-12. The calendar day of the Europe/Warsaw zone is computed from an aware instant, and every date the app shows is such a calendar day. | doc:`docs/standards/standard_time.md` section Time windows in data: local day versus UTC day; doc:`docs/product/specification.md` M10 | 2026-10-03
F-13. The Geofabrik extracts drop only the user, uid and changeset fields, so the timestamp of every element version stays in the copy. | cmd:`curl https://download.geofabrik.de/technical.html` -> "The user , uid and changeset fields are missing in these files since May 3, 2018." | 2026-10-03
F-14. Within the administrative boundary of Kraków there are 89 254 foot ways (`highway` of footway, path, pedestrian or steps): 66 923 with `surface`, 12 612 with `smoothness`, 5 505 with `incline`, 2 295 with `width`, 166 with `wheelchair=no`, 6 177 tagged `footway=crossing` and 11 552 tagged `footway=sidewalk`. | cmd:Overpass `out count` on `https://maps.mail.ru/osm/tools/overpass/api/interpreter` within `area["boundary"="administrative"]["name"="Kraków"]["admin_level"="8"]` -> the numbers above | 2026-10-03
F-15. Of the 5 505 `incline` values on those ways 5 415 are `up` or `down`, 74 are percent values, 8 are `yes`, 4 bare numbers, 3 `steep` and 1 `flat`, and none is given in degrees. | cmd:Overpass `[out:csv(...)]` export of the tags of those ways, counted by form -> the numbers above | 2026-10-03
F-16. Only 80 of the 82 197 foot ways other than steps have a surface, an incline and a width together; 2 007 have a surface or a smoothness and a width, and 523 a surface or a smoothness and an incline. | cmd:the same export, counted -> the numbers above | 2026-10-03
F-17. Of the 2 295 `width` values 2 289 are plain numbers in metres, 1 has the form `N m`, 2 use a decimal comma, 2 are `3c` and 1 is `grass`; 106 are below 0.9. | cmd:the same export, counted by form -> the numbers above | 2026-10-03
F-18. The most common surfaces of those ways are `paving_stones` 42 404, `asphalt` 10 576, `paved` 5 241, `concrete` 2 559 and `sett` 742; `paved` and `unpaved` (174) are on neither list of the PRD, and all 12 612 `smoothness` values are among the eight standard ones. | cmd:the same export, counted -> the numbers above | 2026-10-03
F-19. Kerb information sits on nodes: 5 324 nodes have `kerb` (`lowered` 3 840, `flush` 1 077, `raised` 350, `no` 48, `yes` 7, `normal` 2), 4 621 of them are `barrier=kerb`, 631 `highway=crossing` nodes have `kerb`, only 32 ways have `kerb`, and `kerb:height` stands on 2 nodes, both `0.4m`. | cmd:Overpass `out count` and `[out:csv(...)]` export of `node[kerb]` within the area of Kraków -> the numbers above | 2026-10-03
F-20. In the bounding box of Kraków 371 nodes have `kerb=raised`, 6 of them on a bus stop, platform or tram stop node, and 59 nodes are `barrier=step`. | cmd:Overpass `out count` for `node[kerb=raised]` and `node[barrier=step]` in the bounding box `49.9676668,19.7922355,50.1261338,20.2173455` -> the numbers above | 2026-10-03
F-21. In the same bounding box 649 ways of the classes living street, residential, unclassified, tertiary, secondary and primary carry a sidewalk as a tag of the road; 641 of them have `surface`, 74 have `width` and 149 have a `sidewalk:*:surface` tag. | cmd:Overpass `out count` for `way["highway"~"^(living_street|residential|unclassified|tertiary|secondary|primary)$"]["sidewalk"~"^(both|left|right|yes)$"]` and its subsets -> 649, 641, 74, 149 | 2026-10-03
F-22. On the steps of Kraków `handrail` is `yes` 2 386 times, `no` 1 653, `left` 3 and `right` 1; `ramp` is `no` 2 474, `yes` 902 and `separate` 165; `ramp:wheelchair` is `yes` 171, `separate` 122, `no` 28 and `limited` 3; 3 145 of the 7 057 steps have `step_count`. | cmd:the export of F-15 filtered to `highway=steps`, counted; cmd:Overpass `out count` for steps with `step_count` -> the numbers above | 2026-10-03
F-23. The OpenStreetMap wiki lists the wheelchair among the users of `smoothness=intermediate` and not among those of `smoothness=bad`. | cmd:`curl "https://wiki.openstreetmap.org/w/index.php?title=Template:Description:smoothness&action=raw"` -> `(wheels) city bike, sport cars, wheel chair, ...` for intermediate, `(robust_wheels) trekking bike, normal cars, ...` for bad | 2026-10-03
F-24. The wiki gives `incline` in percent with `%` or in degrees with `°`, and `up` or `down` when the value is not known. | cmd:`curl "https://wiki.openstreetmap.org/w/index.php?title=Key:incline&action=raw"` -> section Values | 2026-10-03
F-25. The wiki puts `barrier=kerb` with `kerb` on the node where a way crosses the kerb, lets a `kerb` on a crossing node stand for both sides of the crossing, says that `kerb=raised` on a bus stop or a platform describes the boarding edge, and reads `kerb:height` in metres by default. | cmd:`curl "https://wiki.openstreetmap.org/w/index.php?title=Key:kerb&action=raw"` -> sections On a node, Kerb height and Examples | 2026-10-03
F-26. The wiki reads `width` in metres by default, and the surface key names `sidewalk:surface`, `sidewalk:both:surface`, `sidewalk:left:surface` and `sidewalk:right:surface` apart from the `surface` of the road. | cmd:`curl "https://wiki.openstreetmap.org/w/index.php?title=Key:width&action=raw"` -> the `description` of its infobox; cmd:`curl "https://wiki.openstreetmap.org/w/index.php?title=Key:surface&action=raw"` -> section Surface for footways and cycleways | 2026-10-03
F-27. Before this change the architecture tests fail in four tests, every reported path being a file of the impeccable skill under `.claude/` or `.agents/`, while prettier passes on every file this plan changes. | cmd:`venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` -> `4 failed, 110 passed`, failing tests `test_every_paired_skill_is_at_parity`, `test_every_paired_agent_role_is_at_parity`, `test_repository_has_no_forbidden_characters`, `test_repository_has_no_bold_in_prose`; cmd:`npx prettier --check` on the files of the Scope of changes -> `All matched files use Prettier code style!` | 2026-10-03
F-28. The plan of `plans_finished/osm_data_source/`, closed on 2026-10-03 while this plan was written, says in its D-20 that version 3 with its rules is written by this initiative and that it writes nothing into the specification, finds that steps 1.4 and 1.5 here cover FR-2 - FR-11 of its PRD, keeps the weight of a vote after its 30-day identifier is deleted out of version 3 (D-21 there), and closes Q-2 of the MVP plan with steps that do not touch the passages of steps 2.4 and 2.7 here. | doc:`plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md` the state line, D-20, D-21 and section Scope of changes | 2026-10-03

## Decisions

D-1. The thresholds and value lists enter version 3 of the specification in full, as the values the user approved on 2026-10-03; a value the import person changes before the demo is recorded enters a later version. Decided by the user on 2026-10-03 in phase B, against keeping them out of version 3 until the import person confirms them. PRD FR-11 and AC-15 were amended accordingly.

D-2. This initiative writes the whole of version 3, the rules of `plans_finished/osm_data_source/` included, so that version 3 is one edit with one approval. Decided by the user on 2026-10-03 in phase B, against leaving version 3 open until phase B of `plans_finished/osm_data_source/` and against a separate version 4 for those rules. The plan of `plans_finished/osm_data_source/` agrees in its D-20, decided by the user on 2026-10-03 after the two sessions compared their plans, and its session checked that steps 1.4 and 1.5 here cover its PRD (F-28). Version 3 leaves out the weight of a vote after its 30-day identifier is deleted, which that initiative settles in its PRD and hands to Q-10 of the MVP plan (D-21 there).

D-3. On ways for motor traffic `surface`, `smoothness` and `width` describe the carriageway, so they count only when the way has no sidewalk; with a sidewalk tagged on the way they are read from the sidewalk tags, and otherwise they are unknown, while `incline` counts on every way. Decided by the user on 2026-10-03 in phase B, against never reading the carriageway and against reading the tags of the road as they are, which would have made up to 649 roads with a sidewalk tag green on the strength of the carriageway (F-21, F-26). The rule was added to the PRD as FR-12, AC-16 and a bullet of Domain rules, because it is a product rule the PRD did not cover.

D-4. After version 3 this plan also brings `plans_finished/mvp/MVP_PRD.md` and `plans_finished/mvp/MVP_PLAN.md` in line: AC-10 gains the width, the rule of segment states follows M7 of version 3, and the references to version 2 become version 3 (F-4, F-6). `plans_finished/mvp/MVP_SHAPE.md` stays unchanged as the record of its interview. Decided by the user on 2026-10-03 in phase B, against changing only AC-10 and the rule of states and against leaving the MVP PRD untouched.

D-5. The tag rules enter the specification as a subsection of M6, "Reading OpenStreetMap tags", not as a new feature M12, because the MVP PRD and plan refer to the mandatory features as M1-M11 and M6 is the feature of OpenStreetMap data. Agent decision at C:40, without asking.

D-6. The rule turns the tags of one OpenStreetMap element into its facts, once per copy and independently of the profile, on the elements of the pedestrian network that `plans_finished/routing_engine/` and `plans_finished/osm_data_source/` decide. For every way of the network it gives: for each of stairs, poor surface, steep incline and narrow passage one of the states present, absent, absent by default and unknown, where absent is used only for an explicit tag value on the passable side of the rule and absent by default only for stairs on a way that is not `highway=steps`; the number of steps when the way is `highway=steps` with a `step_count` read by D-9; the `wheelchair=no` marking; and the ramp and handrail amenities of a `highway=steps` way (D-13). For every node of such a way it gives the point facts of D-11, the kerb point of D-8, and whether the node also belongs to a way for motor traffic. For every element that carries an amenity it gives the amenity facts of D-13. Every fact carries the type and the OpenStreetMap identifier of its element and the date of D-15. The high kerb has no way state: it comes only from kerb points (D-7, D-8). Agent decision at C:40, without asking: absent and absent by default have to stay apart, because only the first contradicts a report (PRD FR-5) and only the second does not count for the state no data (PRD FR-9).

D-7. A segment of a walking way, as the route defines it, takes for stairs, poor surface, steep incline and narrow passage: present when the way state is present or a point fact of that barrier lies on the segment; absent when the way state is absent and no such point fact lies on it; absent by default for stairs when the way state is absent by default and no `barrier=step` lies on the segment; unknown otherwise. A high kerb point on any segment makes the high kerb present there. The kerbs are a required attribute only of a segment of a way that is not for motor traffic and meets a carriageway, which means: the segment is part of a way tagged `footway=crossing`, `path=crossing` or `cycleway=crossing`, or one of its nodes is a kerb point, a `highway=crossing` node or a node that also belongs to a way for motor traffic. On such a segment the high kerb is absent when it has at least one kerb point and all its kerb points are lowered, and unknown when it has no kerb point or one of them is unknown. A kerb point on a `highway=crossing` node stands for both kerbs of the crossing (F-25). Agent decision at C:40, without asking: kerb data sits on nodes (F-19), and on a road walked on the carriageway there is no kerb to step over.

D-8. A kerb point is a node with a `kerb` or `kerb:height` tag or with `barrier=kerb`, except a node tagged `highway=bus_stop`, `public_transport=platform`, `public_transport=stop_position`, `railway=platform` or `railway=tram_stop`, where the kerb describes the boarding edge of the stop (F-25). It is high when `kerb=raised` or `kerb:height` is above 0.03 m; lowered when `kerb` is `lowered`, `flush` or `no` or `kerb:height` is at most 0.03 m; and unknown otherwise, for `kerb=yes`, `kerb=rolled`, `kerb=normal`, any other value and `barrier=kerb` alone. When the two tags disagree, the point is high. A lowered kerb point is also the amenity lowered kerb, and a high one its explicit absence. Agent decision at C:40, without asking: a conflict resolves towards the barrier, because M10 forbids hiding a barrier behind contradictory data; the stop exclusion follows the wiki and concerns 6 of 371 raised kerbs (F-20).

D-9. Numbers are read only in these forms, and every other form is unknown (PRD FR-8): an incline is an optionally signed decimal number with a dot followed by `%` or `°`, with or without a space before the sign, degrees converted to percent as 100 times the tangent of the angle, steep when its absolute value is above 6; a length - `width`, `kerb:height`, `sidewalk:width`, `sidewalk:both:width` - is a decimal number with a dot, optionally followed by `m` with or without a space, in metres; a number of steps is a positive integer. A value holding several values separated by `;` is unknown. In the copy of Kraków this leaves unknown 16 `incline` values besides the 5 415 `up` and `down`, and 5 `width` values, and reads both `kerb:height=0.4m` as high (F-15, F-17, F-19). Agent decision at C:40, without asking: these are the forms the wiki defines (F-24 - F-26), and a guessed unit would turn a missing fact into a known one.

D-10. On a way read by its own tags, or by its sidewalk tags under D-12, `smoothness` of `excellent`, `good` or `intermediate` makes poor surface absent and `smoothness` of `bad`, `very_bad`, `horrible`, `very_horrible` or `impassable` makes it present. A `smoothness` value outside these eight counts as no `smoothness`, and then `surface` decides by the two lists of the PRD section Domain rules; a surface on neither list leaves poor surface unknown. Agent decision at C:40, without asking: the PRD does not say what an unrecognised smoothness does, and ignoring it lets only a listed value decide. In the copy of Kraków every `smoothness` value is one of the eight, and `surface=paved` on 5 241 foot ways stays unknown without a `smoothness` (F-18).

D-11. A node of a way of the pedestrian network gives stairs present at that point when it is `barrier=step`, with the number of steps from its `step_count` read by D-9, and a narrow passage present at that point when it is `barrier=kissing_gate`, `turnstile`, `stile` or `full-height_turnstile`. A node that belongs to no way of the network gives no point barrier. Agent decision at C:40, without asking: the PRD table says on the way, and a node is on a way exactly when the way lists it.

D-12. The classes of ways for motor traffic and the sidewalk keys are those of the PRD section Domain rules. The per side keys `sidewalk:left:*` and `sidewalk:right:*` are not read, and a way tagged only `sidewalk:left` or `sidewalk:right` counts as saying nothing about a sidewalk, so its surface, smoothness and width are unknown. The sidewalk keys are read by D-9 and D-10 exactly as `width`, `smoothness` and `surface`. Agent decision at C:40, without asking: a route segment does not know which side of the road it runs on, and a per side value would have to be guessed.

D-13. Amenities are read from these elements, and a fact of an area sits at a point inside the area: elevator - a node `highway=elevator`, or an area with it; accessible toilet - an element `amenity=toilets` with `wheelchair` of `yes` or `designated` (present) or of `no` or `limited` (absent), and any element with `toilets:wheelchair=yes` (present) or `toilets:wheelchair=no` (absent); rest place - an element `amenity=bench` or `leisure=picnic_table` (present), and an element `highway=bus_stop`, `public_transport=platform` or `amenity=shelter` with `bench=yes` (present) or `bench=no` (absent); ramp - a `highway=steps` way or a node with an `entrance` tag, with `ramp:wheelchair=yes` or `ramp=yes` (present) or `ramp:wheelchair=no` or `ramp=no` (absent), `ramp:wheelchair` deciding when both are given; handrail at stairs - a `highway=steps` way with `handrail=yes` or any of `handrail:left`, `handrail:right` and `handrail:center` set to `yes` (present), or with `handrail=no` or every given side `no` (absent); lowered kerb - D-8. Every other value, `ramp=separate`, `ramp:wheelchair=limited` and `handrail=left` included, gives no fact (F-22). Agent decision at C:40, without asking: the PRD names the tags but not the elements, and `ramp:wheelchair` speaks of the wheelchair itself.

D-14. The thresholds - 6 percent, 0.9 m, 0.03 m - and the value lists - the poor and good surfaces, the two parts of the smoothness scale, the kerb values, the gate barriers, the stop tags of D-8, the classes of ways for motor traffic and the sidewalk keys - are constants of the third configuration layer in one module next to the code of the rule (F-10): the same in every environment, used in one place, not secret. A change of a value is a change of that module followed by a fresh import, which gives PRD FR-2 and AC-10. No environment entry is added. The names of the module and of the constants are decided with the backend architecture of `plans_finished/mvp/MVP_PLAN.md` Q-11, following `docs/standards/standard_naming.md`. Agent decision at C:40, without asking.

D-15. The date of a fact is the timestamp of the version of its OpenStreetMap element in the copy (F-13), an instant in UTC, converted to the calendar day in the Europe/Warsaw zone by `docs/standards/standard_time.md` (F-12): the way for a way state and for the ramp and handrail of steps, the node for a point fact and a kerb point, the element for an amenity. A way keeps the timestamp of its own last version, which changes when its tags or its list of nodes change, not when one of its nodes is moved. Agent decision at C:40, without asking: PRD FR-7 names the element the tags belong to.

D-16. The rule of D-6 and D-8 - D-15 is built in the import work package of `plans_finished/mvp/`, owned by the import person, as code that takes the tags of one element, and for D-6 the membership of a node in ways for motor traffic, and returns its facts without reading the database or the network. The segment combination of D-7 and the contradiction of M2 are built in the route work package that `plans_finished/routing_engine/` decides. Module and function names are decided in `plans_finished/mvp/MVP_PLAN.md` with Q-11, as `plans_finished/geocoding/GEOCODING_PLAN.md` D-2 did. Agent decision at C:40, without asking: it follows from the PRD section Out of scope.

D-17. The work packages add these tests under `docs/standards/standard_tests.md`, none touching the database or the network (F-11). The import package adds unit tests of the rule for AC-1, AC-4 - AC-8, AC-12 and AC-16 of the PRD, each threshold checked on both sides (6 and 6.1 percent, 0.9 and 0.89 m, 0.03 and 0.031 m), every number form of D-9 accepted and refused, the kerb points of D-8 with the conflict and the stop exclusion, AC-10 with the constant of the threshold replaced in the test, and AC-11 with an instant of 23:30 UTC on 2 October 2026. The route package adds unit tests of D-7 and of the segment states for AC-2, AC-3, AC-13 and AC-14, and the runs of AC-9. Agent decision at C:40, without asking: every domain rule gets a test of its positive side and of its refusal (F-11).

## Scope of changes

The texts to insert are given in fenced blocks and are inserted without the fence. Every file outside `plans_finished/osm_barrier_mapping/` is read again right before it is edited (Risks); when a quoted passage no longer matches the file, the step stops and the difference goes to the user.

### Step 1. `docs/product/specification.md`, version 3

1.1. Replace the state line `Document state: 2026-10-03, version 2 - target group, MVP scope and the rules of the MVP features (presets and amenities added in phase A of the PRD)` with the line below, YYYY-MM-DD being the day of the edit.

```text
Document state: YYYY-MM-DD, version 3 - the OpenStreetMap tag rules with their thresholds and the contradiction between OpenStreetMap and a user report, decided in `plans_finished/osm_barrier_mapping/`, and the fate of OpenStreetMap facts across fresh copies and the refresh of the copy, decided in `plans_finished/osm_data_source/`
```

1.2. In the section Why this document exists, after the sentence "Version 2 adds the rules of these features, decided in the shape interview of the initiative `plans_finished/mvp/`.", insert in the same paragraph:

```text
Version 3 adds which OpenStreetMap tags count as which barrier or amenity, with their thresholds, and when OpenStreetMap contradicts a user report, decided in `plans_finished/osm_barrier_mapping/`, and the fate of OpenStreetMap facts across fresh copies and the refresh of the copy, decided in `plans_finished/osm_data_source/`.
```

1.3. In M2, after the paragraph that starts "An unverified or disputed barrier from the profile, not contradicted by OpenStreetMap, is not avoided", insert the paragraph:

```text
OpenStreetMap contradicts a user report in two cases only: an opposite fact of the closed list at the same place - a lowered kerb against a reported high kerb, or a high kerb against a reported lowered kerb - or a tag value on the same stretch of way that the tag rules of M6 classify as not the reported barrier, for example `surface=asphalt` against a report of poor surface. The absence of a tag never contradicts a report; in particular a way not tagged as steps never contradicts a report of stairs.
```

1.4. In M4, after the bullet that starts "A fact from OpenStreetMap shows its source and the date of its last edit in OpenStreetMap.", insert the four bullets:

```text
- Whether a user report contradicts an OpenStreetMap fact follows the rule of M2. The date of the last OpenStreetMap edit of a fact is the calendar day of the last edit of the OpenStreetMap element whose tags give the fact.
- When a fresh copy of OpenStreetMap data (M6) no longer holds an OpenStreetMap fact and the sum of its confirmations is greater than the sum of its denials, the fact becomes a user fact: it keeps all its votes, confirmations and denials alike, shows the source user report with the date of its last confirmation, and from then on its status follows the rules of a user fact. Otherwise - no votes, only denials, or as many confirmations as denials by weight - it becomes outdated with the reason that it was removed in OpenStreetMap, disappears from the map and the routes, and its votes stay in its history.
- When a later copy holds a fact of the same type on the same OpenStreetMap element again, it is the same fact again: a converted user fact or an outdated OpenStreetMap fact becomes an OpenStreetMap fact once more, with the source OpenStreetMap, the date of its last OpenStreetMap edit and all its votes. The same element means the same OpenStreetMap identifier; this is a match by identity, never by distance.
- An OpenStreetMap fact that appears in a fresh copy where a user fact of the same type already lies is a separate fact, and the two are not merged (M3). Whether a fresh copy contradicts a converted user fact follows the rule of M2.
```

1.5. In M6, after its only paragraph, insert the first block below as a paragraph, then the heading `#### Reading OpenStreetMap tags`, then the second block below, and after it the part of the section Domain rules of `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PRD.md` from the line "Barriers:" to the end of that section, the line "The thresholds in short: ..." included, copied verbatim except that the reference " (FR-12)" at the end of the bullet on ways for motor traffic is removed.

```text
A copy of OpenStreetMap data is used as a whole or not at all: when a fresh copy cannot be fetched or completed, the app keeps the last complete copy unchanged, and a successful fresh copy replaces it for every OpenStreetMap fact. The date of a copy is the calendar day of the state of OpenStreetMap it reflects, not the day it was downloaded, and it is the date the app shows wherever it says how fresh its OpenStreetMap data is. In the prototype a copy is fetched before the demo and the team triggers a fresh copy by hand; nothing refreshes on a schedule.
```

```text
Every barrier and amenity of the closed list (M3) is present, absent or unknown on a stretch of way or at a point, by the tags of the OpenStreetMap element it belongs to. A tag value these rules do not list leaves the item unknown: it never makes a barrier absent and never makes an amenity present. Lengths are read in metres and the incline in percent, or in degrees converted to percent; a number in any other form is unknown. The thresholds and value lists are the same for every profile, because a preset only switches barrier types on or off (M1). Every fact these rules give carries the source OpenStreetMap and the date of the last OpenStreetMap edit of its element (M4).
```

1.6. In M7, replace the bullet "- grey, dashed - no data." with the first block below, and after the paragraph that starts "A segment without complete data is never green." insert the second block as a new paragraph.

```text
- grey, dashed - no data: no attribute relevant to the profile is known other than by the default of no stairs.
```

```text
The attribute behind each barrier is the one named in the tag rules of M6: the steps for stairs, the kerbs for a high kerb, the surface for poor surface, the incline for a steep incline and the width for a narrow passage. The kerbs are an attribute only of a segment where the walking way meets a carriageway, that is at a crossing. A way not tagged as steps counts as known to have no stairs; this default never contradicts a report of stairs (M2), and on its own it does not make a segment partial data. A way that OpenStreetMap marks as not accessible for wheelchairs (`wheelchair=no`) is never green, for any profile: a segment of it that would be green is partial data, and the list of M8 says that OpenStreetMap marks the way as not accessible for wheelchairs. The marking adds no barrier, so the route does not avoid the way because of it.
```

1.7. In M8, replace the sentence "For a segment with partial data or no data, the list names the missing attributes." with:

```text
For a segment with partial data or no data, the list names the missing attributes by the names of the tag rules of M6 - kerbs, surface, incline, width - and for a way marked `wheelchair=no` it says that OpenStreetMap marks the way as not accessible for wheelchairs.
```

1.8. In Open questions, replace "None at version 2." with "None at version 3.".

1.9. In Decision provenance, append as the last bullet:

```text
- Version 3: the rules of reading OpenStreetMap tags (M6, M7, M8) and of the contradiction between OpenStreetMap and a user report (M2, M4) were decided by the user in the shape interview, at the PRD gate and in phase B of `plans_finished/osm_barrier_mapping/`, and the rules of OpenStreetMap copies and of OpenStreetMap facts across fresh copies (M4, M6) in the shape interview, at the PRD gate and in phase B of `plans_finished/osm_data_source/`; those documents record the scenarios each rule was decided on. The tag values and thresholds of M6 were proposed by the agent from common OpenStreetMap tagging practice and the OpenStreetMap wiki and approved by the user on 2026-10-03 as the values the import runs on; the import person of the team confirms or changes them before the demo is recorded, and a change is a new version. The rules of OpenStreetMap facts across fresh copies were given by the user answering for the import person, whose ruling is still to be confirmed.
```

1.10. Show the user the diff of steps 1.1 - 1.9 and ask for approval of version 3. A requested change is applied and shown again. After the approval, append to the bullet of step 1.9 the sentence "The user approved this version on YYYY-MM-DD.", with the day of the approval.

### Step 2. `plans_finished/mvp/MVP_PLAN.md`

D-N below is D-4, or the next free number of the section Decisions if another initiative has taken D-4 by the time of the edit; every reference to D-N in this step uses the same number.

2.1. In Goal, replace "`docs/product/specification.md`, version 2," with "`docs/product/specification.md`, version 3,".

2.2. In Decisions, append as the last item:

```text
D-N. Mapping of OpenStreetMap tags to the closed list of barriers and amenities, settling the former Q-8. The tag rules, thresholds and value lists are those of `docs/product/specification.md` version 3, M6, with the segment rules of M7 and M8 and the contradiction of M2, applied as `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6 - D-17 decide. Constraints for the rest of this plan: the import applies the rule once per element, independently of the profile, and keeps for every barrier of a way one of the states present, absent, absent by default and unknown (D-6 there), so that the route can tell an explicit absence, which contradicts a report, from the default of no stairs, which does not; the thresholds and value lists are constants of the third configuration layer next to the code of the rule (D-14 there); the import and route work packages include the tests of D-17 there. Decided by the user on 2026-10-03 in `plans_finished/osm_barrier_mapping/`; the import person confirms or changes the thresholds before the demo is recorded.
```

2.3. In Open questions, remove the item that starts "- Q-8. Mapping of OpenStreetMap tags to the closed list of barriers and amenities, with thresholds". The other identifiers stay unchanged, because the shapes of the sibling initiatives refer to them.

2.4. In the item Q-10, replace "Depends on the rules of Q-8 and," with "Depends on the rules of D-N and,"; replace "the rules of Q-8 in `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md` and the question of Q-2" with "the rules of D-N in `docs/product/specification.md` version 3 and the question of Q-2"; and replace "It does not depend on the numeric thresholds of Q-8, which are configuration values approved later (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, question 2)," with "It does not depend on the numeric thresholds of D-N, which are constants of the third configuration layer (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-14),".

2.5. Replace the item that starts "- Q-10 inputs from `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, section Domain rules:" with:

```text
- Q-10 inputs from `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6, which the schema has to be able to hold: for every way of the pedestrian network, for each of stairs, poor surface, steep incline and narrow passage one of the states present, absent, absent by default and unknown, where absent by default exists only for stairs; the number of steps of stairs when OpenStreetMap gives it; the `wheelchair=no` marking of the way; for every node of such a way its point facts - stairs, a narrow passage, a kerb point that is high, lowered or unknown - and whether it also belongs to a way for motor traffic; for every amenity fact its element and a point; and for every fact the type and identifier of its OpenStreetMap element and the calendar day of its last OpenStreetMap edit. OpenStreetMap contradicts a user report only through an explicit absence or an opposite kerb point, never through absent by default or unknown (`docs/product/specification.md` version 3, M2).
```

2.6. In the item that starts "- Q-10 caveats:", replace "the rules above enter `docs/product/specification.md` only in version 3, which is not written yet, so until the user approves it they are decisions of the two shapes, not of the specification." with "the rules above are in `docs/product/specification.md` version 3, written by `plans_finished/osm_barrier_mapping/` and approved by the user.".

2.7. In Risks, replace "Q-10 depends on the rules of Q-8 and on" with "Q-10 depends on the rules of D-N and on".

The replacements of steps 2.4 and 2.7 touch only the passages about Q-8, so they apply whether or not the plan of `plans_finished/osm_data_source/` has already rewritten the passages about Q-2 around them (F-28).

2.8. In Supplementary files, append the item "- `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md`, the decision behind D-N."

### Step 3. `plans_finished/mvp/MVP_PRD.md`

3.1. In Scope, replace "The mandatory features M1-M11 of the specification, version 2," with "The mandatory features M1-M11 of the specification, version 3,".

3.2. In AC-10, replace "For the segment of shape scenario 9 the list says that the incline and the kerbs are unknown." with:

```text
For the segment of shape scenario 9, read as meeting a carriageway, the list for the preset "I use a wheelchair" says that the incline, the kerbs and the width are unknown (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PRD.md` AC-3).
```

3.3. In Domain rules, replace "The rules are those of the specification, version 2," with "The rules are those of the specification, version 3,".

3.4. In Domain rules, replace the bullet that starts "- Segment states: barrier - a prevailing barrier from the profile" with:

```text
- Segment states: barrier - a prevailing barrier from the profile, or an unverified or disputed one that OpenStreetMap does not contradict; no barrier - every attribute behind the barriers of the profile is known, none is a barrier, and OpenStreetMap does not mark the way `wheelchair=no`; partial data - the known attributes are not barriers, but some are missing or the way is marked `wheelchair=no`; no data - no attribute behind the barriers of the profile is known other than by the default of no stairs. The attributes, the default and the marking are those of the specification, version 3, M6 and M7.
```

### Step 4. `plans_finished/osm_data_source/OSM_DATA_SOURCE_PRD.md`

In Dependencies and impact on other modules, after the sentence "`plans_finished/osm_barrier_mapping/` gives the contradiction rule FR-11 applies, and its rules and these enter version 3 of `docs/product/specification.md` as one change." append in the same item:

```text
That change, these rules included, is written by `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` (D-2 there, and D-20 of `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, decided by the user on 2026-10-03).
```

### Step 5. `plans_finished/routing_engine/ROUTING_ENGINE_SHAPE.md`

In Current state, append as the last item:

```text
- `plans_finished/osm_barrier_mapping/` decided on 2026-10-03 (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-6, D-7, D-11) what the route reads from the import: for every way of the pedestrian network a state of stairs, poor surface, steep incline and narrow passage - present, absent, absent by default for stairs only, unknown - with the number of steps and the `wheelchair=no` marking, and point facts on the nodes of the way: stairs, a narrow passage and kerb points that are high, lowered or unknown. It also decided how a segment combines them, which segments meet a carriageway, and that only an explicit absence or an opposite kerb point contradicts a user report (`docs/product/specification.md` version 3, M2, M6, M7). Left to this initiative: which stretch of way a point report lies on, and within what distance of an opposite kerb point a kerb report counts as contradicted.
```

### Step 6. `plans_finished/api_contract/API_CONTRACT_SHAPE.md`

In Current state, append as the last item:

```text
- `plans_finished/osm_barrier_mapping/` decided on 2026-10-03 (`docs/product/specification.md` version 3, M6 - M8) that the route response names the missing attributes of a segment with partial data or no data as kerbs, surface, incline and width, says for a way marked `wheelchair=no` that OpenStreetMap marks it as not accessible for wheelchairs, and carries the number of steps of stairs when OpenStreetMap gives it, next to the source and the calendar date of the last OpenStreetMap edit of every OpenStreetMap fact.
```

## Rollout order

1. Step 1.1 - 1.9 in the specification, then step 1.10: the approval of version 3 by the user. Steps 2 - 6 wait for the approval, because they refer to version 3 as approved.
2. Steps 2 and 3 in the MVP plan and PRD.
3. Steps 4 - 6 in the sibling initiatives, in any order.
4. The checks of the Definition of Done.

Steps for a human:

- The user approves the text of version 3 of the specification (step 1.10).
- The import person confirms or changes the thresholds before the demo is recorded; a change is a new version of the specification and a change of the constants of D-14, outside this plan.
- The commit and the Merge Request of the changed files.

## Definition of Done

- `docs/product/specification.md` carries steps 1.1 - 1.10 and states everything AC-15 of the PRD lists.
- `plans_finished/mvp/MVP_PLAN.md` carries D-N of step 2.2, has no item Q-8 under Open questions, and carries the replacements of steps 2.1 and 2.4 - 2.8.
- `plans_finished/mvp/MVP_PRD.md` carries the replacements of step 3, and `plans_finished/mvp/MVP_SHAPE.md` is unchanged.
- The files of steps 4 - 6 carry their items, and nothing else in them is changed.
- `npx prettier --check` passes on every file changed by this plan and on the four files of `plans_finished/osm_barrier_mapping/`.
- `venv\Scripts\python.exe -m pytest tests/architecture -o addopts="" -q` reports no violation in a file changed by this plan; the four failures of F-27, all on the files of the impeccable skill, are outside this plan, and `tests/architecture/test_plan_document_contract.py` passes on this closed plan.
- The review of `plan-implement` finds no blocking issue.

## Risks

- Coverage: of the incline tags on the foot ways of Kraków 98 percent are `up` or `down` (F-15), and only 80 foot ways have a surface, an incline and a width together (F-16). The presets "I use a wheelchair" and "Walking is difficult for me" will see almost no green segment outside the sample data of the demo district, and the demo has to say why.
- `surface=paved` on 5 241 foot ways stays unknown without a `smoothness` (F-18, D-10), which adds partial data even for the stroller preset.
- A crossing with only one of its kerbs tagged lowered counts as without a high kerb (D-7), because the rule cannot know that a second kerb exists. A kerb on the crossing node stands for both sides by the wiki (F-25), which covers the common case.
- A walking way that shares a node with a way for motor traffic needs a kerb point there to be known (D-7), also where no kerb exists, for example where a living street meets a residential road. Such a segment is never green, which errs on the safe side of M10 but adds grey and partial segments.
- Shared files: `docs/product/specification.md`, `plans_finished/mvp/MVP_PLAN.md` and `plans_finished/mvp/MVP_PRD.md` are also changed by other initiatives on the same day - `plans_finished/demo_environment/` closes Q-7 with a decision in the MVP plan and changes FR-20 and AC-19 of the MVP PRD, and `plans_finished/osm_data_source/` closes Q-2 with a decision there (F-28). Each file is read again right before its edit, and the D-number of step 2 is taken at that moment.
- The thresholds are values approved by the user, still to be confirmed by the import person; the rules of OpenStreetMap facts across fresh copies were given by the user for the import person, whose ruling is also still to be confirmed. Either change means a version 4.
- The plan of `plans_finished/osm_data_source/` was written in another session at the same time as this one (F-28). Both plans change `plans_finished/mvp/MVP_PLAN.md`; the passages each of them quotes do not overlap, as that session checked, so they apply in either order. Each plan takes the next free D-number at the moment of its edit.
- The weight of a vote after its 30-day identifier is deleted is decided in `plans_finished/osm_data_source/` (D-21 there) and lives in its PRD and in the MVP plan, not in version 3 (D-2). Until a later version of the specification states it, a reader of the specification alone does not see that rule.
- The four failing architecture tests of F-27 hide new violations of the same tests elsewhere; the Definition of Done checks the files of this plan by path.
- The numbers of F-14 - F-22 come from a public Overpass instance on 2026-10-03; F-20 and F-21 use the bounding box of Kraków, which also takes in some ways just outside the city.

## Open questions

None. The four questions of phase B were answered by the user on 2026-10-03 (D-1 - D-4), and who writes version 3 was settled with the session of `plans_finished/osm_data_source/` on the same day (D-2, F-28).

## Supplementary files

- `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PRD.md`, the contract this plan implements, amended in phase B with FR-12, AC-16 and the new wording of FR-11 and AC-15.
- `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SHAPE.md`, the rules and scenarios behind the PRD.
- `plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_SEED.md`, the verbatim request.
- `plans_finished/osm_data_source/OSM_DATA_SOURCE_PRD.md`, the rules version 3 takes from the sibling initiative.
- `plans_finished/osm_data_source/OSM_DATA_SOURCE_PLAN.md`, whose D-20 and D-21 settle who writes version 3 and what it leaves out.
