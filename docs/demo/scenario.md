# EnableMe demo scenario

Document state: 2026-10-04, scenario written; real placements and runtime verification pending

## Purpose and authorities

This is the scenario for checks 7.2 and 7.3 of `FINAL_CHECKLIST.md`. It demonstrates a wheelchair user's walking journey in Czyżyny, the source and reliability of concrete facts, incomplete data and a contradiction changed by one confirmation. The intended running time is 2 minutes 40 seconds, before the final pitch length is known.

`docs/product/specification.md` is the product authority. This scenario implements the approved `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_PRD.md` and the decisions of its closed shape. It replaces the draft as the runbook; the draft remains a historical proposal. Actual results belong in `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_REVIEW.md`, not in this procedure.

The numbered views below are defined in `docs/product/views.md`; text keys are in `docs/product/interface_texts.md`. MVP AC references point to `plans_finished/mvp/MVP_PRD.md`, read with the current specification where older criteria differ. K-1 means the working demo for the chosen group; K-2 means sources, dates, reliability and sample marks; K-3 means contradictory or incomplete data. These are the validation items of `docs/hackathon/challenge_requirements.md`, section Validation during the presentation. Its accessibility item is checked separately by check 6.5, and its prototype-to-service plan belongs to the presentation materials.

## Before a run

- Establish whether the application is local or hosted. Obtain its address outside the repository and record only the environment kind and application revision in results.
- Confirm that the web client talks to the real backend. A development frontend defaults to a mock proxy unless its launch configuration says otherwise; a working mock screen is not a passed hosted check.
- Confirm checks 7.1, 6.1, 6.2 and 3.3: the application is running, route screens work, sources and statuses are shown, and the prepared sample data is loaded. Read the current checklist rather than assuming previous measurements still hold.
- Mateusz verifies O-1 - O-4 and the sample placements below. Keep them unverified until their evidence is available. If the destination changes, use the chosen replacement in both searches and every affected scene.
- Confirm that S-5 is unverified with confirmation weight 1.5 and no denials, and that the presenter is eligible to confirm it without an account. Weights are not displayed by the app; use Mateusz's preparation record to establish the total, without querying personal vote identities from the hosted database.
- Use an unsigned-in browser and the Polish interface. Open Needs explicitly if this device has already passed first opening. Do not erase stored browser vote history to try to bypass a backend vote limit.
- For a hosted rehearsal, announce that the run stops after scene 6. No confirmation or other contribution is submitted there before the pitch. The local rehearsal uses separate data.

If a prerequisite is unavailable, record the relevant runtime checks as unperformed with that reason. Writing this scenario does not establish their result.

## Timed main run

### Scene 1. Set the needs, 0:00-0:15

In V-2 Needs, select `needs.preset.wheelchair` and finish setting the profile. Verify all five barriers: stairs, high kerb, poor surface, steep incline and narrow passage. The needed amenities are elevator, ramp, lowered kerb and accessible toilet. Rest place and handrail are not selected by this preset.

Explain that the application keeps barrier and amenity preferences on the device, without asking for a disability or tying them to an account. Do not add a profile-without-barriers scene.

Traceability: MVP AC-1 for the preset behavior under M1; K-1; stage7 PRD AC-1 and AC-2. This scene does not settle the whole MVP profile criterion.

### Scene 2. Show the map and legend, 0:15-0:30

In V-3 Map of facts, open V-9 Legend. Show the sample marks on S-1, S-3 and the poor-surface area S-4; the area must be visible as an area. Show the date of the imported map-data copy and the OpenStreetMap attribution. Explain that user reports and areas used for this run are prepared sample data.

On the map without a route, the legend need not show segment states; show those with scene 4's route result. The legend explains the sample mark and gives access to the page about the data.

Traceability: MVP AC-8 and AC-17; K-2; stage7 PRD AC-2.

### Scene 3. Choose the route endpoints, 0:30-0:50

In V-4 Route planning and its V-8 Address search, submit Tauron Arena for the start and Ogród Doświadczeń for the destination, or Mateusz's recorded replacement destination. Select the full-address item from each result list. A single match is still selected explicitly; typing alone must not set a point.

Ask for a walking route with the profile from scene 1. Explain that current location is unavailable on the hosted link and that this demonstration therefore starts from an address. An unavailable search is a failed or blocked scene, not permission to silently replace the address flow with invented points.

Traceability: MVP AC-2, address portion; K-1; stage7 PRD AC-3.

### Scene 4. Read the route, 0:50-1:20

