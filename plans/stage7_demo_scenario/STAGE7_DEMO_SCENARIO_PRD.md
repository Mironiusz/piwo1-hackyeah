# PRD: Demo scenario and its run on the hosted demo

Document state: 2026-10-04, approved by the user; planning and execution authorized in the same reply

This PRD carries the closed interview of `STAGE7_DEMO_SCENARIO_SHAPE.md`, at C:40, into the requirements of checks 7.2 and 7.3 of `FINAL_CHECKLIST.md`. The draft is supporting material; the decisions of the shape and the current `docs/product/specification.md` prevail over it. This document defines the scenario and its verification, and is not evidence that the application has passed a run.

## Business goal

Give the Kraków jury a repeatable demonstration of EnableMe's main scenario in Czyżyny: a person sets their needs, plans a walking route, reads concrete barriers and amenities with their sources and reliability, and confirms a barrier whose new status changes the route. Show explicitly how the application handles contradictory and incomplete information without presenting missing data as confirmed accessibility.

Settle the scenario early enough for Mateusz to prepare the sample data and for Adrian to prepare the Polish video and deck. Verify the scenario on the hosted web application when its dependencies are ready, while keeping the demonstration vote available for the pitch.

## Problem and its consequences

The existing draft describes a possible run, but some of its proposals were changed by the closed interview. Without one agreed scenario, the sample data, the video and the live presentation can demonstrate different facts or require behavior the running application cannot reproduce.

The contradiction scene requires both a real lowered kerb from OpenStreetMap and a sample high kerb report below the confirmation threshold. An incorrectly prepared report or a rehearsal vote on the hosted demo can make the visible status change impossible during the pitch. The sample facts must also be placed on the actual pedestrian network: the schematic positions of the on-device demo do not establish their real-world locations.

Writing the scenario does not complete the hosted verification. The checks for the running application, its sample data and its presentation of facts remain prerequisites, and an unperformed or blocked scene must not be reported as passed.

## Scope

- A timed scenario for the hosted web application, covering the main journey and the contradictory and incomplete data of checks 7.2 and 7.3.
- The required sample facts S-1 - S-8, their intended states, their placement conditions and the confirmations or denials needed to produce those states.
- The real map data and address matches that the scenario depends on, with their verification status.
- The rules for rehearsal, preservation of the hosted demonstration state and recovery by the server owner if that state changes early.
- A separate local check of the message shown when routing is unavailable.
- Handover material for the sample data, Polish video and deck, and the comparison with the HarmonyOS demonstration.
- Recorded outcomes of the hosted and local checks, including unmet prerequisites and known limitations.

## Out of scope

- Building or deploying the hosted application, importing the open data, preparing the sample data themselves, or implementing route planning, address search, accounts and community facts.
- The storage and loading mechanics of sample votes, their dates and repeat loading, which belong to Mateusz's sample-data work.
- Selecting the client or data used for the Polish video, writing its script or recording it, and preparing the decks and pitch. Adrian carries the Polish video and deck; this initiative supplies their scenario.
- Modifying the HarmonyOS application or its bundled demo facts. Kuber decides whether it follows any departure required by the hosted scenario.
- Reporting a new barrier, account flows, moderation, a profile without barriers, a route with no barrier-free alternative, and routes with public transport.
- Performing the basic accessibility assessment, which belongs to check 6.5, or planning a substitute pitch if the hosted demo is not ready.
- Stopping routing on the hosted demo, resetting hosted data by the agent, and submitting materials to the organizers.

## Functional requirements

FR-1. Write the main run as an ordered sequence: select the wheelchair preset; show the map and legend; choose the start and destination through submitted address searches; read the route result and list; open a user report and a map-data fact; explain the stretches without complete data; confirm S-5 without an account and observe the route planned again; finish on the page about the data. Each step states the user's action, the view, the expected visible result, its time and the MVP acceptance criterion and Kraków validation point it demonstrates. The intended duration is about 2 minutes 40 seconds; the pitch decides how much is shown live.

FR-2. Describe all eight sample facts from the existing HarmonyOS demo, preserving their type, kind, description, number of steps and intended status except for the agreed additional confirmation weight on S-5. Describe the conditions for placing them on real ways in Czyżyny and the votes required by M4. The flagged and hidden facts S-6 - S-8 are included in the handover but do not add a moderation scene to the run.

