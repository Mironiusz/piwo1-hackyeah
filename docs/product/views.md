# Views of the web frontend

Document state: 2026-10-04

## Why this document exists

This document lists the views of the web frontend of the MVP: what each view is for, what it shows, what a person can do in it, which states it has, where it leads, and what it needs from the programming interface. It is derived from `docs/product/user_journeys.md` and from `docs/product/specification.md`, version 11, and it adds no product rule. In case of a discrepancy the specification prevails.

It serves two readers. The initiative `plans/frontend_app/` of `MVP.md` builds the frontend from it, and the backend person reads its last sections as the view of the first consumer on the contract of the programming interface, `docs/product/api_contract.md`.

Where this document says OpenStreetMap, it names the source, not the text on the screen: the interface calls it map data, and the name itself stands only in the attribution on the map and on the page about the data.

It does not describe the look of a view. The design direction is in `PRODUCT.md` and `.impeccable/briefs/`, and the look of a view is designed separately, in that direction. The names of the views and of their parts are working names in English; the texts of the interface, in Polish and in English, are not fixed here.

## Structure of the app

The app is designed for a phone screen from 360 px wide. On a desktop browser it must not break and is not tuned.

The shell is the same in every view: a header with the name of the product and the menu, the content, and a bottom bar with three entries - Map, Report and Needs. Report is the primary action.

The content is one of two kinds:

- The map with a panel. The app has one map, which stays on the screen and keeps its position while its mode changes. The modes are facts, route planning, route result and point picking. A panel lies over the lower part of the map and carries the content of the mode; the fact detail and the steps of reporting open as panels over the map too.
- A page. The needs, the account, the privacy information, the page about the data and moderation are pages without the map.

| View                     | Kind                  | Journeys         |
| ------------------------ | --------------------- | ---------------- |
| V-1 Shell                | frame of every view   | all              |
| V-2 Needs                | page                  | J-1, J-2         |
| V-3 Map of facts         | map mode with a panel | J-3              |
| V-4 Route planning       | map mode with a panel | J-4              |
| V-5 Route result         | map mode with a panel | J-5              |
| V-6 Fact detail          | panel                 | J-8, J-9         |
| V-7 Reporting            | panel with steps      | J-6, J-7         |
| V-8 Address search       | part of V-4 and V-7   | J-4, J-7         |
| V-9 Legend               | part of V-3 and V-5   | J-3, J-5         |
| V-10 Menu                | part of V-1           | J-11, J-12, J-13 |
| V-11 Account             | page                  | J-11             |
| V-12 Privacy information | page                  | J-12             |
| V-13 About the data      | page                  | J-5              |
| V-14 Moderation          | page                  | J-10             |

Every view works with a keyboard alone and with a screen reader (J-14). The order of focus is the header, the content and the bottom bar; in a map mode the map is one stop that the keyboard can leave, followed by the panel. Everything a map shows is also in its panel as text.

## V-1. Shell

Shows:

- The header: the name of the product and the entry to the menu (V-10).
- The bottom bar: Map, Report, Needs.

A person can:

- Go to the map. It opens in the mode it was left in - facts, route planning or route result.
- Start a report (V-7), from any view.
- Open the needs (V-2).

States:

- Not logged in, logged in, logged in as a moderator. The difference is visible only in the menu.
- The session ended. The app shows once that the person is not logged in any more.
- The first opening on a device. The shell shows the needs (V-2) before anything else.

Kept on the device, and nowhere else: the profile, the chosen language, and that the first opening has happened.

## V-2. Needs

For: J-1, J-2.

Shows:

- The three presets: "I use a wheelchair", "I walk with a baby stroller", "Walking is difficult for me".
- The five barriers to avoid and the six amenities needed, each with whether it is set.
- That the needs stay on this device and are not tied to an account.
- On the first opening: a way to skip, and the language switch.

A person can:

- Pick a preset. It sets the items as the table of M1 says, replacing what was set. A preset is an action, not a stored choice: the app keeps only the items, so no preset shows as chosen afterwards.
- Set or clear a single item.
- Leave the view. The profile is kept on the device.

States:

- No barrier set. The view says that a route will then not be assessed segment by segment.
- No item set at all. The view says the same, and that the map of facts will show every fact.

Leads to: the map of facts on the first opening; otherwise the view the person came from. When a route is shown, leaving with a changed profile plans it again (V-5).

