# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Backend: Python 3.13 with FastAPI, on PostgreSQL with PostGIS (`plans/mvp/MVP_PLAN.md` D-1). The demo runs on a hosted service reachable at a public link (`plans/demo_environment/`).

Frontend: decided by the frontend person on 2026-10-03 in `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`. It is a single-page application in TypeScript with React, built by Vite into static files and kept in `frontend/` as one code unit. The map is drawn by MapLibre GL JS from one archive of vector tiles of Kraków in the PMTiles format, cut from the daily Protomaps build of OpenStreetMap data and served by the project together with the map fonts and sprites. Four rules of that initiative bind all interface work: the programming interface has two clients from the start, the web frontend and a HarmonyOS port that is a separate client, not an embedding of the web app; the web frontend is chosen for the browser; the browser talks only to the server of the project; and frontend code follows the workflow core standards plus `docs/standards/standard_frontend.md`, which is written when the plan of that initiative is carried out. All frontend code is written as work packages of `plans/mvp/`.

## Users

- People planning a walking route in Kraków who meet physical barriers on the way and on entry: wheelchair users, parents with baby strollers and people with walking difficulties.
- Contributors: any user, with or without an account, who reports a barrier, an amenity or an inaccessible area, or confirms or denies an existing one. They include people without any mobility limits.
- A moderator: a member of the team whose role is assigned by hand, who reviews flagged content and can hide it.

People who are blind or have low vision are outside the prototype as a target group, because their route needs depend on different data. The interface itself still has to work with a screen reader.

## Product Purpose

A community app that lets a person judge in advance whether a walking route in Kraków is passable for them. It combines OpenStreetMap data with reports and confirmations from people, and shows concrete barriers and amenities with their source, date and reliability status instead of a single accessible or not accessible label.

The product is built at HackYeah 2026 (3-4 October 2026). Success at the event means that by 11:00 on 4 October the main scenario of the specification works in a demo and meets the requirements of the challenge Kraków bez barier. The same prototype is the base of a submission to the Huawei challenge Imagine What's Next, if the team goes for it.

## Positioning

Two things form the core. The user confirmed them on 2026-10-03 and the specification carries them:

- Honest uncertainty. Every fact carries its source, the date it was obtained or last confirmed, and a reliability status. Missing information is shown as missing, and a route segment without complete data is never shown as free of barriers.
- The community keeps the data current. Anyone reports concrete barriers and amenities and confirms or denies existing facts, OpenStreetMap facts included, and these votes become a visible reliability status.

The app presents facts and leaves the judgement to the person: no scores, no stars and no verdict about a place.

## Operating Context