FR-3. Identify the real map data and address results required by the run: a lowered kerb at the crossing of S-5, a map-data fact on or near the route, route stretches with partial data, and the two full-address matches. Mark each as awaiting verification until Mateusz checks it against the imported copy and the running application. If the default route lacks the lowered kerb or a way around S-2, record the alternative destination in Czyżyny that Mateusz chooses and carry it into every affected scene.

FR-4. Demonstrate both incomplete and contradictory data. Show the straight connections to the pedestrian network as no data and the verified partial-data stretches as partial data, with the plain note that some stretches lack data. Show S-5 as an unverified report contradicted by map data before the vote. Nothing lacking the required data for the selected profile is presented as confirmed accessibility.

FR-5. Verify the unavailable-routing message separately on the local application, using the same application version and demo data as the hosted run. When routing is unavailable, the user sees its plain explanation and no route. Keep a screenshot or a short clip as evidence and restore local routing after the check. The hosted routing remains available throughout this exercise.

FR-6. State the limitations the presenter must explain: current location is unavailable on the hosted link, so the run starts from an address; unavailable routing is demonstrated locally; reports and geozones are marked sample data while the map-data facts come from the dated imported copy; the demo and its data are removed by their owner on 4 October 2026 after the results are announced.

FR-7. Preserve the hosted demonstration state until the pitch. Rehearse only steps 1 - 6 on the hosted application, stopping before the confirmation. Rehearse the confirmation and the resulting route change locally. Do not give out the hosted link before the pitch. The optional demo-link field of the Kraków submission stays empty until then.

FR-8. Describe the response to an early hosted vote on S-5: record that the initial scene is no longer ready and refer restoration of the original demo data to the server owner. After restoration, verify the starting state again before claiming the scene is ready. The agent never resets the hosted data.

FR-9. Prepare the scenario for Mateusz's sample-data work and Adrian's video and deck. Identify for Kuber the additional confirmation weight on S-5 and any changed destination, so he can decide whether the HarmonyOS demo follows them. Do not claim that recipients accepted the handover unless that acceptance is recorded.

FR-10. Identify the basic accessibility assessment of check 6.5 as separate evidence for the Kraków validation. The timed run does not claim to perform that assessment. Any short keyboard demonstration during the pitch is decided as part of the pitch.

FR-11. Record the prerequisite checks before a hosted run: 7.1 for the hosted application, 6.1 for the web main scenario, 6.2 for the presentation of sources and statuses, and 3.3 for the sample data. An unmet prerequisite or an unverified real map-data dependency is recorded as preventing the affected scene from passing.

FR-12. Verify the main run on the hosted web application once the prerequisites are met, observing the rehearsal boundary of FR-7 and the demonstration vote at the pitch. Record actual results for checks 7.2 and 7.3, distinguishing passed, failed and unperformed scenes and identifying the separate local evidence for unavailable routing. Rafał verifies the completion of the checklist checks.

## Acceptance criteria

AC-1 (FR-1). A reader can follow the scenario from the wheelchair preset to the page about the data without inventing an action. Every step has its action, view, visible result, duration and traceability to the relevant MVP acceptance criterion and Kraków validation point. The step times total approximately 2:40 and omit the draft's optional profile-without-barriers scene.

AC-2 (FR-1, FR-2). The wheelchair preset sets the five barriers and four amenities of M1. The map and legend distinguish sample reports and areas from real map data and show the date of the imported copy. The route result contains its segment states, summary and three list groups; the additional-barrier group may be empty for this preset.

AC-3 (FR-1, FR-3). Submitted searches return the Tauron Arena and the selected destination in Kraków with full addresses. Neither route endpoint is set until the presenter selects a result, even when only one match is returned. The default destination is Ogród Doświadczeń unless the documented placement conditions require another destination in Czyżyny.

AC-4 (FR-1, FR-2). On the chosen route, S-2 is an unverified report of four stairs, its segment is marked as a barrier and an alternative avoiding it is offered with a reason naming stairs and the unverified status. The list includes the confirmed ramp S-3 among amenities, and the route avoids the disputed poor-surface geozone S-4. These results are checked with the prepared sample data rather than assumed from their intended positions.

