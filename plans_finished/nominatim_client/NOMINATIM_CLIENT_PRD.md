# PRD: Check of the public Nominatim instance against the decisions of the address search

Document state: 2026-10-04, corrected in phase B: the facts checked are F-1 - F-8 with the policies of F-10 and F-11, against the decisions D-4 - D-10

## Business goal

The address search of `docs/product/specification.md` M2 and M5 gives the start and the destination of a route and the point of a geozone, and the demo at the Tauron Arena starts from it. The work package of `plans_finished/mvp/` that builds it follows decisions resting on facts checked once, by hand, from one machine, on 2026-10-03 (`plans_finished/geocoding/GEOCODING_PLAN.md` F-1 - F-8, F-10, F-11). This initiative gives that work package facts checked again against the live public instance, real responses to test against without the network, and a way to repeat the check before the demo, so that the search works at the demo as it was decided.

## Problem and its consequences

The decisions of the search - how the text is cleaned, which results count as Kraków, how a match is labelled, when a cached answer is reused and how long the search waits (`GEOCODING_PLAN.md` D-4 - D-10) - hold only as long as the public instance answers as it did on 2026-10-03. If it answers differently, for example a stop name finds nothing or the letter case changes the result, the code built on those decisions fails at the demo, and nobody learns it before a jury member types the text.

The tests of the search run without the network (`GEOCODING_PLAN.md` F-18). Written against invented responses, they can pass while a real response breaks the label of a match, for example a result without a street or a postcode (F-7 there).

Without a repeatable check, finding out on the day of the demo whether the instance still answers as recorded means writing the check again under time pressure, with the risk of exceeding the limits of the instance and getting the team machine blocked.

## Scope

- A check of the live public Nominatim instance from a machine of the team against the decisions D-4 - D-10 of `plans_finished/geocoding/GEOCODING_PLAN.md`: the facts about the answers of the instance, F-1 - F-8, again, and new cases.
- A new reading of the usage policy and the privacy policy behind F-10 and F-11 there.
- Recorded real responses of the instance, as material for the tests of the work package of `plans_finished/mvp/` that builds the search.
- A tool that repeats the check, kept with this initiative.
- Carrying the confirmed or corrected decisions into `plans_finished/mvp/MVP_PLAN.md` D-3, after the ruling of the user and the external API person.

## Out of scope

- Writing the interface to Nominatim. It stays with a work package of `plans_finished/mvp/`, with the names of its modules and the structure of the operations decided by Q-11 of `plans_finished/mvp/MVP_PLAN.md`. Decided by the user in the shape interview, because writing it here would decide a part of Q-11 before its initiative exists.
- The automated tests of the search. They are written with its code in the work package of `plans_finished/mvp/` (`GEOCODING_PLAN.md` D-16); this initiative only gives them recorded responses.
- The choice of the search service and the product rules of the search, settled by `plans_finished/geocoding/` and `docs/product/specification.md` M2, Address search.
- A check from the server of the demo whether its address is blocked by the public instance. It stays the manual check after the first deployment of `GEOCODING_PLAN.md` D-16. Decided by the user in the shape interview.
- Changing the archived artifacts of `plans_finished/geocoding/`; a correction lives in this initiative and in `plans_finished/mvp/MVP_PLAN.md` D-3.
- The routing engine named in the seed, which differs from `plans_finished/routing_engine/`; it does not touch the search.
- The fact F-9 of `GEOCODING_PLAN.md`, about the public Photon instance: it concerns the alternative rejected in D-1 there, not a decision the MVP builds on. Decided by the user on 2026-10-04, in phase B, against checking it with requests to that service.
- The licence of the repository, an open entry of `docs/standards/decision_registry.md`.

## Functional requirements

FR-1. Check of the live instance. One run checks again each of the facts about the answers of the instance, F-1 - F-8 of `GEOCODING_PLAN.md`, and the new cases: a name of a public transport stop, the same name in a different letter case, a text with a postcode, a text that matches nothing, and a typo in a name. The pages of the usage policy and of the privacy policy behind F-10 and F-11 there are read again outside the run; this reading sends no search and does not count toward the limits of FR-2. The result is a list of facts dated with the day of the check, each marked as confirming or contradicting a named decision of D-4 - D-10 there.

FR-2. Limits of a run. A run sends at most 40 texts, each once, at most one request per 1.1 seconds, and identifies the application as the search itself does (D-5 there). A refusal for an exceeded limit or a blocked address, or no answer within 5 seconds, stops the run at once: nothing is retried, and the remaining texts are not sent. Another run starts only by the decision of a person.

