# Design brief: views of the MVP

Document state: 2026-10-03, mocks reviewed by the user and corrected after the review; the corrected mocks are in `.impeccable/briefs/views/`

Product truth is in `PRODUCT.md` and `docs/product/specification.md`, version 13. What every view shows and which states it has is in `docs/product/views.md`; this brief does not repeat it. The visual world is the one approved for the route result in `.impeccable/briefs/route-result.md`, and no new direction was chosen here.

## Job and audience

- Who arrives: a person on the way who judges a route, a contributor who reports or votes, and a moderator. Most of them hold a phone outdoors.
- Visitor mode: Operate. Every view serves one task, and the same parts look the same everywhere.

## Outcome and proof

- Every view of `docs/product/views.md` has a mock in one visual world, so two people can build the frontend without the result drifting apart.
- The proof is the system sheet: one set of tokens and shared parts that every mock is built from.

## Selected direction

- Visual authority: `.impeccable/briefs/route-result.md` - Barlow Semi Condensed and Barlow Condensed, navy and yellow, compact density, the route as a line diagram in the header of the route result.
- Structure: one map that stays on the screen, a panel over its lower part, a bottom bar with Map, Report and Needs, a menu in the header, and pages without the map for the needs, the account and the texts.

## Scope and boundaries

- Twenty-eight mocks on one canvas: the system sheet and five rows - the needs and the map of facts; route planning and the route result; the fact detail; reporting; the menu, the account and the pages.
- Fidelity: static mocks in HTML and CSS. The tokens are CSS variables in one stylesheet, and the markup is semantic, so the build can take both over. The map is a drawing, because a mock cannot read the tiles of the project.
- Sources: `.impeccable/briefs/views/` holds the mocks as corrected after the review - the stylesheet `app.css` with the tokens, one file for each mock, and `canvas.json`, the index with the title and the size of each mock. A mock opens in a browser straight from that folder; the script `support.js` it names belongs to the canvas and is not needed for that. The working copy the canvas is published from is `.impeccable/mocks/views-canvas/project/`, which git does not track.
- Not product code. Nothing under `frontend/` was written.

## Mocks by view

| View                | Mocks                                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------------------------- |
| System sheet        | `Main`                                                                                                        |
| V-1 Shell           | the header and the bottom bar of every mock                                                                   |
| V-2 Needs           | `Needs`                                                                                                       |
| V-3 Map of facts    | `MapFacts`                                                                                                    |
| V-4 Route planning  | `RoutePlanning`, `RouteUnavailable`                                                                           |
| V-5 Route result    | `RouteResult`, `RouteNeutral`, `RouteNoRoute`                                                                 |
| V-6 Fact detail     | `FactDetail`, `FactVoted`, `FactContradiction`                                                                |
| V-7 Reporting       | `ReportKind`, `ReportPoint`, `ReportDetails`, `ReportExisting`, `ReportSummary`, `ReportSaved`, `AreaDetails` |
| V-8 Address search  | `RouteSearch`, `RouteSearchNone`                                                                              |
| V-9 Legend          | the legend in `RouteResult`, `RouteNeutral` and `RouteNoRoute`                                                |
| V-10 Menu           | `Menu`                                                                                                        |
| V-11 Account        | `AccountLogin`, `AccountCreate`, `AccountIn`, `AccountDelete`                                                 |
| V-12 Privacy        | `Privacy`                                                                                                     |
| V-13 About the data | `AboutData`                                                                                                   |
| V-14 Moderation     | `Moderation`                                                                                                  |

Every name is a file `<name>.dc.html` in `.impeccable/briefs/views/`.

## States and ranges

- Drawn: the first opening of the needs; the map of facts with the facts of the profile; route planning with both points set; the address search with one result and with nothing found; the usual route result; the route result without barriers in the profile; no route without barriers; routing not answering; the fact detail before a vote, after a vote and for a report that contradicts OpenStreetMap; the five steps of a point report, the details of an area and the saved report; the menu for a moderator; logging in and creating an account with an error; the account when logged in and the confirmation of deleting it; the privacy information, the page about the data and moderation.
- Not drawn: loading; the map that cannot be drawn; the map of facts for a profile without any item; the search unavailable; a point outside Kraków; the refused location; the session that ended; the moderator view denied; the summary of an area. The user decided on 2026-10-03 that they get no mock. The build covers each of them from `docs/product/views.md`, with the message block of the system sheet.

## Interaction and layout

- The shell is the same in every mock: the header with the name of the product and the menu, the content, the bottom bar. During reporting the bar shows Report as the current place.
- A panel carries one thing at a time: the list of facts, the planning form, the route result, a fact, or one step of a report. A step names its number and has a way back and a way forward.
- The two votes are equal buttons. After a vote they are inactive, and the panel says why.
- A list row keeps the same fields in the same places everywhere: icon, type, distance where there is one, street, status, source and date, sample data mark.

## Constraints and open decisions

Drawn by the agent and confirmed by the user on 2026-10-03:

- The status unverified is drawn in ink, not in the red of a barrier. Since version 4 of the specification a fact from OpenStreetMap that nobody voted on is unverified, so red would mark most of the list as a problem.
- The route without assessed segments is a hollow navy line, which is none of the four states and reads as a route without a judgement.
- A point report has five steps and an area has four, because an area has no check for existing facts.
- The action that deletes an account is drawn in the red of a barrier; every other primary action is navy.

Changed by the user on 2026-10-03 and applied to the mocks:

- The list of the route has no block for the segments with partial data or no data. One plain note above the list says that some stretches of the route have no data and that barriers on them are not known; it names no missing attributes (`docs/product/specification.md`, M8).
- The texts do not use the name OpenStreetMap, which confuses a person who does not know it. The source is called map data, in the working Polish copy "dane mapy"; the name stands only in the attribution on the map and once on the page about the data (`docs/product/specification.md`, M10).

Still open:

- The header of the mocks shows the name of the product, EnableMe, decided by the team on 2026-10-04, after the mocks were reviewed. The mocks had a placeholder there until the name was written into them on the same day; the published canvas of the mocks was not changed.
- The texts. They are kept in `docs/product/interface_texts.md`; on 2026-10-04 the mocks were brought in line with the choices decided there, and the single texts stay working copy until the views are built.
- The rule for the labels of the route diagram when barriers are many or close together, as in the brief of the route result.
- Since the review the user took four decisions where the views met `docs/product/api_contract.md` and version 7 of the specification (`docs/product/views.md`, decisions 11 - 14). An outdated fact stays on the map of facts: the system sheet and the page about the data show its status and its muted marker, and no other mock shows an outdated fact. The own vote of a person is remembered on the device, as the mock of the fact detail after a vote shows it. The street name stays in the list rows of the mocks and in the sample data of the demo; whether the programming interface carries it is deferred. The rule of a pseudonym in the mock of creating an account stays.
- The optional feature O9, routes with public transport, has no mock.