AC-5 (FR-2, FR-9). The handover describes all S-1 - S-8 and their placement and voting conditions. It explicitly identifies S-5's departure from the bundled demo: total confirmation weight 1.5 before the presenter's vote. S-6 and S-7 remain flagged sample facts off the demonstration route; S-8 is hidden and affects neither the visible route nor its list.

AC-6 (FR-3, FR-11). Each required map-data item and address match has a recorded verified or unverified state. No unverified lowered kerb or partial-data segment is described as an observed fact. If the default route lacks either the contradiction crossing or the alternative around S-2, the scenario and handover record Mateusz's replacement destination and the affected placements before those scenes can pass.

AC-7 (FR-1, FR-4). The opened S-2 detail shows its type, four steps, description, source, date, unverified status and sample mark. The opened map-data fact shows its real source and the date of its last OpenStreetMap edit. Dates and statuses in the scene agree with the running application, not merely with the draft.

AC-8 (FR-4). Before the confirmation, S-5 is unverified with confirmation weight 1.5 and is within 5 m of the real lowered kerb on the same stretch. Its detail explains the contradiction and its unverified icon remains visible, while the segment follows the map data. One accepted confirmation without an account adds weight 0.5, reaches 2 and makes S-5 confirmed. The application plans the route again and avoids that crossing. A vote recorded only in a local rehearsal does not establish that the hosted scene has passed.

AC-9 (FR-4). The straight stretches joining the chosen points to the pedestrian network are shown as no data. At least one verified partial-data stretch is shown as partial data. The summary and plain note communicate the missing data without listing missing attributes. No such stretch is shown as free of barriers. If no segment has complete data, the legend still explains the four assessed states and the presenter explains why the route is mostly partial data.

AC-10 (FR-5). With local routing unavailable, the route request shows the plain unavailable message and no route. A screenshot or short clip records that result, local routing works again after the check, and the hosted routing was not stopped. A test against stand-in answers alone does not count as this local check.

AC-11 (FR-6, FR-10). The scenario states all limitations of FR-6 and points to the separate accessibility assessment of check 6.5. It does not describe the timed run as proof of keyboard, screen-reader or contrast compliance.

AC-12 (FR-7). The hosted rehearsal ends before the vote and leaves S-5 unverified at weight 1.5. The local rehearsal accepts the demonstration vote and shows the status and route change. The hosted link has not been distributed before the pitch, and the submission's optional demo-link field is left empty during that period.

AC-13 (FR-8). If S-5 receives an early hosted vote, the scene is recorded as no longer ready. Restoration belongs to the server owner, and the scene is marked ready again only after the original unverified state and weight 1.5 are checked. No agent reset of hosted data is performed or claimed.

AC-14 (FR-9). The handover identifies Mateusz's sample-data requirements, Adrian's scenario input for the video and deck, and Kuber's decision about the extra weight on S-5 and a changed destination. The record distinguishes preparation of that material from any recipient's acceptance.

AC-15 (FR-11, FR-12). The result record names the state of checks 7.1, 6.1, 6.2 and 3.3 and the affected unverified map-data dependencies. It reports a blocked or unperformed run when they prevent verification, with no claim that checks 7.2 or 7.3 passed just because the scenario was written.

AC-16 (FR-12). The completed hosted run demonstrates the profile, route, concrete facts with source, date and status, sample marks, contradiction and incomplete data. The local unavailable-routing result is identified separately. Rafał has the actual outcomes needed to verify checks 7.2 and 7.3; a mock-only run or an on-device HarmonyOS run is not recorded as their hosted completion.

## Domain rules