Needs from the programming interface: nothing.

## V-3. Map of facts

For: J-3. This is the view the app opens on after the first opening.

Shows on the map:

- The barriers and amenities of the profile and the geozones of its barrier types, or every fact when the switch says so. A geozone shows its area.
- The sample data mark on sample reports and geozones.
- The OpenStreetMap attribution, always visible.

Shows in the panel:

- The entry to route planning (V-4).
- The switch between the facts of the profile and every fact.
- The list of the facts in the visible area - type, street name, source, date, status, sample data mark - which is the text form of the map.
- The legend (V-9).

A person can: move and zoom the map, use the switch, open a fact from the map or from the list (V-6), start a route (V-4).

States:

- Loading the facts of the visible area.
- No fact in the visible area. The view says that no facts are known here, never that the area is free of barriers.
- Profile without any item. Every fact is shown, and the switch is inactive and says why.
- The facts cannot be loaded. A plain message; the map stays.
- The map cannot be drawn on the device. A plain message stands in place of the map, and the list carries the facts.

Hidden facts are never shown. An outdated fact is shown with its status and a muted marker, so that a person can confirm it again; a fact outdated because it was removed in OpenStreetMap is not shown.

Needs: N-1, N-12.

## V-4. Route planning

For: J-4.

Shows in the panel:

- The start, given in one of three ways: the current location, the address search (V-8), a point on the map.
- The destination, given by the address search or a point on the map.
- The action that asks for the route, active when both are set.

Shows on the map: the start and the destination once they are set.

A person can: set, change and clear the start and the destination; ask for the route; go back to the map of facts.

States:

- Nothing set, the start set, both set.
- Waiting for the consent of the browser to read the location.
- The location is refused or cannot be read. A plain message; the search and the point on the map stay.
- Point picking. The map shows a fixed mark at its center; the person moves the map, with touch or with the arrow keys, and confirms the point.
- A point or the current location outside Kraków. A plain message that routes work only in Kraków; the point is not set.
- The states of the address search (V-8).
- Waiting for the route. The answer can take several seconds.
- Routing does not answer. A plain message that a route cannot be planned right now; no route is shown.

Leads to: the route result (V-5); back to the map of facts (V-3).

Needs: N-2, N-3, N-4.

## V-5. Route result

For: J-5. The design direction of this view is in `.impeccable/briefs/route-result.md`.

Shows above the map: a summary - the route as a line whose stretches carry the segment states, with a text description of those stretches in order, which is the text form of the states, with the names of the start and the destination, and three numbers: the barriers of the profile on the route, the distance without data, and the length of the route. The entry to the needs and the action that changes the route stand next to it.

Shows on the map:

- The route in segments, each in one of the four states, with its color and its line pattern.
- The two straight stretches between the chosen points and the pedestrian network, in the state no data.
- Markers for the barriers of the profile, for the amenities of the profile within 50 m of the route, and an unverified report icon where a report contradicts OpenStreetMap below the threshold.
- The sample data mark and the OpenStreetMap attribution.

Shows in the panel:

- The statement of the route, when there is one: a proposed alternative with its reason, or that no route without barriers exists, or that the segments are not assessed.
- The legend (V-9).
- The list in three groups - barriers from the profile, additional barriers, amenities on the route. Every item has its type, its place as the street name and the distance from the start, its source, its date and its status.
- One plain note when the route has a segment with partial data or no data: some stretches of the route have no data, so barriers on them are not known. The note names no missing attributes.
- For a way OpenStreetMap marks as not accessible for wheelchairs, a sentence saying so.

A person can: open an item or a marker (V-6); take the proposed alternative and go back to the first route; change the route (V-4, with the start and the destination kept); open the needs (V-2); start a report (V-7).

States:

- The usual result.
- An alternative is proposed. It stands with the barrier that causes it and names the barrier and its status. There is at most one.
- The alternative is shown. It is the route on the screen, with its own states and list, and the way back to the first route.
- No route without barriers. The route with the fewest barriers, the plain statement, and the barriers listed.
- Mostly partial data or no data. The summary says how much is unknown.
- An empty group of the list. It says that no barriers are known, or that no amenities of the profile are near, and never that there are none.
- Profile without barriers. The route is drawn in a neutral style that is none of the four states, the statement says that the segments are not assessed because the profile names no barrier, the group of barriers from the profile is absent, and every barrier is in the group of additional barriers.
- Planning again, after the profile changed or after a vote or a report of the person was saved. The view shows that it is working and then the new result.
- Routing does not answer while planning again. The plain message of V-4, and no route.

