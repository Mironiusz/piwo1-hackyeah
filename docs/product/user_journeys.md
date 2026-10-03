# User journeys of the MVP

Document state: 2026-10-03

## Why this document exists

This document describes, step by step, what a person does in the app and what the app answers, for every mandatory feature M1 - M11 of `docs/product/specification.md`, version 6. It is derived from that specification and from `plans/mvp/MVP_PRD.md`, and it adds no product rule of its own: where the journeys needed behavior that no earlier version described, the rule was decided by the user on 2026-10-03 and entered version 6 of the specification. In case of a discrepancy the specification prevails.

The journeys are the input for two things: the list of views of the web frontend (`docs/product/views.md`), and the consultation of the frontend person on the contract of the programming interface (`plans/api_contract/API_CONTRACT_PLAN.md`, Q-1). They do not describe the layout or the look of a screen; the design direction is in `PRODUCT.md` and `.impeccable/briefs/`.

## How to read it

People:

- The person on the way: a wheelchair user, a parent with a baby stroller or a person with walking difficulties, who plans a walking route in Kraków.
- The contributor: anyone, with or without an account, people without any mobility limits included, who reports, confirms or denies facts.
- The moderator: a member of the team with the moderator role.

Places of the app the journeys move between. The names are working names for the list of views:

- the needs screen - the preference profile with its presets,
- the map of facts - the map the app opens on,
- route planning - the start and the destination,
- the route result - the map of the route, the legend and the list,
- the fact detail - one barrier, amenity or geozone with its source, date and status, and the votes,
- reporting - the steps of a point report or of an area,
- the account - creating an account, logging in, logging out, deleting,
- the privacy information,
- the moderator view.

A fact is a barrier or an amenity of the closed list at a place, or a geozone. Without an account and logged in are the two ways a person contributes; the journeys are the same for both unless a journey says otherwise.

Every journey gives who it is for, where it starts, its steps, its branches, where it ends and the rules it rests on. M stands for a section of the specification, FR and AC for `plans/mvp/MVP_PRD.md`.

## J-1. First opening: setting the needs

For: anyone who opens the app for the first time on a device.

Starts: the app is opened and the device holds no profile.

1. The app shows the needs screen before anything else, in the language of the browser: the three presets, the five barriers to avoid, the six amenities needed, and a way to skip.
2. The person picks a preset - "I use a wheelchair", "I walk with a baby stroller" or "Walking is difficult for me". The app marks the items of that preset, as the table of M1 says.
3. The person changes single items, for example unticks stairs.
4. The person leaves the screen. The app keeps the profile on the device and opens the map of facts.

Branches:

- Skip. The app opens the map of facts with a profile without any item. A route can still be planned; it has no segment states (J-5, branch Profile without barriers), and the map of facts shows every fact (J-3).
- Items without a preset. The person marks items one by one; the end is the same.

Ends: the profile is on the device and nowhere else. Nothing was sent, and nothing about a disability was asked.

Rests on: M1; FR-1; AC-1.

## J-2. Changing the needs later

For: anyone with the app open.

Starts: the map of facts or the route result, both of which lead to the needs screen.

1. The person opens the needs screen. It shows the items as they were left.
2. The person changes items or picks another preset.
3. The person leaves the screen. The app keeps the new profile on the device.

Branches:

- A route is shown. The app plans the route again for the same start and destination. Its course, its segment states and its list may change. When routing does not answer at that moment, the app shows the message of J-4 and no route.
- The map of facts is shown. It shows the facts of the new profile.
- Every barrier is unticked. The profile has no barrier, which is allowed (J-5, branch Profile without barriers).
- Another device, or the same person after logging in elsewhere. The profile there is empty: it is never tied to an account.

Ends: the new profile is on the device, and nothing on the screen follows the old one.

Rests on: M1, M2; FR-1; AC-1.

## J-3. Looking at the map of facts

For: anyone; it is the place where a contributor finds facts without planning a route.

Starts: every opening after the first, and the way back from any other place.

1. The app shows the map of Kraków with the facts of the profile: its barriers to avoid, its amenities needed and the geozones of its barrier types. The OpenStreetMap attribution is visible. Hidden and outdated facts are not shown. The same facts are available as a list, which is the text form of the map.
2. The person moves the map, with touch or with the keyboard.
3. The person uses the switch to see every barrier and amenity, and back to the facts of the profile.
4. The person opens a fact and gets the fact detail (J-8).
5. From here the person starts a route (J-4) or a report (J-6, J-7), or opens the needs screen (J-2), the account (J-11) or the privacy information (J-12), or switches the language (J-13).

