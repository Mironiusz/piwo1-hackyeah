# Data sources

Document state: 2026-10-04

EnableMe as designed; what runs in the prototype is in `what_works.md`. Every fact shows its source, date and a status from weighted votes. Missing information is never shown as accessible, except public transport (O9). Sample data are marked.

## OpenStreetMap extract

- Origin: the Geofabrik extract of Małopolska, cut to Kraków.
- Terms of use: ODbL 1.0, attribution on every map view.
- Fetching and updating: daily at Geofabrik; one copy before the demo, refreshed by hand.
- Reliability: MD5 sum, state instant and boundary checked; facts show their last edit day.
- When unavailable: the last complete copy stays with its date.

## Address search

- Origin: public Nominatim, called only from our server.
- Terms of use: the Nominatim usage policy; ODbL results.
- Fetching and updating: on submit only, 1 request per 1.1 s, 24 h cache.
- Reliability: Kraków only; the person picks from full addresses.
- When unavailable: a plain message; picking on the map still works.

## Map tiles, fonts and sprites

- Origin: a PMTiles archive of the daily Protomaps build, with style, fonts and sprites.
- Terms of use: ODbL, attribution always visible.
- Fetching and updating: cut once, served by our server only.
- Reliability: a base map, never a source of facts.
- When unavailable: same host as the app, so only with the app.

## Public transport timetables of ZTP Kraków (optional O9)

- Origin: three static GTFS feeds of ZTP, each published on 2 October 2026.
- Terms of use: not verified.
- Fetching and updating: whole, before the demo, refreshed by hand; no real-time data.
- Reliability: no accessibility data counts as accessible; a stop or trip marked inaccessible is never used.
- When unavailable: a walking route with a plain note.

## Reports of people

- Origin: reports, geozones and votes, with or without an account.
- Terms of use: licence not decided.
- Fetching and updating: saved at once, never edited; corrected by votes or new reports.
- Reliability: statuses from weighted votes; moderators hide flagged content.
- When unavailable: stored by the service, so only with it.

## City data sources named in the brief

The MVP uses none of the Kraków open data portal, MSIP and dane.gov.pl. City data are optional O4; MSIP stops are planned in it, terms not verified.
