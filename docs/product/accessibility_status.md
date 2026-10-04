# Accessibility status of the web frontend

Document state: 2026-10-04

## Why this document exists

The Kraków brief asks for an app whose main scenario works with a keyboard and a screen reader, and `plans/frontend_app/FRONTEND_APP_PRD.md`, FR-14, asks for a written list of what works and what does not. This is that list for the web frontend in `frontend/`, as it stood on 2026-10-04. It records what was checked, how, and by whom, so that the team and the jury read facts and not a claim of conformance. Nothing here says that the frontend conforms to WCAG 2.2; only the checks named below were made.

## What was checked and how

All checks were made by the agent that built the frontend, in a browser at a width of 360 px, on the temporary mock of the service, in Polish and in English.

- Keyboard: the order of the focus was read with the Tab key on the map of facts, and the main scenario - the needs, a route by the address search, the route result, the detail of a fact with a vote - was run with the keys and with clicks on the elements the keys reach. The address search was sent with the Enter key, and the map was moved with the arrow keys.
- Linter: every rule of the plugin `jsx-a11y` of oxlint is an error in `frontend/.oxlintrc.json`, and the code passes.
- Contrast: computed from the colors of the theme and of the map style with the formula of WCAG 2.2. The ratios are in the table below.
- Segment states without color: a screenshot of the route result in grayscale. The four states are told apart in the legend, on the summary line and on the map by their patterns: stripes, a solid line, dark dashes on a light line, and dots.
- Not checked: a screen reader. The check of the main scenario with a screen reader on a phone is a step of a human and was not made yet.

## What works

- Every view has one main heading, and after a change of the view the focus moves to that heading or to the view.
- The order of the focus is the header, the view and the bottom bar. In a map view the map is reached once, with its two zoom buttons and the link of the attribution, and the Tab key leaves it for the panel.
- Everything the map shows is also text in the panel under it: the facts of the map of facts as a list, the route as a text of its stretches in order, as three numbers and as the list in three groups.
- The four segment states have each their own line pattern and their own name in the legend. A route that is not assessed has a fifth style, a hollow line, and the view says so in words.
- The status of a fact is a word with an icon. The sample data mark and the source are words.
- Every control is a button, a link, a checkbox or a labelled field with a text name. The hint and the error of a field are tied to it, an error is announced when it appears, and a change of state - a loading list, a saved vote, the number of search results - stands in a status region.
- The map can be moved with the arrow keys and zoomed with its two buttons, which have a text name in both languages, so no action needs a pinch or a drag.
- A point is picked by moving the map under a fixed mark, with touch or with the arrow keys, and confirmed with a button. Both views that pick a point, for a route and for a report, have a control that moves the focus to the map.
- Both languages have every text, the page states its language, and the switch changes the language without losing a planned route.
- The texts and the controls keep the contrast ratios of the table below.

## What does not work or is limited

- The start of a route from the current location does not work on the hosted demo. The demo is served over plain HTTP, and a browser gives no location to a page served that way; the view then says that the location is not available and offers the address search and the point on the map. The same holds for the action that moves the map to the location while reporting.
- The check with a screen reader on a phone was not made. Until it is, the behavior of the status regions and of the focus after a change of the view with a screen reader is not known.
- The markers of the map are left out of the order of the Tab key. They have a text name and react to a pointer; a person who uses a keyboard opens a fact from the list.
- The names of the streets are not in the list rows, because the service gives none. A screen reader user tells two facts of one type apart by the distance on a route and by nothing on the map of facts.
- The state partial data has an amber line whose contrast against the white edge of the route is 2.27 to 1, below the 3 to 1 of a graphic. The state is carried by its dark dashes, which have 8.15 to 1 against the amber and 18.47 to 1 against white.
- A label of a stop on the summary line of the route is left out when it would run into the label before it. The barrier is still named in the text of the stretches and in the list.
- The sizes of the texts are set in pixels. The zoom of the browser enlarges them; a setting of the browser that changes only the default size of text does not.
- The map needs WebGL. On a device without it a message stands in place of the map, the lists and the forms work, and a point cannot be picked on the map.
- On a desktop browser the app is one column up to 520 px wide. It does not break and is not tuned.
- Routes with public transport, the optional feature O9, are not built: `docs/product/api_contract.md` has no interface for them.

## Contrast ratios

| Pair                                                      | Ratio |
| --------------------------------------------------------- | ----- |
| Text `#111418` on the page ground `#F4F5F2`               | 16.88 |
| Text `#111418` on white                                   | 18.47 |
| Second text `#4B5058` on white                            | 8.12  |
| Second text `#4B5058` on the page ground                  | 7.42  |
| White on the navy `#12306B` of the header and the buttons | 12.64 |
| Navy `#12306B` links and outlined buttons on white        | 12.64 |
| Text `#111418` on the yellow `#FFD400`                    | 12.90 |
| Yellow `#FFD400` number on navy                           | 8.83  |
| Status confirmed `#1E7A46` on white                       | 5.35  |
| Status disputed `#8A5A00` on white                        | 5.93  |
| Error text `#C8321E` on white                             | 5.34  |
| Inactive button text `#5A5F67` on `#EEF0EC`               | 5.60  |
| Names of streets `#4B5058` on the map ground `#ECECE3`    | 6.83  |
| Names of streets `#4B5058` on a park `#D3E1CB`            | 5.95  |
| Segment barrier `#C8321E` against the white edge          | 5.34  |
| Segment no barrier `#1E7A46` against the white edge       | 5.35  |
| Segment no data `#6F7480` against the white edge          | 4.68  |
| Segment partial data `#E0A100` against the white edge     | 2.27  |
| Dashes `#111418` of partial data against its amber        | 8.15  |
| Neutral route `#12306B` against the map ground            | 10.64 |