Branches:

- Profile without any item. The map shows every fact, because there is nothing to narrow it to.
- The map cannot be drawn on the device. The app says so in place of the map, and the list carries the facts.

Ends: the person has seen what is known around a place, with nothing presented as accessible for lack of data.

Rests on: M4, M10; FR-15, FR-16.

## J-4. Planning a route

For: the person on the way.

Starts: the map of facts.

1. The person opens route planning.
2. The person gives the start in one of three ways.
   - The current location. The browser asks for consent; when it is given, the start is the current location.
   - An address or the name of a place. The person types it and submits it with the Enter key or the search button; nothing is suggested while typing. The app shows a list of the matches in Kraków, each with its full address, also when there is only one, and a screen reader announces how many there are. The start is set only when the person picks an item.
   - A point on the map.
3. The person gives the destination by an address or a name, or by a point on the map, in the same way.
4. The person asks for the route. The app sends the start, the destination and the preferences of the profile, and shows that it is working; the answer can take a few seconds.
5. The app shows the route result (J-5).

Branches:

- The location is refused or cannot be read. The app says so, and the start is given by an address or a point on the map.
- A point or the current location outside Kraków. The app says plainly that routes work only in Kraków, and the point is not set.
- Nothing found. The app says plainly that nothing was found in Kraków. No point is set, and the point on the map stays available.
- The search is unavailable. The app says, in different words, that the search cannot be answered right now. No point is set, and the point on the map stays available.
- The text is empty or longer than 200 characters. The app says that this text cannot be searched and asks for another one.
- Routing does not answer. The app says plainly that a route cannot be planned right now and shows no route.
- Profile without barriers. The route is planned (J-5, branch Profile without barriers).

Ends: a route result, or a plain message and no route. Nothing of the request is stored; the current location was used for this request only.

Rests on: M2 with its address search; FR-2, FR-17; AC-2, AC-16.

## J-5. Reading the route result

For: the person on the way.

Starts: a planned route.

What the result carries:

- The route on the map, cut into segments, each in one of four states - barrier, no barrier, partial data, no data - with its own color and line pattern, and a legend that names the four.
- The two straight stretches between the chosen points and the pedestrian network, at the start and at the end, always in the state no data.
- Markers for the barriers of the profile and for the amenities of the profile within 50 m of the route.
- The list in three groups - barriers from the profile, additional barriers, amenities on the route - where every item has its type, its place as the street name and the distance from the start, its source, its date and its status.
- For a segment with partial data or no data, the missing attributes by name: kerbs, surface, incline, width, and on the two stretches at the ends the steps, for a profile that avoids stairs.
- The sample data mark on every sample report and geozone, on the map and on the list.
- The OpenStreetMap attribution and the date of the OpenStreetMap copy in use.
- A summary before anything else: how many barriers of the profile are on the route, how much of the route has no data, and how long the route is.

1. The person reads the summary.
2. The person reads the map and the list. Both say the same; the list is the text form of the map.
3. The person opens an item of the list or a marker and gets the fact detail (J-8).
4. The person decides on their own whether to take the route. The app gives no verdict, score or label.

Branches:

- An unverified or disputed barrier of the profile that OpenStreetMap does not contradict. The route goes through it and its segment is in the state barrier. When a way around it exists, the app proposes one alternative route and says why, naming the barrier and its status. The person takes the alternative, which is then shown as the route with its own states and list, and can go back to the first route.
- No route without barriers. The app shows the route with the fewest barriers, says plainly that no route without barriers exists, and lists where the barriers are.
- A report that contradicts OpenStreetMap and has not reached the threshold. The segment follows OpenStreetMap, an unverified report icon stands at the place, and the list shows the report among the barriers from the profile as unverified.
- A way that OpenStreetMap marks as not accessible for wheelchairs. Its segment is never in the state no barrier; where it would be, it is partial data, and the list says that OpenStreetMap marks the way as not accessible for wheelchairs.
- Mostly partial data or no data. The states say so, the summary says how much is unknown, and an empty group of the list says that no barriers are known, never that there are none.
- Profile without barriers. No segment has a state. The route is drawn in a neutral style that is none of the four, the app says that the segments are not assessed because the profile names no barrier, and every barrier on the route is in the group of additional barriers.
- A contribution saved while the route is shown. After a vote or a report of the person is saved (J-6, J-7, J-8), the app plans the route again for the same start and destination.
- Another route. The person goes back to route planning with the start and the destination kept.

