# FRONTEND_ALGORITHM

Document state: 2026-10-04

## Algorithm goal

The frontend shows a person what the service knows - the facts of an area, a route for the needs of the person, the detail of one fact - and sends what the person does: a route request, a vote, a flag, a report, an account. It applies no rule of the product. It decides only two things: how an answer of the service is shown, so that nothing depends on color alone and nothing is known only from the map, and when the service is asked, so that it is asked only for an action of the person.

## Domain concepts

- Needs: the barrier types a person avoids and the amenity types a person needs. They live only on the device and travel only inside a route request.
- Fact: a barrier, an amenity or an area with its source, its days and its status, as `docs/product/api_contract.md` defines it. A route fact is a fact with its distance from the start and the mark that the map data contradict it.
- Segment state: one of the four states the service gives a segment of a route - barrier, no barrier, partial data, no data.
- Assessed route: a route planned for needs with at least one barrier. A route planned for needs without a barrier is not assessed, and its segments are drawn in a neutral style that is none of the four states.
- Stale route: a shown route planned for needs that have changed since, or planned before a vote or a report of the person was saved.
- Own vote: the latest vote of the person on a fact, with the instant from which the next vote is accepted, the start of the next calendar day. The service returns no vote of the person, so the device remembers it, together with its voter: the pseudonym of the account of the session, or nobody for a person without an account. A remembered vote is shown only to its voter.
- Rest: the position of the map once it has stood still for 0.3 seconds.
- Sample data mark: the mark on every fact the demo added for the show.

## General process map

1. On opening, the frontend reads what the device keeps: the needs, the language, the session token and the own votes. A value it cannot read is dropped. On the first opening it shows the needs before anything else.
2. On the map of facts, every rest of the map at zoom 14 or closer asks the service once for the facts of the visible rectangle. The facts of the needs, or every fact after the switch, are shown twice: as markers and as a list, which is the text form of the map.
3. For a route, the person gives two points, and the frontend sends one request with the points and the needs. The answer is shown as a summary line with three numbers, as line layers on the map, and as a list in three groups.
4. The detail of a fact is read from the service when it opens. A vote is sent once, its answer replaces the shown fact, and the device remembers the vote.
5. A report goes through its steps without sending anything, then checks for existing facts of the same type nearby, and is saved once after the summary is approved.
6. A route that became stale is planned again once, when the person is back on it.

## Detailed run order

Opening:

- The language is the stored one, else Polish when the first language of the browser is Polish, else English.
- A stored session token is checked once by reading the account of the session. A token the service refuses is removed, and the person is told once that they are logged out. When the check gets no answer about the token, the token stays, and the account page says that something went wrong and offers to try again, in place of the form for logging in.
- Needs with the first opening not yet done lead every address to the needs. Leaving the needs, by any way, ends the first opening.

Map of facts:

- The map reports a rest 0.3 seconds after it stopped moving and never while it moves. A rest below zoom 14 asks nothing, and the view asks the person to zoom in.
- While a request runs, the last facts stay on the screen. An answer that arrives after a newer request started is dropped.
- With the scope of the needs, a fact is shown when its type is one of the needs; an area is shown by its barrier type. Needs without any item show every fact, and the switch is inactive and says why.
- An answer marked as cut off asks the person to zoom in. No fact in the scope says that none is known here.
- Until the map has rested for the first time the list says that it is loading, and never that no fact is known.
- When the map cannot be drawn, a message stands in its place, and the list shows the facts around the place the map would have opened on. The map cannot be drawn when it cannot be created, when its style does not load, and when the tile archive cannot be read; an error of one tile or of a font leaves the map on the screen.

Route:

- The start from the location of the device is read only when the person asks for it. A point outside the bounds of Kraków is refused before any request, with the same text the view shows when the service refuses a point.
- The address search is sent when the person submits the text. The matches are a list to pick from, also when there is one.
- The route request carries the two points and the needs, and nothing else.
- The summary line draws the segments in their order, joined where neighbours share a state, each in the pattern of its state, with a stop for every barrier of the needs. Next to the line stands the same order as a text.
- The three numbers are the count of the barriers of the needs, the length of the segments without data, and the length of the route.
- The map draws one line layer for each state, markers for the barriers of the needs and for the amenities of the needs, and nothing for a barrier outside the needs.
- The list shows the three groups as the service ordered them. The proposal of the alternative stands under the first barrier it avoids and names that barrier and its status.

Fact detail:

- The detail shows the kind, the source, every day the service gave, the status, and for a fact of a route its distance from the start.
- The two votes are inactive while a vote of the person is remembered and the next calendar day has not started, while a vote is being sent, and after the service answered that the vote came too soon.
- A saved vote stores the voter, the verdict, the day and the start of the next calendar day on the clock of the device, and marks a shown route as stale. The device keeps one vote for a fact, the latest one cast on it.
- The flag action exists only for a fact the service marks as one that can be flagged, and it asks for one confirmation.

Report:

- Nothing is sent before the summary is approved, except the check for existing facts once the details are given.
- The answer that the report is one of the existing facts sends a confirmation of that fact and saves no report.
- The key of a save is generated once, when the summary is approved, and repeated with every attempt of the same save.
- A saved report is remembered on the device as the own vote of its author on the new fact, because a report carries the confirmation of its author.

## Domain rules

- The segment states, the groups of the list, the status of a fact, whether a fact can be flagged and every day are shown as the service gave them.
- A segment state is never told by color alone: a barrier is red with white stripes, no barrier is solid green, partial data is amber with dark dashes, no data is a grey dotted line. The legend, the summary line and the map use the same four patterns.
- A route that is not assessed is one hollow navy line, and the view says that its stretches are not assessed. Its barriers stand in one group.
- A route with a segment in partial data or no data shows one note that some stretches have no data. No missing attribute is named.
- An empty group says what is not known, with the length without data, and never that the route is free of barriers.
- An outdated fact stays on the map of facts with a muted marker and keeps both votes.
- A report the map data contradict has a dashed marker on the route, and its detail says that the map data show something else.
- The source of a fact is called map data. The name OpenStreetMap stands only in the attribution on the map and on the page about the data.
- A day is written as the service gave it, in the form of the language, and an instant shows the hour of its text. No time zone is converted.
- A text written by a person is shown as plain text.
- A pseudonym is checked in the form against the rule of the contract: 3 to 30 characters of the 26 Latin letters and the nine Polish letters, each in both cases, the digits 0 to 9, the underscore and the hyphen.
- A label of a stop of the summary line is left out when it would run into the label before it. The text next to the line and the list name every barrier.
- The markers of the map are buttons with a text name and are left out of the order of the Tab key, because the list under the map holds the same facts as links. The map itself is one stop the keyboard can leave. A view that picks a point on the map has a control that moves the focus to the map.

## Reconcile and deduplication

- A report is saved with a key the frontend generates once, so a save repeated after a lost answer leaves one report.
- A route request for the same two points and the same needs as the one that is running is not sent again. An answer of an older request is dropped.
- A stale route is planned again once: the new answer carries the needs it was planned for, which ends the stale state.
- A vote is sent once. The device then keeps the votes inactive until the next calendar day, and a vote the service refuses as too soon is shown as a plain message with the day from which the next one is possible.
- The session token of every answer replaces the stored one.

## Diagnostics and summary

- Every failed request becomes one error with the code of the contract, and a request without any answer becomes a network error. A view maps the code to a text of the interface and never shows the code.
- A failure while a view is drawn ends in the text that something went wrong, with a way to try again, instead of an empty page.
- The frontend writes nothing to the console and sends nothing to a host other than the one the page came from.
