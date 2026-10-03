# Product specification

Document state: 2026-10-03, version 2 - target group, MVP scope and the rules of the MVP features (presets and amenities added in phase A of the PRD)

## Why this document exists

This is the source of truth for the product, named in `CLAUDE.md`, section What we are building: what the product does, for whom, and what is in the prototype built at HackYeah 2026. In case of a discrepancy with anything else in the repository, this document prevails. It has to satisfy the external constraints summarized in `docs/hackathon/challenge_requirements.md`; a conflict with them is raised with the user, never resolved silently.

Version 1 settled the target group and the scope of the MVP, split into mandatory and optional features. Version 2 adds the rules of these features, decided in the shape interview of the initiative `plans/mvp/`. This document does not settle the technology stack or any technical solution - those are chosen in phase B of `plan-prd`. Product behavior that this document does not describe is still undecided, and every question about it goes to the user.

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

The route avoids the barriers from the profile known from OpenStreetMap, the confirmed barriers from the profile and the geozones (M5) whose type is in the profile. Rest places are shown along the route and in the list from M8, but they do not change its course.

An unverified or disputed barrier from the profile, not contradicted by OpenStreetMap, is not avoided: its segment is red, and the app proposes an alternative route that avoids it and says why, naming the barrier and its status.

When every way to the destination crosses a barrier from the profile or a matching geozone, the app shows the route with the fewest such barriers, says plainly that no route without barriers exists, and lists where the barriers are, so that the user decides.

### M3. Point reports of barriers and amenities

A report is a point on the map with a type from a closed list and an optional description. The list is closed so that a report can be matched against the profile and against the route. A report describes a concrete fact, not a score - the Kraków brief asks for concrete barriers and amenities instead of an accessible / not accessible label.

The initial list:

- barriers: stairs, high kerb, poor surface, steep incline, narrow passage;
- amenities: ramp, elevator, lowered kerb, accessible toilet, rest place (for example a bench), handrail at stairs.

The number of steps can be given for stairs, because a few steps with a handrail may be acceptable for a person with walking difficulties and are a barrier for a wheelchair.

Before a report is saved, the app shows the existing facts of the same type within about 15 m, facts from OpenStreetMap included, and asks whether it is the same barrier. Yes turns the report into a confirmation of the existing fact; no creates a new report. Nothing is merged automatically. Then the app shows a summary that the user has to approve, to rule out a mistake. Once saved, a report is not edited by anyone, the author included - corrections go through M4 and new reports.

### M4. Confirmations and reliability statuses

Every barrier and amenity, facts from OpenStreetMap included, can be confirmed by users as still there or reported as gone.

- Statuses of a user fact: unverified, confirmed, disputed, outdated. A new report is unverified.
- Weights: a logged-in person counts 1 and a person without an account 0.5, the author of the report included.
- A user fact becomes confirmed when the sum of its confirmations reaches 2. It becomes outdated when the denials reach at least 2 and outweigh the confirmations. It is disputed when it has both confirmations and denials and neither rule applies.
- A fact from OpenStreetMap shows its source and the date of its last edit in OpenStreetMap. It prevails over a contradicting user report, or over denials, until they reach the sum of 2. Then the user fact replaces it in the view, or the OpenStreetMap fact becomes outdated. A confirmation of an OpenStreetMap fact updates its date of last confirmation.
- One person has one vote per fact: per account for logged-in users, per hashed identifier for others (M9).
- A status does not change with time alone. The date of the last confirmation is visible and the user judges it.

Contradicting facts are also the case of contradictory data the Kraków demo has to show.

### M5. Simple geozones

A user can mark an inaccessible area, for example a sidewalk closed for works or a stretch of cobblestones. A geozone is a point, chosen on the map or by searching an address, with a radius chosen from a list (for example 10, 25, 50 or 100 m), so that it can be created with a keyboard alone. It carries a barrier type from the same list as point reports and is matched against the profile like them. Before saving, the user approves a summary; after saving, it is not edited. Other users judge a geozone with the mechanism of M4. Routes avoid geozones whose type is in the profile (M2).