Ends: the person knows the barriers of their profile on the route, what is unknown about it, and how far each fact can be trusted.

Rests on: M2, M7, M8, M10; FR-3, FR-4, FR-9, FR-10, FR-11, FR-15, FR-18; AC-3, AC-4, AC-8, AC-9, AC-10, AC-14, AC-17.

## J-6. Reporting a barrier or an amenity

For: the contributor, with or without an account.

Starts: the one entry to reporting, on the map of facts and on the route result.

1. The person chooses what they report: a barrier, an amenity or an area. An area continues in J-7.
2. The person sets the point on the map. At the person's request the app moves the map to the current location of the device; nothing is sent, and the point is only the one the person sets.
3. The person chooses the type from the closed list: stairs, high kerb, poor surface, steep incline or narrow passage for a barrier; ramp, elevator, lowered kerb, accessible toilet, rest place or handrail at stairs for an amenity. A description is optional, and so is the number of steps for stairs.
4. The app shows the existing facts of the same type within about 15 m, facts from OpenStreetMap included, and asks whether it is the same one. Hidden and outdated facts are not shown.
5. The person answers no, or there was nothing to show. The app shows a summary: what is reported, where, and the optional fields.
6. The person approves the summary. The app saves the report: a user report, unverified, dated today, carrying the confirmation of its author. Nobody can edit it afterwards, the author included.

Branches:

- It is the same one. The report becomes a confirmation of the existing fact and follows J-8, its limit of one vote a day included. No new report is saved.
- The person leaves before approving. Nothing is saved.
- The point lies farther than 15 m from every way of the pedestrian network. The report is saved and shown like any other; it changes no route, and the app does not say so.
- A route is shown. After the report is saved, the app plans the route again (J-5).

Ends: a new fact on the map with the status unverified, or one more confirmation of an existing fact. Nothing about the author is shown to anyone.

Rests on: M3, M4; FR-5, FR-13; AC-5.

## J-7. Marking an area

For: the contributor, with or without an account; the whole journey works with a keyboard alone.

Starts: the entry to reporting, with an area chosen in step 1 of J-6.

1. The person gives the point of the area on the map or by searching an address, with the list of matches of J-4.
2. The person chooses the radius from the list: 10, 25, 50 or 100 m.
3. The person chooses the barrier type from the closed list of barriers. A description is optional.
4. The app shows a summary: the point, the radius, the type and the description.
5. The person approves the summary. The app saves the geozone as unverified. Nobody can edit it afterwards.

Branches:

- Keyboard alone. The point is given by the address search, or by moving the map under a fixed mark with the arrow keys; the radius and the type are lists. No step needs a pointer.
- The search finds nothing or is unavailable. The messages of J-4 apply, and the point on the map stays available.
- A route is shown. After the geozone is saved, the app plans the route again (J-5).

Ends: a geozone that other people confirm or deny like any fact (J-8), that can be flagged (J-9), and that routes avoid for a profile with its barrier type while it is unverified, confirmed or disputed.

Rests on: M5, M2; FR-8; AC-7.

## J-8. Confirming or denying a fact

For: the contributor, with or without an account.

Starts: the fact detail, opened from the list or a marker of the route result, from the map of facts, or from step 4 of J-6.

The fact detail shows the type, the place, the source - OpenStreetMap or user report - the date, the status, the sample data mark when it applies, the description when there is one, the number of steps of stairs when it is known, and the person's own latest vote on this fact when there is one. A fact from OpenStreetMap shows the date of its last edit in OpenStreetMap; a user fact shows the date it was reported or last confirmed.

1. The person chooses one of two equal answers: still there, or gone.
2. The app saves the vote and shows the status of the fact after it, together with the person's own vote.
3. Until a day has passed since that vote, the vote controls of this fact are inactive, and the app says that the next vote is possible after a day.

Branches:

- The person voted on this fact less than a day ago. The controls are inactive from the start, with the same explanation. A vote that reaches the server earlier than a day after the previous one is refused, and the app says so; this is an ordinary answer, not an error.
- A change of mind after a day. The new vote replaces the earlier one; only the latest vote of a person counts, and a vote cannot be withdrawn without casting another one.
- The fact becomes outdated. It disappears from the maps and the lists.
- The fact was hidden by a moderator in the meantime. The vote is refused, and the fact is gone from the screen.
- A fact from OpenStreetMap. It is voted on in the same way and has the same statuses; a confirmation updates its date of last confirmation, and its shown date stays the date of its last OpenStreetMap edit.
- A geozone. It is voted on in the same way.
- A route is shown. After the vote is saved, the app plans the route again (J-5).

