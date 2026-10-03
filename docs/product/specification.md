# Product specification

Document state: 2026-10-03, version 4 - vote statuses and moderation, OpenStreetMap facts, geozones on routes, address search, amenity distance, server-side requests and routing behavior, with account and session rules added by `plans/account_sessions/`
## Why this document exists

This is the source of truth for the product, named in `CLAUDE.md`, section What we are building: what the product does, for whom, and what is in the prototype built at HackYeah 2026. In case of a discrepancy with anything else in the repository, this document prevails. It has to satisfy the external constraints summarized in `docs/hackathon/challenge_requirements.md`; a conflict with them is raised with the user, never resolved silently.

Version 1 settled the target group and the scope of the MVP, split into mandatory and optional features. Version 2 adds the rules of these features, decided in the shape interview of the initiative `plans/mvp/`. Version 3 adds which OpenStreetMap tags count as which barrier or amenity, their thresholds, contradiction handling and the fate of OpenStreetMap facts across fresh copies, decided in `plans_finished/osm_barrier_mapping/` and `plans_finished/osm_data_source/`. Version 4 brings in the rules of votes, statuses, flags, hiding and geozone radii from `plans/fact_schema/`; vote weight after identifier deletion from `plans_finished/osm_data_source/`; address search from `plans_finished/geocoding/`; amenity distance from `plans/mvp/`; browser-to-project-server communication from `plans_finished/frontend_stack/`; OpenStreetMap fact statuses and geozones on routes from `plans_finished/consistency_check/`; and routing behavior from `plans/routing_engine/`. Account creation, rolling sessions and cross-mode vote deduplication were added through `plans/account_sessions/`. This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd`. Product behavior that this document does not describe is still undecided, and every question about it goes to the user.
## Target group

The prototype is narrowed to three groups that share one kind of needs - physical barriers on the way and on entry:

- wheelchair users,
- parents with baby strollers,
- people with walking difficulties.

The group is chosen through preferences about barriers and amenities, never through a disability. The app does not ask about a disability and does not store one, because barrier preferences are enough to match the results (the Kraków brief, and Article 9 of the GDPR for health data).

People who are blind or have low vision are outside the prototype: their needs depend on different data (tactile paving, acoustic signals), which is a separate scope.

## Area, device and language

- Routes work in the whole of Kraków on OpenStreetMap data. The demo, with its sample data, takes place in the district of the Tauron Arena, the venue of HackYeah.
- The app is designed for a phone, because that is what people use on the way. On a desktop browser it must not break, but it is not tuned for it.
- The interface is in Polish and English, with the default taken from the browser settings and a switch in the app.

## Main scenario

1. The user sets their needs as barrier and amenity preferences, or picks a preset that fills them in.
2. The user plans a walking route in Kraków from their current location, an address or a point on the map.
3. The app shows the route with its segments marked by what is known about them, and a text list of the barriers on it - the ones matching the user's preferences and, separately, the additional ones.
4. For every barrier and amenity the user sees its source, the date it was obtained or last confirmed, and its reliability status, and judges the route on their own.
5. The user reports a barrier they see on the way, or confirms that a reported one still exists or is gone.

## Mandatory features

The MVP is not finished until all of these work in the demo.

### M1. Preference profile

The profile is a list of barriers the user wants to avoid and amenities the user needs. Three presets fill it in: "I use a wheelchair", "I walk with a baby stroller", "Walking is difficult for me". A preset only sets the preferences and is not stored as information about the user.

What each preset sets:

| Item               | I use a wheelchair | I walk with a baby stroller | Walking is difficult for me |
| ------------------ | ------------------ | --------------------------- | --------------------------- |
| Stairs             | avoid              | avoid                       | avoid                       |
| High kerb          | avoid              | avoid                       | -                           |
| Poor surface       | avoid              | avoid                       | avoid                       |
| Steep incline      | avoid              | -                           | avoid                       |
| Narrow passage     | avoid              | avoid                       | -                           |
| Elevator           | need               | need                        | -                           |
| Ramp               | need               | need                        | -                           |
| Lowered kerb       | need               | need                        | -                           |
| Accessible toilet  | need               | -                           | -                           |
| Rest place         | -                  | -                           | need                        |
| Handrail at stairs | -                  | -                           | need                        |

A preset is only a starting point: the user can change every item, for example untick stairs when a few steps with a handrail are acceptable.

The profile works without logging in and is kept only on the device. It never enters the account, because a profile tied to an account practically reveals health information. A route request carries the preferences without linking them to the account.

### M2. Route matched to the profile

A walking route from A to B within Kraków. The start is the current location (after the browser asks for consent), an address or a point on the map. The current location travels only in the route request: it is not stored, not logged and not linked to the account.

Nothing of a route request leaves the project: the current location, the start, the destination and the preferences of the profile, and anything derived from them such as a list of places to avoid, are used only by software of the project running on its own infrastructure, and are never sent to a routing service outside the project.

A route leads only along ways that a pedestrian may use according to their OpenStreetMap tags. Ways forbidden to pedestrians, ways not built yet and private ways without a permission for pedestrians are not part of the pedestrian network; ways for motor traffic are, as the tag rules of M6 read their surface and width when they have no sidewalk.

The stretch between a chosen start or destination - a point on the map, an address or the current location - and the point where the route joins the pedestrian network is a segment of the route in the state no data (M7), drawn as a straight line, and the list of M8 names its missing attributes as for any other segment with no data. This holds for every length, also a few metres at the start.

The route avoids the barriers from the profile known from OpenStreetMap, the confirmed barriers from the profile and the geozones (M5) whose type is in the profile. A geozone is avoided when it is unverified, confirmed or disputed. A fact or a geozone that is outdated (M4) or hidden by a moderator (M11) does not change the route. Rest places are shown along the route and in the list from M8, but they do not change its course.

An unverified or disputed barrier from the profile, not contradicted by OpenStreetMap, is not avoided: its segment is red, and the app proposes an alternative route that avoids it and says why, naming the barrier and its status.

OpenStreetMap contradicts a user report in two cases only: an opposite fact of the closed list at the same place - a lowered kerb against a reported high kerb, or a high kerb against a reported lowered kerb - or a tag value on the same stretch of way that the tag rules of M6 classify as not the reported barrier, for example `surface=asphalt` against a report of poor surface. The absence of a tag never contradicts a report; in particular a way not tagged as steps never contradicts a report of stairs.

When every way to the destination crosses a barrier from the profile or a matching geozone, the app shows the route with the fewest such barriers, says plainly that no route without barriers exists, and lists where the barriers are, so that the user decides.

#### Address search

An address or the name of a place, for example "Tauron Arena" or "Rynek Główny", can give the start and the destination of a route and the point of a geozone (M5).

- The search runs only when the user submits the text, with the Enter key or a search button; nothing is suggested while the user types.
- The search returns only places within Kraków.
- The result is always a list the user picks from, also when it has a single item. Each item shows the full address, so places with the same name can be told apart. The app never takes a match on its own: the start, the destination or the point of a geozone is set only when the user picks an item.
- The search field, the submission, the list and the picking work with a keyboard alone and with a screen reader, and the screen reader announces how many results there are.
- When nothing is found in Kraków, the user gets a plain message saying so. When the search cannot be answered right now, the user gets a different plain message saying that the search is unavailable. In both cases no point is guessed, and choosing a point on the map stays available.

### M3. Point reports of barriers and amenities

A report is a point on the map with a type from a closed list and an optional description. The list is closed so that a report can be matched against the profile and against the route. A report describes a concrete fact, not a score - the Kraków brief asks for concrete barriers and amenities instead of an accessible / not accessible label.

The initial list:

- barriers: stairs, high kerb, poor surface, steep incline, narrow passage;
- amenities: ramp, elevator, lowered kerb, accessible toilet, rest place (for example a bench), handrail at stairs.

The number of steps can be given for stairs, because a few steps with a handrail may be acceptable for a person with walking difficulties and are a barrier for a wheelchair.

Before a report is saved, the app shows the existing facts of the same type within about 15 m, facts from OpenStreetMap included, and asks whether it is the same barrier. Yes turns the report into a confirmation of the existing fact; no creates a new report. Nothing is merged automatically. Then the app shows a summary that the user has to approve, to rule out a mistake. Once saved, a report is not edited by anyone, the author included - corrections go through M4 and new reports.

### M4. Confirmations and reliability statuses

Every barrier and amenity, facts from OpenStreetMap included, can be confirmed by users as still there or reported as gone.

- Statuses of every fact, facts from OpenStreetMap included: unverified, confirmed, disputed, outdated. A new report is unverified, and so is a fact from OpenStreetMap that nobody has voted on.
- The facts from OpenStreetMap are the barriers and amenities the tag rules of M6 make present. An item those rules make absent or unknown is not a fact and gets no votes.
- Weights: a logged-in person counts 1 and a person without an account 0.5, the author of the report included. A report carries the vote of its author as a confirmation.
- A person is an account, or for a vote without an account its hashed identifier (M9). A person votes on the same fact again only once a day has passed since their previous vote on it; an earlier vote is refused. Of the votes of one person on a fact only the latest counts, so a person can change their mind or refresh a confirmation, but never adds weight by voting again. A vote cannot be withdrawn without casting another one.
- The status of a fact is derived from the latest votes of the five persons who voted on it most recently, in this order: outdated when the denials reach at least 2 and outweigh the confirmations; otherwise disputed when there are both confirmations and denials; otherwise confirmed when the confirmations reach 2; otherwise unverified. A single denial therefore turns a confirmed fact into disputed, until it falls out of the five latest persons or the denials make the fact outdated. Older votes stay in the history of the fact and only stop counting.
- A vote keeps its weight for as long as the fact exists, also after the identifier of a vote without an account is deleted (M9) or the account that cast it is deleted. From then on it belongs to no person and counts as the vote of a person of its own.
- A fact from OpenStreetMap shows its source and the date of its last edit in OpenStreetMap. Whatever its status, it counts on the map and the route until it is outdated, and it becomes outdated by the same rule as any other fact. It prevails over a contradicting user report until the confirmations of that report reach the sum of 2; then the user fact replaces it in the view. A confirmation of an OpenStreetMap fact updates its date of last confirmation.
- Whether a user report contradicts an OpenStreetMap fact follows the rule of M2. The date of the last OpenStreetMap edit of a fact is the calendar day of the last edit of the OpenStreetMap element whose tags give the fact.
- When a fresh copy of OpenStreetMap data (M6) no longer holds an OpenStreetMap fact and the sum of its confirmations is greater than the sum of its denials, both counted over the same latest votes of five persons as the status, the fact becomes a user fact: it keeps all its votes, confirmations and denials alike, shows the source user report with the date of its last confirmation, and from then on its status follows the rules of a user fact. Otherwise - no votes, only denials, or as many confirmations as denials by weight - it becomes outdated with the reason that it was removed in OpenStreetMap, disappears from the map and the routes, and its votes stay in its history.
- When a later copy holds a fact of the same type on the same OpenStreetMap element again, it is the same fact again: a converted user fact or an outdated OpenStreetMap fact becomes an OpenStreetMap fact once more, with the source OpenStreetMap, the date of its last OpenStreetMap edit and all its votes. The same element means the same OpenStreetMap identifier; this is a match by identity, never by distance.
- An OpenStreetMap fact that appears in a fresh copy where a user fact of the same type already lies is a separate fact, and the two are not merged (M3). Whether a fresh copy contradicts a converted user fact follows the rule of M2.
- Every vote has the same 30-day hash of the IP address and browser characteristics, including account and anonymous votes. While the hash exists, a second vote with that hash on the same fact is rejected regardless of authentication state; per-account uniqueness also applies. After the hash expires, a later anonymous vote with the same hash may be accepted (M9).- A status does not change with time alone. The date of the last confirmation is visible and the user judges it.

Contradicting facts are also the case of contradictory data the Kraków demo has to show.

### M5. Simple geozones

A user can mark an inaccessible area, for example a sidewalk closed for works or a stretch of cobblestones. A geozone is a point, chosen on the map or by searching an address (M2, Address search), with a radius chosen from the list 10, 25, 50 and 100 m, so that it can be created with a keyboard alone. It carries a barrier type from the same list as point reports and is matched against the profile like them. Before saving, the user approves a summary; after saving, it is not edited. Other users judge a geozone with the mechanism of M4. Routes avoid geozones whose type is in the profile, unless they are outdated or hidden (M2).

### M6. Open data at start

OpenStreetMap is the data source available from the first minute, so the map is not empty before users report anything. It provides the accessibility attributes of ways and places (wheelchair access, kerbs, incline, surface, smoothness, steps, elevators, toilets, benches) and the base map. Its licence (ODbL) and attribution are respected. When fresh data cannot be fetched, the app works on the last fetched copy and shows its date.

A copy of OpenStreetMap data is used as a whole or not at all: when a fresh copy cannot be fetched or completed, the app keeps the last complete copy unchanged, and a successful fresh copy replaces it for every OpenStreetMap fact. The date of a copy is the calendar day of the state of OpenStreetMap it reflects, not the day it was downloaded, and it is the date the app shows wherever it says how fresh its OpenStreetMap data is. In the prototype a copy is fetched before the demo and the team triggers a fresh copy by hand; nothing refreshes on a schedule.

#### Reading OpenStreetMap tags

Every barrier and amenity of the closed list (M3) is present, absent or unknown on a stretch of way or at a point, by the tags of the OpenStreetMap element it belongs to. A tag value these rules do not list leaves the item unknown: it never makes a barrier absent and never makes an amenity present. Lengths are read in metres and the incline in percent, or in degrees converted to percent; a number in any other form is unknown. The thresholds and value lists are the same for every profile, because a preset only switches barrier types on or off (M1). Every fact these rules give carries the source OpenStreetMap and the date of the last OpenStreetMap edit of its element (M4).

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
- Ways for motor traffic are those with `highway` of `trunk`, `primary`, `secondary`, `tertiary`, their `_link` ways, `unclassified`, `residential` and `service`. On them `surface`, `smoothness` and `width` count only when the way has no sidewalk on either side (`sidewalk=no`, `sidewalk=none` or `sidewalk:both=no`). With a sidewalk tagged on the way (`sidewalk` or `sidewalk:both` of `both`, `left`, `right` or `yes`) they are read from `sidewalk:surface`, `sidewalk:both:surface`, `sidewalk:smoothness`, `sidewalk:both:smoothness`, `sidewalk:width` and `sidewalk:both:width`. In every other case, `sidewalk=separate` and a missing sidewalk tag included, they are unknown. `incline` counts on every way.

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

### M7. Route colors

A route segment has one of four states:

- red - a prevailing barrier from the profile,
- green - every attribute relevant to the profile is known and none of them is a barrier,
- partial data - the known attributes are not barriers, but some relevant ones are missing,
- grey, dashed - no data: no attribute relevant to the profile is known other than by the default of no stairs.

A segment without complete data is never green. Only barriers from the profile appear on the map and in the colors; barriers outside the profile are left out of the map so that they do not clutter it, and they stay on the list from M8. A user report that contradicts OpenStreetMap and has not reached the threshold of M4 appears on the map as an unverified report icon, while the color follows OpenStreetMap. Color is never the only carrier of the information: each state also has an icon or a line pattern, and the same information is in the list from M8.

The attribute behind each barrier is the one named in the tag rules of M6: the steps for stairs, the kerbs for a high kerb, the surface for poor surface, the incline for a steep incline and the width for a narrow passage. The kerbs are an attribute only of a segment where the walking way meets a carriageway, that is at a crossing. A way not tagged as steps counts as known to have no stairs; this default never contradicts a report of stairs (M2), and on its own it does not make a segment partial data. A way that OpenStreetMap marks as not accessible for wheelchairs (`wheelchair=no`) is never green, for any profile: a segment of it that would be green is partial data, and the list of M8 says that OpenStreetMap marks the way as not accessible for wheelchairs. The marking adds no barrier, so the route does not avoid the way because of it.

### M8. Barrier list for the route

After a route is planned, the app shows a text list of the barriers on it, in two groups: those matching the profile, and "additional barriers" outside the profile, so the user can judge them on their own. A third group, amenities on the route, lists the amenities the profile needs that lie within 50 m of the route; they also have icons on the map and do not change the course of the route. Each item has its type, place, source, date and reliability status. For a segment with partial data or no data, the list names the missing attributes by the names of the tag rules of M6 - kerbs, surface, incline, width - and for a way marked `wheelchair=no` it says that OpenStreetMap marks the way as not accessible for wheelchairs. The list is also the text alternative for the map that WCAG requires.

### M9. Accounts and anonymous reports

A light account: a pseudonym and a password, without an email address and without any question about a disability. Pseudonyms are unique without regard to letter case. Passwords have a minimum length of 5 characters, accept printable ASCII characters, spaces and Unicode, allow a maximum length of at least 64 characters, and have no character-composition or periodic-change rules. Common or breached passwords are not rejected. There is no password recovery; a forgotten password can make the account permanently inaccessible. These password rules are based on [NIST SP 800-63B-4](https://pages.nist.gov/800-63-4/sp800-63b.html), except for the user-chosen 5-character minimum and omission of the common or breached password blocklist.

After login, a person remains logged in until 24 hours after their last activity. Every request in the active session, including a read-only request, renews this period. The session remains active when the browser is closed and reopened.

Reports, confirmations and denials can also be made without an account, with the lower weight of M4.

Every vote, including one made through an account, stores a one-way hash of the IP address combined with browser characteristics, never the raw values. While the hash exists, it rejects a second vote on the same fact across account and anonymous contributions. It is deleted after 30 days. After it expires, a later anonymous vote with the same hash may be accepted; per-account uniqueness still applies. Different hashes are treated as different identifiers, so this does not deduplicate one person across different devices or networks. Matching hashes are deduplicated even when they belong to different people who share a browser and network. The combination is used instead of the IP address alone, because many people share one public address.
Other users never see who made a report, a confirmation or a geozone - neither a pseudonym nor whether the author was logged in. The weights behind a status are known only to the system.

Deleting an account removes the account, the pseudonym and the points. Reports and votes stay, detached from the person, and keep their weight, each vote counting as the vote of a person of its own (M4).

### M10. Requirements of the Kraków brief

- Every fact shows its source (OpenStreetMap, city data, user report), the date it was obtained or last confirmed and its reliability status.
- Dates are shown as the calendar day in the Europe/Warsaw zone, without the hour.
- Missing information is never presented as a confirmation of accessibility.
- The main scenario works with a keyboard and a screen reader, has sufficient contrast, and map information has a text form.
- The demo shows a contradiction between OpenStreetMap and a user report, and what the user sees when a source is unavailable: when the routing service does not answer, a plain message and no guessed route.
- Sample data used in the demo is clearly marked as sample data.

### M11. Flagging and moderation

Anyone can flag a report, a geozone, a fact converted from OpenStreetMap, which shows as a user report (M4), or a photo; a fact from OpenStreetMap cannot be flagged. A flag keeps nothing about who flagged. A moderator - a member of the team whose role is assigned by hand - sees the flagged content in a simple view, without anything about its author, and can hide it and restore it. Hidden content disappears for everyone: it is not on the map or the list, does not change the route or a segment state, takes no part in the check for existing facts of M3 and cannot be voted on. Restored, it counts again with the votes it still has. Removing the moderator role revokes access on the account's next request, even if its session remains active.
## Optional features

Built in this order, only after all mandatory features work.

### O1. Moving the profile with a QR code

The profile can be moved to another device with a QR code. The code carries the preferences themselves, not a link to a copy on a server, because the profile is kept only on the device.

### O2. Photos in reports

A report, a confirmation or a denial can carry a photo, and such a vote weighs 0.5 more. Photos are public next to their report. When uploading, the user is told to photograph the barrier, not people. The metadata of the file (location, device) is removed before publishing, and a photo can be flagged (M11).

### O3. Good Samaritan points and a city ranking

Points for reports and confirmations, and a public ranking of pseudonyms with their points for Kraków, without any list of their reports. Points are limited so they cannot be farmed, for example one confirmation per person per object. Rewards - such as a free public transport ticket - are presented in the business model only and are not implemented.

### O4. Open city data

Datasets from the open data portal of the City of Kraków or from MSIP, once it is checked which useful datasets exist and on what terms they can be used.

### O5. Geozone corrections

Suggesting a change to the shape or the type of a geozone, with a way to accept or reject the suggestion.

### O6. Place cards

A card of a place, for example a café or a museum, with the accessibility of its entrance, toilet and elevator.

### O7. Live alerts on the route

A notification when the user approaches a barrier on the planned route, which needs the user's location while walking.

### O8. Voice

Voice output or voice reporting, for example reporting a barrier without using the hands. For the Kraków challenge screen reader support matters more than own speech synthesis.

## Personal data

- Kept: the pseudonym and the password of an account; the hash of every vote, including account votes, for 30 days; photos (O2), without their metadata.
- Not kept: the preference profile (only on the device), the current location (only inside a route request), an email address, any information about a disability.
- Not shown to other users: anything about the author of a report, a confirmation or a geozone.
- Not revealed by the browser to anyone outside the project: the browser talks only to the server of the project, which serves the map tiles, the fonts, the scripts and every other file, so no service outside the project learns the IP address of the person or the area they look at.
- Not sent by the project to anyone outside it: anything of a route request - the current location, the start, the destination and the preferences of the profile (M2). The text of an address search is a separate request: the project hands it to an address search service outside the project from its own server, without anything that identifies the person (M2, Address search).

The privacy information of the app states each kept item with its purpose and retention.

## Out of scope

- Turn-by-turn navigation and public transport routes.
- Needs specific to people who are blind or have low vision.
- Scores, stars or a single accessible / not accessible label for places.
- Implementing rewards for points.
- Routes that guarantee a rest place at a given distance.
- Sending user reports back to OpenStreetMap - a development idea for the presentation.
- A layout tuned for desktop browsers.
- Statuses that change with time alone.

## Relation to the HarmonyOS port

Whether the project is submitted to the Huawei challenge, and in what form, is an open entry in `docs/standards/decision_registry.md`. Some optional features would use device capabilities if the port happens: the QR transfer the code scanner (O1), photos the camera (O2), live alerts the location services (O7), voice the speech services of the system (O8).

## Open questions

None at version 4. Product behavior not described here goes to the user.

## Decision provenance

All decisions were made by the user on 2026-10-03, in a conversation with the agent.

- Version 1: the user decided the split into mandatory and optional features, the target group, the scope of geozones (simple geozones mandatory, corrections optional), light accounts with anonymous reports, and points with the ranking as an optional feature. The descriptions of the features, the initial list of barriers and amenities, the grey style for segments without data, the order of the optional features and the out-of-scope list were proposed by the agent and accepted by the user without separate discussion.
- Version 2: every rule added in this version was decided by the user in the shape interview recorded in `plans/mvp/MVP_SHAPE.md`, which also records the scenarios each rule was decided on. The contents of the presets and the role of amenities in the profile were decided in phase A of the PRD of the same initiative.
- Version 3: the rules of reading OpenStreetMap tags (M6, M7, M8), contradiction handling between OpenStreetMap and user reports (M2, M4), and OpenStreetMap copy behavior (M4, M6) were decided by the user in `plans_finished/osm_barrier_mapping/` and `plans_finished/osm_data_source/`; those documents record the scenarios each rule was decided on. The tag values and thresholds of M6 were proposed by the agent from common OpenStreetMap tagging practice and the OpenStreetMap wiki and approved by the user on 2026-10-03 as the values the import runs on; the import person of the team confirms or changes them before the demo is recorded, and a change is a new version. The rules of OpenStreetMap facts across fresh copies were given by the user answering for the import person, whose ruling is still to be confirmed. The user approved this version on 2026-10-03.
- Version 4: the user decided the rules of votes, statuses, flags, hiding, geozone radii and pseudonyms (M4, M5, M9, M11) in the shape interview and at the PRD gate of `plans/fact_schema/`; the weight a vote keeps after its identifier is deleted (M4, M9) in phase B of `plans_finished/osm_data_source/` (D-21); and the statuses of OpenStreetMap facts, geozones on routes and cross-mode voting in `plans_finished/consistency_check/` (U-1 - U-4). The address search was decided in `plans_finished/geocoding/`, the 50 m amenity distance at the PRD gate of `plans/mvp/`, and browser-to-project-server communication in `plans_finished/frontend_stack/`. The user also decided account creation rules, rolling 24-hour sessions, immediate moderator-role revocation and use of the same 30-day hash for account and anonymous vote deduplication in `plans/account_sessions/`; the shared hash applies to both logged-in and anonymous votes. The routing request, pedestrian network and connection to that network were decided in `plans/routing_engine/`. The user approved this version on 2026-10-03.