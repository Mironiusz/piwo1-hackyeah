# Design brief: views of the MVP

Document state: 2026-10-03, mocks published for approval, waiting for the user's confirmation

Product truth is in `PRODUCT.md` and `docs/product/specification.md`, version 6. What every view shows and which states it has is in `docs/product/views.md`; this brief does not repeat it. The visual world is the one approved for the route result in `.impeccable/briefs/route-result.md`, and no new direction was chosen here.

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

- Twenty-eight mocks on one canvas, in five rows: the system sheet; the needs and the map of facts; route planning and the route result; the fact detail; reporting; the menu, the account and the pages.
- Fidelity: static mocks in HTML and CSS. The tokens are CSS variables in one stylesheet, and the markup is semantic, so the build can take both over. The map is a drawing, because a mock cannot read the tiles of the project.
- Sources: `.impeccable/mocks/views-canvas/project/`, which git does not track. The approved mocks are copied into `.impeccable/briefs/views/` when the user approves them.
- Not product code. Nothing under `frontend/` was written.

## States and ranges

- Drawn: the first opening of the needs; the map of facts with the facts of the profile; route planning with both points set; the address search with one result and with nothing found; the usual route result; the route result without barriers in the profile; no route without barriers; routing not answering; the fact detail before a vote, after a vote and for a report that contradicts OpenStreetMap; the five steps of a point report, the details of an area and the saved report; the menu for a moderator; logging in and creating an account with an error; the account when logged in and the confirmation of deleting it; the privacy information, the page about the data and moderation.
- Not drawn: loading; the map that cannot be drawn; the map of facts for a profile without any item; the search unavailable; a point outside Kraków; the refused location; the session that ended; the moderator view denied; the summary of an area. Their content is in `docs/product/views.md`, and they use the message block of the system sheet.

## Interaction and layout

- The shell is the same in every mock: the header with the name of the product and the menu, the content, the bottom bar. During reporting the bar shows Report as the current place.
- A panel carries one thing at a time: the list of facts, the planning form, the route result, a fact, or one step of a report. A step names its number and has a way back and a way forward.
- The two votes are equal buttons. After a vote they are inactive, and the panel says why.
- A list row keeps the same fields in the same places everywhere: icon, type, distance where there is one, street, status, source and date, sample data mark.

## Constraints and open decisions

Drawn by the agent and not asked, for the user to confirm with the mocks:

- The status unverified is drawn in ink, not in the red of a barrier. Since version 4 of the specification a fact from OpenStreetMap that nobody voted on is unverified, so red would mark most of the list as a problem.
- The route without assessed segments is a hollow navy line, which is none of the four states and reads as a route without a judgement.
- The segments with partial data or no data stand in the list as a block of their own, after the three groups.
- A point report has five steps and an area has four, because an area has no check for existing facts.
- The action that deletes an account is drawn in the red of a barrier; every other primary action is navy.

Still open:

- The name of the product. The mocks show a placeholder.
- The texts. The Polish labels are working copy, written without the characters `docs/standards/standard_formatting.md` forbids.
- The rule for the labels of the route diagram when barriers are many or close together, as in the brief of the route result.