Ends: the vote counts toward the status of the fact. Nothing about who voted, or about the weight of the vote, is shown to anyone.

Rests on: M4, M9; FR-6, FR-7, FR-13, FR-15; AC-6, AC-12.

## J-9. Flagging content

For: anyone, with or without an account.

Starts: the fact detail of a report, of a geozone, or of a fact converted from OpenStreetMap, which shows as a user report.

1. The person chooses to flag the content.
2. The app asks for one confirmation. It asks for no reason.
3. The person confirms. The app saves the flag, without anything about who flagged, and says that the content was passed to moderation.

Branches:

- A fact from OpenStreetMap. Its detail has no flag action.

Ends: the content appears in the moderator view (J-10). For everyone else nothing changes until a moderator hides it.

Rests on: M11; FR-14; AC-13.

## J-10. Moderating

For: the moderator.

Starts: the moderator is logged in (J-11) and opens the moderator view.

1. The app shows the flagged content: reports, geozones and facts converted from OpenStreetMap, each with what a fact detail shows and nothing about its author or about who flagged.
2. The moderator hides an item. It disappears for everyone: from the maps and the lists, from routes and segment states, from the check for existing facts of J-6, and it cannot be voted on.
3. The moderator restores a hidden item. It counts again, with the votes it still has.

Branches:

- A person without the moderator role, logged in or not. The view cannot be opened.
- The role is removed by the team. The next request of that account to the view is denied, even when its session is still active.
- A flag cannot be dismissed. A flagged item that is not hidden stays in the view.

Ends: content that should not be public is hidden for everyone, and a wrong hiding can be undone.

Rests on: M11; FR-14; AC-13.

## J-11. The account

For: anyone who wants an account. Nothing in the main scenario needs one.

Creating an account:

1. The person opens the account and chooses to create one.
2. The person gives a pseudonym and a password. The app asks for no email address and nothing about a disability, and says that a forgotten password cannot be recovered.
3. The app creates the account, and the person is logged in.

- The pseudonym has 3 to 30 characters - letters, the Polish ones included, digits, the underscore and the hyphen - and is unique without regard to letter case. When it is taken or breaks a rule, the app says which.
- The password has at least 5 characters and may hold any printable characters, spaces included. When it is too short, the app says so.

Logging in and out:

1. The person gives the pseudonym and the password. The app logs the person in.
2. The person stays logged in for 24 hours after their last activity, also after closing and reopening the browser.
3. The person logs out. The app logs them out in this browser.

- A wrong pseudonym or password. The app says that the two do not match, without saying which.
- The session ended. The next action of the person is handled as without an account, and the app shows that they are not logged in.
- What changes after logging in. Contributions count as made from an account. The app says nothing about their weight, shows nothing about the account to other people, and keeps the needs on the device, apart from the account.

Deleting the account:

1. The person chooses to delete the account.
2. The app says what is removed - the account and the pseudonym - and what stays - the reports and the votes, detached from the person.
3. The person confirms once; the password is not asked again. The app deletes the account and logs the person out. The pseudonym can be taken again.

Ends: an account exists, is in use, or is gone without a trace of the pseudonym, while the facts it confirmed keep their statuses.

Rests on: M9; FR-12, FR-13; AC-11.

## J-12. Reading the privacy information

For: anyone.

Starts: any place of the app.

1. The person opens the privacy information.
2. The app states, in the language of the interface, what it keeps, for what purpose and for how long: the pseudonym and the password of an account, and the identifier of a vote without an account, for 30 days, which is pseudonymized personal data. It states what it does not keep: the needs, the current location, an email address and any information about a disability. In the hosted demo it also states that the demo and all its data are deleted on 4 October 2026, after the results are announced.

Ends: the person knows what the app knows about them.

Rests on: the section Personal data of the specification; FR-20; AC-19.

## J-13. Switching the language

For: anyone.

Starts: any place of the app. The first language is the one of the browser, Polish or English.

1. The person uses the language switch.
2. The app shows every text in the other language. What the person was doing stays as it was: a planned route stays on the screen and is not planned again, and a report in progress keeps its steps.

Ends: the same screen in the other language.

Rests on: FR-19; AC-18.

## J-14. The main scenario with a keyboard alone and with a screen reader

For: a person who does not use a pointer or does not see the screen. This is not a separate path through the app: it is J-1, J-4, J-5, J-6 and J-8 done without a pointer, and what has to hold at each of them.