The language switch keeps the route on the screen and asks for no new route.

Needs: N-3, N-12.

## V-6. Fact detail

For: J-8, J-9. A panel over the map, opened from V-3, from V-5, and from the existing facts of V-7.

Shows:

- The type; for stairs the number of steps when it is known; for a geozone its radius.
- The place as the street name; opened from a route, also the distance from the start.
- The source - map data or user report - and the date: for a fact from OpenStreetMap the day of its last edit there, for a user fact the day it was reported or last confirmed.
- The status in a word and an icon: unverified, confirmed, disputed or outdated.
- The sample data mark when it applies, and the description when there is one.
- For a report that contradicts OpenStreetMap: that OpenStreetMap says otherwise here.
- The person's own latest vote on this fact, when there is one. The frontend remembers it on the device after the vote; the programming interface returns no vote of the person.
- Two equal vote controls - still there, gone - and the flag action, which a fact from OpenStreetMap does not have.

A person can: vote; flag; close the panel.

States:

- The person can vote.
- The person already voted on this fact the same day. The controls are inactive and say that the next vote is possible the next day.
- The vote is being saved; the vote is saved, and the detail shows the status after it and the person's vote.
- The vote is refused because the person already voted on this fact the same day. A plain message, not an error.
- The fact is not available any more - hidden in the meantime. A plain message, and the panel closes.
- The fact is outdated. The panel shows that status and keeps the two votes, so that the fact can be confirmed again.
- Flagging: one confirmation, without a reason, then a message that the content was passed to moderation.
- The vote or the flag cannot be saved. A plain message; nothing changed.

Leads to: the map mode it was opened from. When a route is shown, a saved vote plans it again (V-5).

Nothing about who reported or voted, and nothing about weights, is shown.

Needs: N-5, N-8, N-9.

## V-7. Reporting

For: J-6, J-7. A panel with steps over the map, opened from the bottom bar.

Steps:

1. The kind: a barrier, an amenity or an area.
2. The point. The map is in the mode point picking: a fixed mark at its center, moved with touch or with the arrow keys, and a confirmation. A control moves the map to the current location of the device, in the browser only. For an area the point can also be given by the address search (V-8).
3. The details. The type from the closed list of the kind; an optional description; for stairs an optional number of steps; for an area the radius from the list 10, 25, 50, 100 m and a barrier type.
4. The existing facts, for a barrier or an amenity only: the facts of the same type within about 15 m, each with what a fact detail shows, and the question whether it is the same one, with an answer for each fact and an answer for none of them.
5. The summary: the kind, the type, the point on the map, the optional fields, and the action that approves it.
6. Saved: a message, and the new fact on the map.

A person can: go a step back; leave at any step, which saves nothing; approve the summary.

States:

- Each step, with what was already given kept when the person goes back.
- No existing fact nearby. Step 4 is skipped.
- It is the same one. The report becomes a vote on that fact, and the states of voting of V-6 apply, the refusal on the same day included.
- Saving; saved.
- The report cannot be saved. A plain message; the panel keeps what was given, so the person can try again.
- The states of the address search (V-8), for an area.

The summary says nothing about a point that lies far from every way.

Leads to: the map mode it was opened from. When a route is shown, a saved report or area plans it again (V-5).

Needs: N-4, N-6, N-7, N-10.

## V-8. Address search

Part of V-4 and of V-7.

Shows: a text field, a search button, and under them the results or a message.

A person can: type, submit with the Enter key or the button, move through the results and pick one.

States:

- Empty; a text typed and not submitted. Nothing is suggested while typing.
- Searching.
- Results: a list of at most ten places in Kraków, each with its full address, also when there is one. A screen reader announces how many there are. Nothing is set until the person picks an item.
- Nothing found in Kraków. A plain message.
- The search is unavailable. A different plain message.
- The text is empty or longer than 200 characters. A plain message asking for another text.

In the last three states no point is set, and the point on the map stays available. The text of a search never stands in the address of the page. The labels of the results come from the search as they are, also when the interface is in English.

Needs: N-4.

## V-9. Legend

Part of V-3 and of V-5.

Shows:

- The four segment states, each with its color, its line pattern and its name: barrier, no barrier, partial data, no data. In V-3 this part is absent, because there is no route.
- The kinds of markers: a barrier, an amenity, a geozone, an unverified report that contradicts OpenStreetMap.
- The sample data mark and what it means.
- The date of the OpenStreetMap copy in use, as a calendar day.
- The way to the page about the data (V-13).

## V-10. Menu

Part of V-1, opened from the header.

Shows:

- The account: the way to V-11, with the pseudonym when the person is logged in.
- The language switch, Polish and English.
- The privacy information (V-12).
- The page about the data (V-13).
- Moderation (V-14), only for an account with the moderator role.

## V-11. Account

For: J-11. A page.

States and what each shows:

- Not logged in: the pseudonym and the password, the action that logs in, and the way to creating an account.
- Creating an account: the pseudonym, the password, the rules of both, and that a forgotten password cannot be recovered. The view asks for no email address.
- Logged in: the pseudonym, the action that logs out, and the action that deletes the account.
- Deleting: what is removed - the account and the pseudonym - what stays - the reports and the votes, detached from the person - and one confirmation. The password is not asked again.

Messages:

- The pseudonym is taken; the pseudonym breaks a rule, and which one - 3 to 30 characters of letters, digits, the underscore and the hyphen.
- The password is shorter than 5 characters.
- The pseudonym and the password do not match, without saying which.
- The account was deleted.
- The request cannot be answered right now.

The view says nothing about the weight of a contribution from an account, and nothing about the needs, which are not part of the account.

Leads to: the view the person came from.

Needs: N-11.

## V-12. Privacy information

For: J-12. A page of text in the language of the interface.

Shows what the app keeps, for what purpose and for how long - the pseudonym and the password of an account, and the identifier of a vote without an account until the demo and all its data are deleted on 4 October 2026, which is pseudonymized personal data - and what it does not keep: the needs, the current location, an email address, any information about a disability. In the hosted demo it also says that the demo and all its data are deleted on 4 October 2026, after the results are announced.

Needs from the programming interface: nothing.

## V-13. About the data

A page of text in the language of the interface, reached from the menu and from the legend.

Shows:

- Where the facts come from: OpenStreetMap and reports of people, and how the two are told apart on every fact.
- The date of the OpenStreetMap copy in use.
- What the statuses mean, in words: unverified, confirmed, disputed, outdated. It gives no weights and no numbers of votes.
- What the four segment states mean, and that missing data is never shown as accessible.
- What the sample data mark means.
- How wrong or outdated data is corrected: by voting on a fact and by reporting.
- The licence and the attribution of OpenStreetMap.

Needs: N-12.

## V-14. Moderation

For: J-10. A page, for an account with the moderator role only.

Shows:

- The flagged content that is not hidden - reports, geozones, facts converted from OpenStreetMap - each with what a fact detail shows and its place on a map, and nothing about its author or about who flagged.
- The hidden content, with the action that restores it.

A person can: hide an item; restore a hidden item.

States:

- Loading; nothing flagged.
- An item hidden or restored: it moves between the two lists.
- Access denied: the account has no role, or the role was removed while the session is active. A plain message, and the menu loses the entry.

A flag cannot be dismissed: a flagged item that is not hidden stays in the first list.

Needs: N-13.

## Messages

Every message is plain, has its text in both dictionaries, and where it comes from the server it arrives as a code.

- A route cannot be planned right now.
- No route without barriers exists.
- Some stretches of this route have no data.
- An alternative route avoids a named barrier with a named status.
- The segments are not assessed, because the profile names no barrier.
- The location cannot be read.
- Routes work only in Kraków.
- Nothing was found in Kraków; the search is unavailable right now; this text cannot be searched.
- No facts are known here; no barriers are known on this route; no amenities of the profile are near this route.
- The vote was saved; the next vote on this fact is possible the next day; this fact is not available any more.
- The content was passed to moderation.
- The report was saved; the area was saved.
- This cannot be saved right now; this cannot be loaded right now.
- The session ended.
- The messages of the account (V-11).
- This view needs the moderator role.
- The map cannot be drawn on this device.

## What the views need from the programming interface

These are the needs of the first consumer, in words. The paths, the shapes and the codes are those of `docs/product/api_contract.md`.

Needs of every operation:

- Everything from a closed list arrives as a code: the types, the sources, the statuses, the segment states, the kinds of messages. The frontend translates codes, so a change of language asks for nothing again.
- Every date arrives as a calendar day in the Europe/Warsaw zone. The frontend converts no time.
- The frontend applies no product rule. The segment states, the groups of the list, the status of a fact and whether a fact can be flagged arrive as decided by the server.
- Nothing about the author of a report, a vote or a geozone, and no weight, arrives.
- The page and the programming interface are on one host.

Operations:

- N-1. The facts of an area of the map: barriers, amenities and geozones, narrowed to a set of types or not, without hidden ones and without those outdated because they were removed in OpenStreetMap. For each: the type, the point, for a geozone the radius, the street name, the source, the date, the status, the sample data mark.
- N-2. Whether a point lies in Kraków, at the moment the point is set, for a point on the map and for the current location.
- N-3. A route for a start, a destination and the preferences of the profile. The answer carries: the segments with their geometry, their state, the marking of a way not accessible for wheelchairs and the two straight stretches at the ends; the three groups with their items, each with the distance from the start and the street name; at most one alternative with its reason; whether no route without barriers exists; whether the segments are assessed at all; the length of the route. Separate outcomes: routing does not answer; a point is outside Kraków.
- N-4. The address search: the text in the body of the request; the answer is a list of at most ten matches with a label and a point, an empty list, the search unavailable, or the text refused.
- N-5. One fact with everything the fact detail shows and whether it can be flagged. The person's own latest vote and the day from which the next vote is possible are kept on the device (decision 14).
- N-6. The existing facts of a type near a point, for the check before a report is saved.
- N-7. Saving a point report: the kind, the type, the point, the optional description, the optional number of steps.
- N-8. A vote on a fact: confirm or deny. Outcomes: saved, with the status after it; refused because the person already voted on it the same day; the fact is not available.
- N-9. A flag on a fact. Outcomes: saved; the fact cannot be flagged.
- N-10. Saving a geozone: the point, the radius, the barrier type, the optional description.
- N-11. The account: creating one, logging in, logging out, deleting, and who is logged in now - the pseudonym and whether the account has the moderator role. Outcomes of creating: the pseudonym is taken; a rule is broken, and which one.
- N-12. The date of the OpenStreetMap copy in use.
- N-13. Moderation: the flagged content that is not hidden, the hidden content, hiding, restoring. Outcome for an account without the role: denied.

The form of the contract. The frontend person asks for the contract as an OpenAPI description, generated by FastAPI from the backend code and kept as a file in the repository. The frontend generates its TypeScript types from that file, so a difference between the contract and the code shows up in the type check. It was written as the answer to the first half of a question the plan of the contract had open at that time; that plan was closed on 2026-10-03 without it, with the contract approved in place of the frontend person (`plans_finished/api_contract/API_CONTRACT_PLAN.md`, D-10).

## The views read against the contract of the team

On 2026-10-03 the contract was written as `docs/product/api_contract.md`, without the list above, and approved in place of the frontend person. The agent read it against the views on the same day, and it reached this branch with the merge of `dev` on 2026-10-04. It is a document in prose, not an OpenAPI description; the frontend writes its types from it by hand until the backend code exists and FastAPI can generate the description of decision 6.

The contract covers the views, with these differences:

- The street name of a fact has no field, and the stored data keeps no name of a way. Deferred by the user until the backend person tests the programming interface (decision 13).
- The own vote of a person has no field. A vote repeated on the same calendar day is refused with the instant from which the next vote is accepted, the start of the next day, and the frontend keeps the vote on the device (decision 14).
- A point outside Kraków has no outcome of its own. Proposed by the agent: the frontend checks a point against the bounds of the map of Kraków before it asks for a route, and gives the same message when the request is refused for its start or its destination.
- A segment carries its missing attributes. The frontend does not show them (decision 8).
- The contradiction of a report with OpenStreetMap is one mark on a fact of a route. It does not say what OpenStreetMap shows there, so the note of the fact detail is a general sentence, and a fact opened from the map of facts has no such note.

The contract adds what the views did not name, and the build covers it:

- The facts of an area are at most 1000; when the area holds more, the map of facts asks the person to zoom in.
- Saving a report or a geozone carries a key that the frontend generates once, when the person approves the summary, and repeats with every attempt of the same save.
- The session is a token that the frontend keeps in the storage of the browser and replaces with the renewed one of every answer; a route request, an address search, creating an account and logging in carry no token.
- A request refused because the session expired logs the person out, with a message, and lets them repeat the action.
- The address search always shows a list to pick from, also for one match.
- Creating an account does not log in; the frontend logs in right after it.