- The app is designed for a phone, because that is what people use on the way. On a desktop browser it must not break, but it is not tuned for it.
- The interface is in Polish and English, with the default taken from the browser settings and a switch in the app. Repository content stays in English (`CLAUDE.md`).
- Routes work in the whole of Kraków. The demo takes place in the district of the Tauron Arena, the venue of HackYeah, with sample reports and geozones marked as sample data.
- The Kraków jury expects a live demo: state the needs of the chosen group, plan a route, show the concrete barriers and amenities with their source, date and status, show a contradiction between OpenStreetMap and a user report, and show what happens when a source is unavailable.
- Whether and in what form a HarmonyOS client is built is an open entry in `docs/standards/decision_registry.md`. The MVP must not prevent a second client from using the same data and rules. If the port is built, it is a second client of the same programming interface, native or in React Native for OpenHarmony, not an application embedding the web app. The web frontend is chosen for the browser and keeps nothing the port would need outside that interface (`plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, Domain rules).
- Authority: `docs/product/specification.md`, version 6, is the source of truth for the product and prevails over this file. The steps of a person through every mandatory feature are in `docs/product/user_journeys.md`. The requirements and acceptance criteria of the MVP are in `plans/mvp/MVP_PRD.md`, the scenarios behind its rules in `plans/mvp/MVP_SHAPE.md`, and the constraints of both challenges in `docs/hackathon/challenge_requirements.md`. This file is the summary that interface work starts from.

## Capabilities and Constraints

The MVP is the mandatory features M1-M11 of the specification. In terms of what the interface has to carry:

- Preference profile. A list of barriers to avoid and amenities needed, filled in by one of three presets - "I use a wheelchair", "I walk with a baby stroller", "Walking is difficult for me" - and then editable item by item. It works without an account and is kept only on the device. The first opening shows it before anything else, and it can be skipped; a profile without any barrier is allowed.
- Map of facts. The app opens on a map of Kraków that shows the barriers, amenities and geozones of the profile, with a switch to every fact and a list as its text form. Facts are opened, voted on and reported there without planning a route.
- Route. A walking route from A to B within Kraków, starting from the current location, an address or a point on the map. It avoids the barriers and geozones that match the profile. For an unverified or disputed barrier the app proposes an alternative route and says why. When no route without barriers exists, the app says so plainly, shows the route with the fewest barriers and lists them. A point outside Kraków is refused with a plain message. A shown route is planned again when the profile changes and when a vote or a report of the person is saved.
- Route segment states. Four states: barrier, no barrier, partial data, no data. The specification names them red, green, partial data, and grey dashed. Color is never the only carrier: each state also has an icon or a line pattern, a legend explains them, and the states have to be told apart in grayscale. Only barriers from the profile appear on the map. The stretches between the chosen points and the pedestrian network, at both ends of every route, are always no data. With a profile without barriers no segment has a state: the route is drawn in a neutral style that is none of the four, and the app says that the segments are not assessed.
- List for the route. A text list in three groups - barriers from the profile, additional barriers outside the profile, amenities on the route - where each item has its type, place, source, date and status, and one plain note says when some stretches of the route have no data; the missing attributes are not named. The place is the street name from OpenStreetMap, when the way has one, and the distance from the start. The list is the text alternative for the map.
- Reports. A point on the map with a type from a closed list and an optional description; for stairs, an optional number of steps. Before saving, the app shows the existing facts of the same type nearby and asks whether it is the same one, then shows a summary that the user approves. A saved report is not edited by anyone.
- Confirmations and denials. Every fact, OpenStreetMap facts included, can be confirmed as still there or reported as gone. A person votes on the same fact again only after a day, and only the latest vote of a person counts. Every fact, an OpenStreetMap fact included, has one of four statuses: unverified, confirmed, disputed, outdated. An outdated fact stays on the map with its status, so that a person can confirm it again; only a fact outdated because it was removed in OpenStreetMap disappears. The app shows a person their own latest vote on a fact, remembered on the device, and keeps the vote controls inactive for a day after it.
- Geozones. An inaccessible area marked as a point with a radius from a list and a barrier type, created with a keyboard alone, approved in a summary and not edited afterwards. It can carry an optional description. Reporting has one entry, where the person first chooses a barrier, an amenity or an area.
- Accounts. A pseudonym and a password, without an email address. Reports and votes also work without an account. A pseudonym has 3 to 30 characters: letters, digits, the underscore and the hyphen. An account is deleted after one confirmation, without the password. The app says nothing about a contribution from an account counting more.
- Flagging and moderation. Anyone can flag a report, a geozone or a fact converted from OpenStreetMap; the moderator sees flagged content in a separate view and can hide it and restore it. A flag has no reason and takes one confirmation.
- Privacy information. A page stating which personal data the app keeps, for what purpose and for how long, and which it does not keep.

Terms the interface uses:

- Barriers: stairs, high kerb, poor surface, steep incline, narrow passage.
- Amenities: ramp, elevator, lowered kerb, accessible toilet, rest place, handrail at stairs.
- Reliability statuses of a fact: unverified, confirmed, disputed, outdated.
- Sources of a fact: OpenStreetMap or user report; city data once the optional feature O4 exists. The interface calls the first one map data, in the working Polish copy "dane mapy", and uses the name OpenStreetMap only in the attribution on the map and on the page about the data.

The specification gives these terms in English. Their Polish wording, with every other text of the interface in both languages, is proposed in `docs/product/interface_texts.md` and waits for the approval of the frontend person.

Constraints:

- The app never asks about a disability and never stores one. A preset only sets preferences.
- Missing or unverified information is never presented as a confirmation of accessibility.
- Nothing about the author of a report, a vote or a geozone is shown to other users - neither a pseudonym nor whether the author was logged in. The weights behind a status stay inside the system.
- A status never changes with time alone. The date of the last confirmation is visible and the person judges it.
- Dates are shown as a calendar day in the Europe/Warsaw zone, without the hour.
- When the routing service does not answer, the app says plainly that a route cannot be planned right now and shows no guessed route. When fresh OpenStreetMap data cannot be fetched, the app works on the last fetched copy and shows its date.
- The OpenStreetMap attribution is visible on the map.
- The browser talks only to the server of the project: map tiles, fonts, scripts and every other file are served by it, so no service outside the project sees the IP address of the person or the area they look at (`plans_finished/frontend_stack/FRONTEND_STACK_SHAPE.md`, Domain rules).
- Sample data is marked as sample data wherever it appears.
- The main scenario works on a phone screen 360 px wide, and switching the language does not lose the planned route.

Outside the MVP:

- The optional features O1-O8 of the specification, built only after M1-M11 work: moving the profile with a QR code, photos in reports, points and a city ranking, open city data, geozone corrections, place cards, live alerts on the route, voice.
- Out of scope altogether: turn-by-turn navigation, public transport routes, scores or stars for places, implemented rewards, routes that guarantee a rest place at a given distance, and a layout tuned for desktop.

Undecided:

- The product name.
- The Polish wording of the interface terms, proposed in `docs/product/interface_texts.md` and not approved yet.
- The contract of the programming interface (`plans/api_contract/`).
- The form of the HarmonyOS client, and the licence of the repository.
- Two ideas the user raised on 2026-10-03 that the specification does not contain: a venue card through which owners and event organizers describe their own place, also as the business model, and measuring slope and surface with the phone's sensors. The specification has only place cards, as the optional feature O6. Neither idea is designed until the specification includes it.

## Evidence on Hand

- `docs/product/specification.md`, version 6: the target group, the features and their rules, personal data and the out-of-scope list.
- `docs/product/user_journeys.md`: fourteen journeys through the mandatory features, with their branches, and the path of the demo for the Kraków jury.
- `docs/product/views.md`: the fourteen views of the web frontend - one map with modes, panels over it and pages - with their content, their states and what each needs from the programming interface.
- `docs/product/interface_texts.md`: the texts of the interface in Polish and English, proposed and not approved yet.
- `plans/mvp/MVP_PRD.md`: twenty functional requirements with their acceptance criteria.
- `plans/mvp/MVP_SHAPE.md`: twelve scenarios with concrete inputs and expected states, usable as realistic content for screens and for the demo.
- The organizers' briefs, summarized in `docs/hackathon/challenge_requirements.md`.

There is no product name, logo or brand asset. There is no product code, no imported OpenStreetMap data and no sample data for the demo district yet. There is no user research, no testimonials, no partners, no usage numbers and no endorsement from the City. Future work must not fabricate any of these.

## Product Principles

1. Unknown is a state of its own. What is not known is shown as unknown - never as accessible and never hidden.
2. Every fact shows where it comes from: its source, its date and its reliability status, right next to the fact.
3. Needs, not diagnoses. Results follow barrier and amenity preferences, and the product never asks who the person is.
4. The person judges, the app does not. It shows concrete facts and says plainly what it cannot do, without scores and without verdicts.
5. The map never stands alone. Everything shown on the map is also available as text.

## Accessibility & Inclusion

- WCAG 2.2 level AA is the development goal set by the Kraków brief.
- The main scenario - setting the profile, planning a route, reading the result, reporting a barrier and voting - works with a keyboard alone and with a screen reader, on a phone.
- Text and the styles of the route segments meet the WCAG 2.2 AA contrast ratios, and the four segment states can be told apart without color.
- Every piece of information on the map is also available as text, through the list for the route.
- A geozone can be created with a keyboard alone.
- The brief requires a recorded list of what already works and what still needs work.
- The interface is available in Polish and in English.