1. Setting the needs (J-1). The presets and every item are reached with the keyboard and announced with their name and whether they are set.
2. Planning the route (J-4). The search field, its submission, the list of matches and the picking work with the keyboard; the number of matches is announced. A point on the map is never the only way to give a place.
3. Reading the result (J-5). The summary and the list carry everything the map shows: the state of every segment in words, the missing attributes, every fact with its source, date and status. The map is one stop in the order of focus and can be left with the keyboard.
4. Reporting (J-6). The point is set by moving the map under a fixed mark with the arrow keys; the type, the optional fields, the existing facts and the summary are reached and announced in order.
5. Voting (J-8). The two answers are reached with the keyboard, the status after the vote is announced, and inactive vote controls say why they are inactive.

Ends: the main scenario is completed without a pointer, and what works and what does not is recorded, as the Kraków brief asks.

Rests on: M10; FR-16; AC-15.

## The path of the demo for the Kraków jury

The brief asks the demo to state the needs of the chosen group, check a route, show where the information comes from, show a case of contradictory or incomplete data or an unavailable source, and check the accessibility of the main scenario. The journeys above cover it in this order:

1. The needs of the group: J-1 with the preset "I use a wheelchair".
2. A route in the district of the Tauron Arena: J-4 and J-5, with the sample reports and geozones marked as sample data.
3. Source, date and status of the facts on the route: J-5 and the fact detail of J-8.
4. Contradictory data: the branch of J-5 where a report contradicts OpenStreetMap, then one more confirmation in J-8, after which the route is planned again and avoids the place.
5. Incomplete data: the segments in the states partial data and no data, with their missing attributes.
6. An unavailable source: the branch of J-4 where routing does not answer.
7. The accessibility check: J-14.

How the live demo makes routing unavailable is not decided yet; it belongs to the task `DEPLOYMENT` of `plans/demo_environment/`.

## Decisions behind the journeys

Decided by the user, the frontend person of the team, on 2026-10-03, question by question, and part of version 6 of the specification:

1. The app opens on the map of facts, which shows the facts of the profile; facts can be opened, voted on and reported without a route (M4).
2. A profile without any barrier is allowed; its route has no segment states and is drawn in a neutral style (M1, M7, M8).
3. A change of the profile plans a shown route again (M1, M2).
4. A point or a location outside Kraków is refused with a plain message; a refused location leaves the address and the map (M2).
5. The place of an item is the street name from OpenStreetMap and the distance from the start (M8).
6. An outdated fact is shown nowhere (M4).
7. During reporting the location only moves the map, in the browser (M3).
8. A report far from every way is saved and shown, and the summary does not mention it (M3).
9. A geozone can carry an optional description; it has no check for existing geozones (M5).
10. The app shows a person their own vote, and the vote controls are inactive for a day after it (M4).
11. The app says nothing about the weight of an account; a pseudonym has 3 to 30 characters of letters, digits, the underscore and the hyphen; deleting an account takes one confirmation, without the password (M9).
12. A flag has no reason and takes one confirmation (M11).
13. The map of facts has a switch between the facts of the profile and every fact (M4).
14. The first opening shows the needs screen, which can be skipped (M1).
15. Reporting has one entry, with the choice of a barrier, an amenity or an area (M3, M5).
16. The user approved these rules alone and had them written into the specification as version 6.
17. The journeys are written directly into this file, without the chain `plan-shape`.
18. A vote or a report of the person, saved while a route is shown, plans the route again (M2).

Proposed by the agent and accepted with the journeys, not asked one by one:

- With a profile without any item the map of facts shows every fact (M4).
- Outdated facts are left out of the check for existing facts of a report (M3).
- The facts of the map of facts are also available as a list (M4, from M10).
- After an account is created the person is logged in, and a failed login does not say whether the pseudonym or the password was wrong. Neither is in the specification; both are for the contract of the programming interface to confirm.
- The chosen language is remembered on the device, and a planned route is not kept after the app is closed. Neither is in the specification.

## What stays open

Where the date of the OpenStreetMap copy stands and how a moderator reaches the moderator view were open when the journeys were written; both are settled in `docs/product/views.md`. Still open, and blocking neither document:

- the wording of the messages and of every label, in Polish and in English, and the Polish names of the terms of the specification,
- the name of the product,
- the look of every screen, the route result apart, whose direction is in `.impeccable/briefs/route-result.md`.

Five rules of version 6 change work owned by other people and wait for their confirmation: the description of a geozone and the rules of a pseudonym (`plans/fact_schema/`), and the own vote, the street name of an item and outdated facts left out of every reading (`plans/api_contract/`).