## Decisions behind the views

Decided by the user, the frontend person of the team, on 2026-10-03, question by question:

1. The app has one map with modes - facts, route planning, route result, point picking - and not separate screens with a map each.
2. The bottom bar has Map, Report and Needs; the account, the language, the privacy information and moderation are in a menu in the header. The profile is called the needs, so that it is not taken for the account.
3. The fact detail and the steps of reporting are panels over the map.
4. The date of the OpenStreetMap copy stands in the legend and on a page about the data.
5. Moderation is an entry of the menu that only an account with the moderator role sees.
6. The contract of the programming interface is asked for as an OpenAPI description generated by FastAPI.
7. This document is the list of views; the look of each view is designed separately.
8. The list of the route names no missing attributes: one plain note says that some stretches have no data. Decided with the mocks, because the Kraków brief asks only that incomplete data is marked and never shown as accessible.
9. The texts of the interface do not use the name OpenStreetMap. The source is called map data, in the working Polish copy "dane mapy"; the name stands only in the attribution on the map and on the page about the data.
10. The states that have no mock are not drawn as mocks. The build covers them from this document.
11. An outdated fact stays on the map with its status and can be confirmed again; only a fact removed in OpenStreetMap disappears. The user took over the rule the team had decided in `plans_finished/api_contract/` on the branch `dev`, in place of the earlier choice that an outdated fact is shown nowhere.
12. A pseudonym keeps its narrower rule - 3 to 30 characters of letters, digits, the underscore and the hyphen - and the user asks the owners of `docs/product/api_contract.md` to bring it into the contract, which accepts every character that is not a control character. The contract took the rule on 2026-10-04.
13. Whether a list row names the street is deferred until the backend person tests the programming interface, which has no field for it. The sample data of the demo carries the street, and a row without a street name shows no place line.
14. The own vote of a person is remembered on the device. On another device the person learns of it from the refusal of a vote repeated on the same day.
15. No frontend code is written before Q-11 of `plans_finished/mvp/MVP_PLAN.md` is decided; until then the frontend person prepares everything that does not depend on it. Q-11 was decided on 2026-10-04 in `plans_finished/backend_architecture/`, and `MVP.md` gives the frontend to the initiatives `plans/frontend_app/` and `plans/map_tiles/`, which wait for nothing to start.
16. The demo runs only on the programming interface of the service. The frontend shows no route and no fact from sample data of its own when the service is not ready; decided on 2026-10-04 as the position of the frontend person, with the last word left to the team.
17. The navigation between the views uses the library React Router, decided on 2026-10-04. The reason for the new run time dependency: the addresses of the views and the back button of the browser, without code of our own to test.

Proposed by the agent and not asked one by one:

- A preset is an action that sets the items, and no preset shows as chosen afterwards, because M1 says a preset is not stored.
- With a profile without any item the switch of the map of facts is inactive and says why.
- The page about the data explains the statuses in words and gives no weights and no numbers of votes, because M9 keeps them inside the system.
- Whether a point lies in Kraków has to be known when the point is set (N-2); how the frontend learns it is for the contract.

## The hosted demo

The hosted demo is served over plain HTTP (`MVP.md`, Known departures from the Kraków brief), and a browser gives no location to a page served that way. There the start from the current location, and the location action while reporting, end in the state of the refused location. Since version 10 of the specification the demo does not show routing that does not answer; that state of V-4 stays and is checked outside the hosted link.

## What stays open

- The texts of every label and message in Polish and in English, and the Polish names of the terms: in `docs/product/interface_texts.md`, with the rules of the wording decided on 2026-10-04 and the single texts working copy until the views are built.
- The rule for the labels of the summary line when barriers are many or close together (`.impeccable/briefs/route-result.md`, Constraints and open decisions).
- Whether a list row names the street (decision 13).
- The views of the optional feature O9, routes with public transport, added by version 8 of the specification: a switch in route planning, a public transport segment in the route result and the statement that public transport was unavailable. `MVP.md` gives them to `plans/frontend_app/` once `plans/public_transport_routing/` has written its interface into the contract. No view and no mock covers them.