### M6. Open data at start

OpenStreetMap is the data source available from the first minute, so the map is not empty before users report anything. It provides the accessibility attributes of ways and places (wheelchair access, kerbs, incline, surface, smoothness, steps, elevators, toilets, benches) and the base map. Its licence (ODbL) and attribution are respected. When fresh data cannot be fetched, the app works on the last fetched copy and shows its date.

### M7. Route colors

A route segment has one of four states:

- red - a prevailing barrier from the profile,
- green - every attribute relevant to the profile is known and none of them is a barrier,
- partial data - the known attributes are not barriers, but some relevant ones are missing,
- grey, dashed - no data.

A segment without complete data is never green. Only barriers from the profile appear on the map and in the colors; barriers outside the profile are left out of the map so that they do not clutter it, and they stay on the list from M8. A user report that contradicts OpenStreetMap and has not reached the threshold of M4 appears on the map as an unverified report icon, while the color follows OpenStreetMap. Color is never the only carrier of the information: each state also has an icon or a line pattern, and the same information is in the list from M8.

### M8. Barrier list for the route

After a route is planned, the app shows a text list of the barriers on it, in two groups: those matching the profile, and "additional barriers" outside the profile, so the user can judge them on their own. A third group, amenities on the route, lists the amenities the profile needs that lie near the route; they also have icons on the map and do not change the course of the route. Each item has its type, place, source, date and reliability status. For a segment with partial data or no data, the list names the missing attributes. The list is also the text alternative for the map that WCAG requires.

### M9. Accounts and anonymous reports

A light account: a pseudonym and a password, without an email address and without any question about a disability. Reports, confirmations and denials can also be made without an account, with the lower weight of M4.

A vote without an account stores a one-way hash of the IP address combined with browser characteristics, never the raw values. The hash serves only to allow one vote per fact, and it is deleted after 30 days. The combination is used instead of the IP address alone, because many people share one public address.

Other users never see who made a report, a confirmation or a geozone - neither a pseudonym nor whether the author was logged in. The weights behind a status are known only to the system.

Deleting an account removes the account, the pseudonym and the points. Reports and votes stay, detached from the person, and keep their weight.

### M10. Requirements of the Kraków brief

- Every fact shows its source (OpenStreetMap, city data, user report), the date it was obtained or last confirmed and its reliability status.
- Dates are shown as the calendar day in the Europe/Warsaw zone, without the hour.
- Missing information is never presented as a confirmation of accessibility.
- The main scenario works with a keyboard and a screen reader, has sufficient contrast, and map information has a text form.
- The demo shows a contradiction between OpenStreetMap and a user report, and what the user sees when a source is unavailable: when the routing service does not answer, a plain message and no guessed route.
- Sample data used in the demo is clearly marked as sample data.

### M11. Flagging and moderation

Anyone can flag a report, a geozone or a photo. A moderator - a member of the team whose role is assigned by hand - sees the flagged content in a simple view and can hide it; hidden content disappears for everyone.

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

- Kept: the pseudonym and the password of an account; the hash of a vote without an account, for 30 days; photos (O2), without their metadata.
- Not kept: the preference profile (only on the device), the current location (only inside a route request), an email address, any information about a disability.
- Not shown to other users: anything about the author of a report, a confirmation or a geozone.

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

None at version 2. Product behavior not described here goes to the user.

## Decision provenance

All decisions were made by the user on 2026-10-03, in a conversation with the agent.

- Version 1: the user decided the split into mandatory and optional features, the target group, the scope of geozones (simple geozones mandatory, corrections optional), light accounts with anonymous reports, and points with the ranking as an optional feature. The descriptions of the features, the initial list of barriers and amenities, the grey style for segments without data, the order of the optional features and the out-of-scope list were proposed by the agent and accepted by the user without separate discussion.
- Version 2: every rule added in this version was decided by the user in the shape interview recorded in `plans/mvp/MVP_SHAPE.md`, which also records the scenarios each rule was decided on. The contents of the presets and the role of amenities in the profile were decided in phase A of the PRD of the same initiative.