In V-5 Route result, read the summary: barriers from the profile, distance without data and route length. Open the route legend and identify the four assessed segment states using their names and line patterns as well as color. Scroll the three list groups; the additional-barrier group can be empty because the wheelchair preset avoids every barrier type.

Show S-2, the unverified four-step report, on a barrier segment. Show the offered alternative with its reason naming stairs and the unverified status, without selecting an alternative that would remove the later S-5 crossing from the displayed route. Show S-3 as an amenity in the list and that the displayed route goes around the matching disputed geozone S-4.

Verify these behaviors against the prepared route. If the placement makes an expected scene impossible, record that failure and return the placement requirement to Mateusz; do not describe the intended result as observed.

Traceability: MVP AC-2, AC-3, AC-9 and AC-10; K-1 and K-2; stage7 PRD AC-2 and AC-4.

### Scene 5. Read the facts, 1:20-1:40

From the route list, open S-2 in V-6 Fact detail. Show stairs, four steps, its bundled description about the missing right-hand handrail, the user-report source, its date, unverified status and sample mark. Close it and open the verified O-2 map-data fact.

O-2 shows map data as its source and the calendar day of its last OpenStreetMap edit. Its status is the status of the actual fact; do not assume that map origin means confirmed. Distinguish the fact's date from the date of the imported copy shown in scene 2.

Traceability: MVP AC-14 and AC-17; K-2; stage7 PRD AC-7.

### Scene 6. Explain incomplete data, 1:40-1:55

In V-5, point to the straight connections between the chosen endpoints and the pedestrian network, shown as no data, and to the partial-data stretch verified as O-3. Read the summary's distance without data and the plain note `route.no_data_note`.

The note names no missing attributes. None of these stretches is presented as free of barriers. If all assessed stretches lack complete data, explain why the route is mostly partial data while the legend still explains the four possible states.

Traceability: MVP AC-9 and AC-10 as read under M8; K-3; stage7 PRD AC-9. The hosted rehearsal ends here, without a vote.

### Scene 7. Resolve the contradiction, 1:55-2:25

This is a local rehearsal scene or the hosted pitch contribution. It is never part of an earlier hosted rehearsal.

From the still-displayed route, open S-5 in V-6. Before the vote, show the unverified high kerb report and `fact.contradiction`: map data describes a lowered kerb at the same crossing. The segment follows map data with the unverified-report icon; incomplete data may still prevent it from being green.

Confirm that the barrier is still there, without an account. Accept only an observed successful save: S-5 becomes confirmed, `route.replanning` appears and the new route avoids the crossing. The preparation total of 1.5 plus one anonymous confirmation of 0.5 gives the threshold 2. The presenter does not need to display vote weights or any voter identity.

If the vote is refused as already cast today, the scene has not passed. Do not retry through a changed identity. If the vote succeeds but the route does not change, record the status and route results separately instead of claiming completion.

Traceability: MVP AC-6, relevant confirmation behavior, and AC-9; K-2 and K-3; stage7 PRD AC-8 and AC-12.

### Scene 8. Show the data explanation, 2:25-2:35

Open V-13 About the data through the menu or legend. Show sources, the imported copy's date, the reliability statuses in words, how sample data is marked and the explanation that missing data never confirms accessibility. Explain how reports and votes help correct what is known.

Traceability: MVP AC-14; K-2; stage7 PRD AC-11 and AC-16. This read-only scene can also be checked separately after a rehearsal that stops before scene 7.

### Scene 9. Close with the limits, 2:35-2:40

State that the sample reports are demonstration content, the real map facts come from the dated copy, and the demo and its data are removed by their owner after the results on 4 October 2026. Point to the separate local unavailable-routing evidence and separate accessibility check if the pitch needs them. Their verification is not replaced by this closing statement.

Traceability: K-2 and K-3, with separate evidence for the accessibility validation; stage7 PRD AC-11. The scene durations total 160 seconds and remain estimates until rehearsal measures them.

## Sample facts for Mateusz

The source of sample content is `mobile_app/accessway/entry/src/main/ets/data/DemoSeed.ets`, function `demoReports`. Preserve its original descriptions, including their Polish user-content wording. Preserve the stable identifiers listed below. Its schematic coordinates are not real-world placement evidence: choose real placements from the imported copy and record which verified route they serve.

All eight facts are marked sample data. Their reliability comes from votes under M4, using distinct sample voting identities and the latest votes of the five most recent persons. Dates follow Europe/Warsaw and the bundled pattern, approximately 0.1 - 2 days before preparation. The exact storage, dates and repeated-load behavior belong to Mateusz's sample-data initiative. Never reserve the presenter's IP and User-Agent pair as a sample voting identity.

