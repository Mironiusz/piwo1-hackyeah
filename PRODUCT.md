# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React + Vite + TypeScript for the web interface, chosen by the user on 2026-10-03. The interface is mobile-first, and the same web app is meant to run in the browser and inside the HarmonyOS application shell. The map library, the backend and the hosting are not decided yet - the team's entry on the technology stack in `docs/standards/decision_registry.md` is still open.

## Users

- People who move on wheels or walk with difficulty: wheelchair users and people with walking difficulties. They check whether a place or a route in Kraków fits their needs.
- Contributors without mobility limits: residents who simply want to report a barrier they noticed. Their reports and confirmations are how the data stays fresh.
- Venue owners and event organizers, who describe the accessibility of their own place.

## Product Purpose

A community app about the accessibility of places and routes in Kraków. It combines open data (OpenStreetMap, open city data) with reports from people, including photos, and shows concrete barriers and amenities instead of a single accessible or not accessible label, so that a person can judge on their own whether a place or a route fits their needs.

The product is built at HackYeah 2026 (3-4 October 2026) for two partner challenges at once: Kraków bez barier (City of Kraków) and Imagine What's Next (Huawei, HarmonyOS). Success at the event means a working demo of the main scenario - find a place or a route and see the accessibility information that matters - and the same product running as a HarmonyOS package.

## Positioning

Three things form the core, confirmed by the user on 2026-10-03:

- Honest uncertainty. Every accessibility fact carries its source, the date it was obtained or last confirmed, and a reliability status. Missing information is shown as missing, never as accessible.
- The community keeps the data fresh. Anyone can report a barrier with a photo or confirm an existing fact with one tap, and information that is not confirmed ages.
- The venue card. Owners and organizers describe the accessibility of their own place. It is also the business model.

Measuring slope and surface roughness with the phone's sensors is a feature of the product, not its core.

## Operating Context

- The interface is used on a phone first. The Kraków brief names residents and tourists as the audience.
- The interface is offered in Polish and in English. Repository content stays in English (`CLAUDE.md`), the Kraków submission is written in Polish.
- The Kraków jury expects a live demo: state the needs of the chosen group, check at least one place or route, show the concrete barriers and amenities, show where each piece of information comes from and when it was confirmed, and show at least one case where data is contradictory, incomplete or its source is unavailable.
- The Huawei jury expects the product running as a `.hap` package on an emulator or a device, with documentation in English.
- Data sources named in the Kraków brief: OpenStreetMap, the open data portal of the City of Kraków, the municipal spatial information system MSIP and the national open data portal.
- The team's specification will live in `docs/product/specification.md` and prevails over this file in case of a conflict. The requirements of both challenges are summarized in `docs/hackathon/challenge_requirements.md`.

## Capabilities and Constraints

Confirmed capabilities:

- Find a place or a route and see the barriers and amenities that matter: stairs, thresholds, ramps, elevators, entrance width, surface, toilet, places to rest.
- Show the source, the date and the reliability status next to every fact, with user reports clearly distinguished from confirmed data.
- Report a barrier with a photo, confirm an existing fact, and correct wrong or outdated information.
- Match routes to needs built from barrier and amenity preferences.
- Let venue owners and event organizers publish an accessibility card of their place.
- Measure slope and surface roughness with the phone's sensors, as an additional feature.

Constraints from the challenge briefs:

- The app never asks a person to disclose a disability. Preferences about barriers and amenities are enough to match results.
- Missing or unverified information is never presented as a confirmation of accessibility.
- No reliance on internal systems of the City Hall or municipal units. Only publicly available data, used on its providers' terms, with attribution where the licence requires it.
- Sample data shown in a demo is clearly marked as sample data.

Undecided:

- The product name.
- The detailed feature list and the scope of the prototype - the specification is still being written.
- The names of the reliability statuses and the rule by which information ages.
- The form of the HarmonyOS client, the backend, the hosting and the map library.
- The licence of the repository and the intellectual property between the two challenges.

## Evidence on Hand

- The organizers' briefs, summarized in `docs/hackathon/challenge_requirements.md`.
- The list of data sources named in the Kraków brief. Nothing has been imported yet.

There is no product name, logo or brand asset. There is no accessibility data collected or verified by the team, no user research, no testimonials, no partner venues, no usage numbers and no endorsement from the City. Future work must not fabricate any of these.

## Product Principles

1. Unknown is a state of its own. What we do not know is shown as unknown, never as accessible and never hidden.
2. Every fact shows where it comes from: its source, its date and how far it can be trusted, right next to the fact.
3. Needs, not diagnoses. Results are matched to barrier and amenity preferences, and the product never asks who the person is.
4. Reporting has to be effortless for anyone. A report or a confirmation takes seconds, because people without mobility limits keep the data alive.
5. The map never stands alone. Everything shown on the map is also available as text.

## Accessibility & Inclusion

- WCAG 2.2 level AA is the development goal set by the Kraków brief.
- Already in the prototype: keyboard support, screen reader support, readable content, sufficient contrast, and a text alternative for information shown only on the map.
- The evaluation includes a list of what already works and what still needs work.
- The interface is available in Polish and in English.