FR-3. Recorded responses. Every response of a run is recorded together with its text, its status, its time and the licence statement the response carries, and is kept with this initiative as material for the tests of the search in `plans_finished/mvp/`. A refusal that stopped a run is recorded too.

FR-4. A repeatable check. A member of the team can run the check again, for example on the day of the demo, under the limits of FR-2, from the instructions kept with this initiative, without writing anything. The check runs only by hand; no test and no automatic check of the repository sends a request to the instance.

FR-5. Contradictions. A fact that contradicts a decision of `plans_finished/geocoding/` is shown to the user and the external API person, and the decision changes only by their ruling. A changed decision is carried into `plans_finished/mvp/MVP_PLAN.md` D-3, and `plans_finished/geocoding/` stays unchanged.

FR-6. Searched texts. The texts of the check are names of public places and addresses of public buildings, never an address tied to a person.

## Acceptance criteria

AC-1 (FR-1). After a full run and the reading of the policies, each of F-1 - F-8, F-10 and F-11 and each of the five new cases has a dated fact that names the decision it concerns and says whether it confirms or contradicts it.

AC-2 (FR-2). In a full run of 40 texts, the recorded times show 40 requests, no two of them started less than 1.1 seconds apart. When the instance refuses the twelfth text, the twelfth request is the last one sent, and 11 responses and the refusal are recorded.

AC-3 (FR-3). Every request sent by a run has a recording with its text, its status, its time and, for a response with results, its licence statement; nothing is recorded for a text that was not sent.

AC-4 (FR-4). A member of the team who did not take part in this initiative repeats the check from the instructions kept with it without changing any file of the repository other than the recordings of the run. The tests and the automatic checks of the repository send no request to the instance.

AC-5 (FR-5). Every fact that contradicts a decision has a recorded ruling of the user and the external API person before `plans_finished/mvp/MVP_PLAN.md` D-3 changes, and the files of `plans_finished/geocoding/` have no change.

AC-6 (FR-6). Every text of the list of a run is the name of a public place or the address of a public building.

## Domain rules

The rules are those of the section Domain rules of `plans_finished/nominatim_client/NOMINATIM_CLIENT_SHAPE.md`. In short, for reading the acceptance criteria:

- The decisions of `plans_finished/geocoding/GEOCODING_PLAN.md` D-1 - D-16 and the product rules of `docs/product/specification.md` M2, Address search, apply as decided; this initiative checks them and does not change them on its own.
- A run is small and slow on purpose: at most 40 texts, at most one request per 1.1 seconds, each text once, no retry, a stop at the first refusal.
- The check runs only by hand.
- The searched texts are never of a person, so their recording breaks no rule on the searched text.

## Dependencies and impact on other modules

- No product code exists, so nothing in the repository changes indirectly.
- `plans_finished/mvp/MVP_PLAN.md` D-3 receives the confirmed or corrected decisions; the work package of `plans_finished/mvp/` that builds the search receives the recorded responses for its tests.
- Q-11 of `plans_finished/mvp/MVP_PLAN.md`, decided in a separate initiative not yet set up, decides the code that uses these results; this initiative does not wait for it.
- `plans_finished/geocoding/` is read and never changed.
- The usage policy of the public instance (`GEOCODING_PLAN.md` F-10) bounds every run.
- `docs/standards/standard_formatting.md` applies to a copy of someone else's document kept with an initiative, which the recorded responses are.
- `docs/standards/decision_registry.md`, the open entry on the licence of the repository, is touched by keeping OpenStreetMap data in the public repository.

## Risks and notes

- Time: the Kraków submission closes at 11:00 on 4 October 2026, the date of this document. A correction found after the search work package has started lands in code already written, so the check is useful only before that work package, or as the check on the day of the demo of FR-4.
- The public instance may block the team machine after a refusal; the stop of FR-2 limits the damage but does not rule it out, and the same machine may be needed for development.
- The check runs from a team machine, not from the server of the demo, so it says nothing about whether the server is blocked; that stays with `GEOCODING_PLAN.md` D-16.
- The instance may change between the check and the demo; FR-4 exists for that.
- The recorded responses are OpenStreetMap data under the ODbL; they keep their licence statement, but keeping them in a public repository touches the open entry on the licence of the repository, which this initiative does not settle.
- A name in OpenStreetMap may hold a character that `docs/standards/standard_formatting.md` forbids; then the user chooses how the copy is handled.
- When this initiative is archived, its directory moves to `plans_finished/`; the work package of the search should not depend on where the recordings lie.
- The answers of the shape interview were given by the user; the ruling of the external API person on them is still to be confirmed.