### S-1. Confirmed high kerb

Source identifier: `demo-kerb-lema`. Point report, high kerb, no description. Prepare two confirmations of weight 1, total 2, no denials. Place it at a crossing near the Tauron Arena, off the selected route so that the route can avoid it. Real placement remains unverified.

### S-2. Unverified stairs

Source identifier: `demo-stairs-pokoju`. Point report, stairs, four steps, the original description about the missing right-hand handrail. Prepare one confirmation of weight 1, no denials. Place it within 15 m of the selected pedestrian stretch, where map data does not explicitly give the stairs, with a real path around it. Prefer al. Pokoju when the verified route permits it. Real placement and alternative remain unverified.

### S-3. Confirmed ramp

Source identifier: `demo-ramp-park`. Point report, ramp, no description. Prepare two confirmations of weight 1, total 2, no denials. Place it within 50 m of the displayed route near the park entrance, so the profile's amenity group includes it. Real placement remains unverified.

### S-4. Disputed poor-surface area

Source identifier: `demo-area-surface`. Geozone, poor surface, radius 25 m, the original pavement-renovation description. Prepare one confirmation and one denial of weight 1 each, giving disputed. Place it beside the shortest path so that a matching wheelchair route goes around it, with neither endpoint inside it. Real placement and effect on the route remain unverified.

### S-5. Contradicted high kerb before the demonstration vote

Source identifier: `demo-kerb-medweckiego`. Point report, high kerb, no description. Prepare confirmation weight 1.5 and no denials, using one confirmation of weight 1 and another distinct person's confirmation of weight 0.5. This is the agreed departure from the bundled demo's weight 1.

Place it within 5 m of O-1 on the same pedestrian stretch, at a crossing used by the displayed route before the vote. A route around that crossing must be available once the report is confirmed. Its source identifier does not establish its street: the bundled content currently names Stanisława Lema. Real placement remains unverified.

### S-6. Flagged stairs

Source identifier: `demo-flag-stairs`. Point report, stairs, three steps, the original description with a surname placeholder, not a real person's name. Prepare one confirmation of weight 1, giving unverified, and mark it flagged. Place it off the demonstration route. Flagging alone does not hide it. Real placement remains unverified.

### S-7. Flagged narrow-passage area

Source identifier: `demo-flag-area`. Geozone, narrow passage, radius 50 m, the original scaffolding description. Prepare one confirmation and one denial of weight 1 each, giving disputed, and mark it flagged. Place it off the demonstration route, near ul. Medweckiego if compatible with the imported copy. Real placement remains unverified.

### S-8. Hidden high kerb

Source identifier: `demo-hidden-kerb`. Point report, high kerb, the original placeholder description mentioning a hidden phone-number text without containing an actual phone number. Prepare one confirmation of weight 1, giving unverified, and mark it flagged and hidden. It appears neither on the public map nor in the route list and changes no route. Real placement remains unverified.

## Real map-data requirements

O-1. A real lowered-kerb fact from OpenStreetMap at the crossing used for S-5. Record its element and pedestrian stretch, S-5's same-stretch relationship and distance of at most 5 m, and the route's use of the crossing before confirmation. Status: unverified.

O-2. A real map-data fact on the displayed route or within 50 m of it, available from the route list, with its last-edit date. A lowered kerb in the amenities group is suitable if the actual route lists it. Status: unverified.

O-3. At least one actual stretch of the displayed route with partial data for the wheelchair preset. Record where it appears and whether any stretches have complete data. The no-data connectors do not establish that a partial-data stretch exists. Status: unverified.

O-4. Actual submitted-search matches for Tauron Arena and Ogród Doświadczeń, or the documented replacement destination, with full addresses in Kraków. Status: unverified.

Mateusz checks these against the imported copy and running service. If the default route lacks O-1 or an alternative around S-2, he chooses another destination in Czyżyny with both and records its name, the supporting map data and the affected sample placements. Apply that change to the searches and handover before the run. Do not substitute a fabricated OpenStreetMap fact.

Street-name delivery is deliberately deferred in `docs/standards/decision_registry.md`, entry Street name of an item of a list. The scenario does not require a new street field or infer one from a sample identifier; the route list can identify an item by its distance under the existing contract.

## Hosted rehearsal and preservation

Run scenes 1 - 6 on the real hosted application. Stop before scene 7's vote. The page about the data may be read separately without contributing. Record measured scene times and results, and leave S-5 unverified at the initial confirmation total 1.5.