- `docs/product/specification.md` is the product authority, particularly M1, M2, M4 and M6 - M10. The requirements of `docs/hackathon/challenge_requirements.md`, section Validation during the presentation, constrain what the demonstration must explain. This initiative adds no product behavior.
- The hosted web application is the client for checks 7.2 and 7.3. The video and HarmonyOS demonstration may use different data or a different client, and their selection does not change what counts as a verified hosted run.
- Sample-fact content comes from the existing bundled HarmonyOS demonstration identified by the shape. Real locations and map-data facts come from the imported copy. S-5's initial weight of 1.5 is the agreed exception to the bundled sample content; another destination is allowed only under the shape's placement conditions.
- A vote with an account weighs 1 and a vote without an account weighs 0.5. The threshold of confirmation is 2 under M4. S-5 starts with confirmations totalling 1.5, so one anonymous confirmation is sufficient. The sample voting identities must leave the presenter eligible for that confirmation.
- An unverified user report contradicted by an opposite map-data kerb remains visible as an unverified report while the segment follows map data. After the report is confirmed, its barrier affects the route according to M2 and M7.
- Missing information never confirms accessibility. The plain note for incomplete stretches follows M8; the scene does not list the names of missing attributes.
- The contribution in the timed run is a confirmation without an account. Under the current M9, people with the same IP address and User-Agent share that identity and its daily limit. A second vote on the same fact by that identity on the same calendar day in Europe/Warsaw is refused. Its pseudonymized identifier remains until the demo and its data are deleted.
- A rehearsal vote changes the fact and cannot be treated as a harmless preview. Hosted rehearsal therefore ends before the vote, while local rehearsal uses separate data. The hosted demonstration state is preserved from preparation until the pitch.
- No hosted address, host, login or secret enters the scenario or its result record. The public link is supplied outside the repository. Sample descriptions contain no personal data, and result evidence must not expose the presenter's IP address, User-Agent or identifier.
- Flagged sample content remains public until hidden. The flagged off-route facts do not add a moderation scene, and hidden S-8 changes nothing in the public run.

## Dependencies and impact on other modules

- The scenario can be written before the application is ready. Its hosted verification depends on checks 7.1, 6.1, 6.2 and 3.3 of `FINAL_CHECKLIST.md`; its local checks require the corresponding local application and demo data.
- Mateusz's sample-data work consumes the scenario's fact content, placement conditions and intended voting totals. Mateusz verifies the real map-data dependencies and chooses a replacement destination when the agreed conditions require it.
- The run consumes route planning, submitted address search, fact reads and anonymous confirmation. According to the user's current division of work, Rafał works on walking routes, address search and accounts; community facts is being handled in a separate session. This PRD assigns no implementation of those features to this initiative.
- Adrian consumes the scenario for the Polish video and deck and decides their recording choices. Rafał and Adrian decide how much of the scenario fits the pitch. The pitch length remains a dependency of check 10.6 rather than an invented limit in this PRD.
- Kuber receives the identified differences from the bundled HarmonyOS demo and decides whether to align its content. Aligning it is not a prerequisite for verifying the hosted web run.
- The separate accessibility result of check 6.5 supplies the relevant Kraków validation evidence. Check 10.6 decides whether to include a short keyboard demonstration during the pitch.
- Rafał verifies checklist completion from the actual results. Restoration after an early hosted vote remains the server owner's responsibility, outside the agent's execution scope.

## Risks and notes

- The recorded local readiness check found no product endpoints registered in the available checkout and no running local containers. That result does not establish the state of any separate hosted deployment. The hosted address and the running application remain unverified here.
- The needed lowered kerb, route around S-2 and partial-data stretch may not exist on the default route. Their existence cannot be inferred from the draft or invented sample coordinates. The destination-change rule addresses placement, but the affected scenes remain unverified until checked.
- S-5 at weight 1 rather than 1.5 would reach only 1.5 after an anonymous vote, so the status would not change. An earlier vote from the same IP and User-Agent may instead make the demonstration vote unavailable that day. Sample-data preparation and local rehearsal must prove the starting conditions.
- Anyone receiving the hosted link early can vote or add reports that change the run. Withholding the link and stopping rehearsal before the vote are the agreed protections, not a guarantee against an accidental write.
- Restoring hosted demo data is a human action and may require importing the copy again, taking up to 60 minutes. This initiative supplies no shortcut that deletes a vote or invents a second contradiction scene.
- The draft's approximate timings are not a measured rehearsal result. The pitch length and final route geometry are still unknown, and must not be reported as established by this PRD.
- Passing this scenario does not prove all MVP acceptance criteria: new reports, accounts, moderation, the no-barrier-free-route case, public transport and the accessibility assessment remain outside this run.
- Approval of this PRD allows the implementation plan to define the concrete artifacts and verification procedure. It does not certify that either the hosted or local demonstration already works.