Keep the hosted sample data untouched between preparation and the pitch. Do not distribute the link before the pitch; the optional demo-link field of the Kraków submission remains empty then. Those submission and sharing actions are performed by humans.

Preserve any existing browser vote history. In the accepted demo identity model, a fresh browser is not necessarily a new person: an identical IP and User-Agent shares the same daily limit. A local vote is safe for hosted preservation only when the local environment uses its own data and is positively identified as local.

## Local confirmation rehearsal

Use the same application revision and verified demo placements in a separate local environment. Verify S-5's initial state and voting eligibility before the exercise. Follow scenes 1 - 7, observe the accepted confirmation, confirmed status and actual route avoiding the crossing, then optionally finish scenes 8 - 9.

Record the scene timings and whether the original route, proposed alternative and post-confirmation route match the required scenes. Local success establishes local evidence only. It does not consume the hosted vote or establish that the hosted scene passed.

A second local take requires another preparation of local data by its owner; this runbook adds no reset command and never withdraws or deletes a vote. Do not run any preparation against the hosted data to repeat a local rehearsal.

## Local unavailable-routing exercise

Begin only when the real local application, demo data and routing are ready and the local routing service and its delivered stop/start commands are positively identified. Record the normal route first. Do not guess a container name, simulate this through the mock service or stop any hosted service.

1. Stop only the local routing engine with the local setup's delivered command.
2. Submit the scene 3 route in the web client, with the same chosen start, destination and profile.
3. Verify `plan.unavailable.title` and its explanation, with no route shown. Keep a screenshot or a short clip without identifying request data or a hosted address.
4. Restore the local routing engine with the delivered command even if the check failed.
5. Submit the route again and record that local routing has recovered.

If the local service cannot be positively identified, record this exercise as unperformed. Its evidence remains separate from the hosted contradiction and incomplete-data scenes. Adrian decides whether the captured view belongs in the deck.

## Early hosted vote and recovery

If S-5 receives a hosted vote before the pitch, record that the original contradiction scene is no longer ready. Do not claim that a changed browser restores its initial status or that deleting browser history resets the server.

Only the server owner restores hosted data according to `docs/deployment/hosted_demo.md`. The agent does not perform a reset. Restoration may require loading the imported copy again and may take up to 60 minutes. After the human restoration, recheck the copy date, the sample placements, S-5 at weight 1.5 without denials and the presenter's eligibility before declaring the scene ready again.

## Limitations and separate checks

- Current location is unavailable on the hosted link; this run uses submitted address searches.
- Hosted routing is not stopped for demonstration. Unavailable routing is checked in the separate local exercise.
- All user reports and areas used here are sample data, marked as such. Map-data facts remain real facts of the imported copy, with their dates and actual reliability statuses.
- The demo and its data are removed by their owner on 4 October 2026 after the results. This scenario contains no deletion procedure.
- The basic accessibility assessment is check 6.5. The timed scenario does not certify keyboard, screen-reader or contrast compliance; the pitch decides whether to show a short keyboard pass separately.
- New reporting, accounts, moderation, a profile without barriers, the route without a barrier-free alternative and public transport are outside the timed scenario.

## Handover

Mateusz receives the Sample facts and Real map-data requirements sections for check 3.3, including the initial S-5 total and the rule for choosing another destination. Adrian receives the Timed main run and Limitations sections as input to the Polish video and deck, with the distinction between real hosted evidence and an on-device demonstration. Kuber receives the S-5 difference and any changed destination to decide whether the HarmonyOS sample follows them. Rafał receives the run results for checks 7.2 and 7.3 and the measured timings for the pitch with Adrian.

The material is prepared here; acceptance by each recipient remains pending until actually received. This document sends no message to a team member and decides no recording choice.

## Recording a result

Append observations to `plans/stage7_demo_scenario/STAGE7_DEMO_SCENARIO_REVIEW.md`. Record the date, application revision, local or hosted environment kind, prerequisite state, verified destination and data items, scene, actual duration, visible result and acceptance criterion.

Use passed only for an observed successful scene, failed for an observed mismatch, and unperformed for missing runtime evidence, with its reason. Record documentary completion separately. Before screenshots or clips enter the repository, remove addresses, secrets, raw IP, User-Agent, voter identifiers and any personal data. Record an external evidence reference without an address when sanitization is not possible.

A complete hosted result needs the real contribution at the pitch and the route change, as well as the read-only scenes. A full local rehearsal, a mock demonstration or written expected outputs cannot close hosted checks 7.2 and 7.3. Keep the initiative active until its result record supports their actual completion.
