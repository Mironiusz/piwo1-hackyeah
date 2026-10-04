# PRD: Sample reports and geozones for the demo

Document state: 2026-10-04, approved by the user; technical planning authorized

## Business goal

Give the team a small, clearly marked set of fictional community contributions in Czyżyny that demonstrates the mandatory reporting, geozone and contradictory-data behavior around Tauron Arena Kraków. People viewing the demo must be able to distinguish sample content from real observations and judge reliability through the existing product rules.

This delivers the data and loading part of FR-18 of `plans_finished/mvp/MVP_PRD.md` and check 3.3 of `FINAL_CHECKLIST.md`. The frontend remains responsible for the visible sample mark required by MVP AC-17; the complete demonstration remains with `stage7_demo_scenario`.

## Problem and its consequences

OpenStreetMap alone cannot demonstrate the community-reporting scenario or the precedence of its data over a contradictory, unverified user report. The existing initiative has no agreed concrete sample locations or loading implementation. Unmarked invented observations could be mistaken for information about real accessibility, while repeated loading could duplicate examples or reset contributions made during the demo.

The closed shape resolves the initial scope: three point reports and one geozone, all initially unverified, with one fictional author confirmation without an account each. Confirmations and denials are performed through the application during the demo rather than prepared in advance.

## Scope

- Four fictional examples in Czyżyny near Tauron Arena Kraków: a poor-surface point report that contradicts explicit OpenStreetMap information, a separate stairs report with a positive step count, a rest-place report near the demonstration route, and a separate poor-surface geozone with a radius of 25 m.
- Locations based on the real OpenStreetMap copy used for the demo, chosen to meet the product's spatial rules and coordinated with the demonstration route.
- A sample mark and clearly fictional description for every example, with the source, date and reliability information required of user reports.
- Exactly one initial fictional author confirmation without an account for each example, giving each a confirmation weight of 0.5 and an unverified initial status.
- The sample-loading step consumed by the common loading program, including a truthful result and safe repetition after a partially completed loading flow.

## Out of scope

- Building or changing OpenStreetMap import, routing, voting, moderation, account operations, frontend views or map tiles. Their implementation initiatives retain those responsibilities.
- Writing or executing the complete hosted demonstration, which belongs to `stage7_demo_scenario`.
- Changing the product specification, stored-data contract, public programming interface or reliability rules.
- Fabricating or modifying OpenStreetMap observations to produce the desired contradiction.
- Preloading confirmed, disputed or outdated sample statuses through additional fictional votes, or creating sample accounts.
- Automatic loading on application startup, scheduled loading, deleting sample content or resetting contributions.
- Operating the hosted demo or using real personal data to fabricate sample authors.

## Functional requirements

FR-1. Minimal dataset. Supply the four examples described in Scope. The stairs report and geozone must be spatially separate from the contradictory report so that they do not prevent its demonstration. The rest-place report must be within 50 m of the demonstration route, and the geozone must cover part of a pedestrian stretch.

FR-2. Honest provenance. Every prepared example is a sample user report with a description identifying its content as fictional. Its sample mark, source and date remain available to the existing fact views and lists. Sample content must not be presented as an OpenStreetMap observation or a verified statement of accessibility.

FR-3. Real contradiction. Place the poor-surface point report within 15 m of its nearest pedestrian stretch, where the imported OpenStreetMap surface information explicitly makes poor surface absent under the product's tag rules. A missing tag, a synthetic pedestrian network or the default absence of stairs is not evidence of a contradiction. The samples do not modify the source copy to satisfy this requirement.

FR-4. Initial votes and statuses. On first loading, every sample has exactly one fictional author confirmation cast without an account and no denial, so each starts unverified with confirmation weight 0.5. No real account, IP address or browser data is used to fabricate the author. Subsequent user votes follow the existing product rules and can change the sample's status.

FR-5. Required loading effect. Supply the sample step of the common, manually invoked loading flow after the OpenStreetMap data needed for validation are available. Report complete sample success only when the required examples and initial confirmations have been loaded and their spatial and contradiction prerequisites are satisfied. Missing or invalid prerequisites and unsuccessful loading produce a failure visible to the common program.

FR-6. Repeat-safe loading. A manual retry of the whole flow does not duplicate samples or their initial votes, overwrite their existing votes, flags or moderation state, or alter unrelated reports, votes and accounts. Repeating loading does not restore an example to its initial unverified state after people have contributed to it.

## Acceptance criteria

AC-1 (FR-1, FR-4, FR-5). With the required source copy available and no samples yet, one successful loading creates exactly three sample point reports and one sample geozone with the agreed types. Each has exactly one fictional confirmation without an account and an unverified status; no sample account or additional fictional vote is created.

AC-2 (FR-1, FR-3). Inspecting the chosen locations against the imported pedestrian network shows that the poor-surface point report is within 15 m of its nearest stretch and that the stretch has explicit information classified as poor surface absent. The stairs report gives a positive step count on a separate stretch. The rest place is within 50 m of the demonstration route, and the 25 m geozone covers part of a separate stretch without obstructing the contradictory-data demonstration.

AC-3 (FR-2). Reading all four examples through the existing fact operations returns the sample mark, user-report source, appropriate date and vote-derived status. Each description identifies the content as fictional. No example is returned with an OpenStreetMap source.

AC-4 (FR-2, jointly with `frontend_app`). With the samples loaded and the frontend available, every visible sample carries its sample mark on both the map and its corresponding list entry, meeting MVP AC-17. Its details show the source, date and reliability status. This is a joint presentation check, not an extension of this initiative into frontend implementation.

AC-5 (FR-3, FR-4, jointly with `route_planning`, `community_facts` and `frontend_app`). Before live contributions, a route through the chosen contradictory stretch shows the unverified sample report while its assessment follows OpenStreetMap under M4 and M7. The sample's 0.5 confirmation weight does not reach the override threshold of 2. With the required operations available, people can confirm or deny it through the application and the existing reliability rules apply.

AC-6 (FR-5). When the required source copy is absent, the selected surface attribute is unknown or makes poor surface present, or the contradictory point is farther than 15 m from its nearest pedestrian stretch, the sample step reports failure. The common program does not claim that the full demo data or required contradiction are ready.

AC-7 (FR-6). After a successful first loading, immediately repeating the entire flow leaves exactly the same four sample facts and four initial fictional votes, with no duplicate or refreshed author confirmation. Unrelated reports, votes and accounts remain unchanged.

AC-8 (FR-6). After first loading, a person votes on one sample, flags another, and a moderator hides a flagged example. Repeating loading preserves those contributions and visibility decisions. No hidden sample is restored, no existing vote is replaced, and no sample status is reset to unverified.

AC-9 (FR-5, FR-6). When a loading flow is incomplete because the sample step or another required step fails, the common program reports incomplete loading. After the cause is fixed and the entire flow is manually repeated, a successful result has all four samples and one initial fictional confirmation per sample, with no duplicates and with existing community contributions preserved.

## Domain rules

- `docs/product/specification.md` prevails. This initiative uses M2 - M5, M8, M10 and M11 without adding exceptions for sample content.
- A sample mark describes provenance; it does not confer confirmation or accessibility. Initial status follows the one fictional author confirmation. Later status follows the ordinary latest-vote rules, and loading never freezes that status.
- An explicit surface attribute on the same associated pedestrian stretch establishes the planned contradiction. Missing information does not establish either accessibility or contradiction.
- OpenStreetMap prevails over the contradictory report until its confirmation weight reaches 2. The unverified report remains visible as M7 requires; it does not become a prevailing barrier merely because it is prepared for the demo.
- A visible geozone whose type matches the profile changes routing under M2 and M5 unless it is outdated or hidden. Its sample mark does not change this behavior. The rest place is shown along the route under M8 and does not change its course.
- Sample dates follow the existing date rules, displayed as calendar days in Europe/Warsaw. No fabricated OpenStreetMap edit date replaces source evidence.
- Sample votes use entirely fictional authors. Preparing them does not use or disclose information about real people.
- The user delegated the minimal dataset and location proposal on 2026-10-04 and chose all initial examples to be unverified. The exact locations still require source verification; the dataset must not claim they have already been checked.

## Dependencies and impact on other modules

- `schema_first_revision` supplies the existing stored-data contract needed for local verification. No change to that contract is agreed here.
- `osm_importer` supplies the real pedestrian network and its accessibility attributes. The prepared dataset consumes them and preserves their provenance.
- `osm_import` owns the common loading flow and consumes this initiative's required sample step. Its agreed full-flow retry behavior requires sample loading to preserve existing contributions and avoid duplicates.
- `community_facts` supplies the existing reading, voting, reliability and moderation behavior. The dataset uses those rules rather than implementing another status system.
- `route_planning` and `frontend_app` supply the route assessment and presentation needed for joint checks AC-4 and AC-5. Adrian remains responsible for the frontend presentation; Marek and Kuba retain their community-fact and routing responsibilities recorded in `TEAM.md`.
- `stage7_demo_scenario`, owned by Rafał, uses the examples for the full demonstration. Its chosen route must agree with the sample locations and leave the initial confirmations and denials to live interaction.
- The initiative's stage is 4. Preparation starts from the agreed documents; verification waits for the relevant delivered dependencies, as `FINAL_CHECKLIST.md`, section Stages, distinguishes.

## Risks and notes

- Exact coordinates and the required explicit surface evidence have not yet been verified against the demo copy. A location from a simplified mobile mock cannot serve as evidence. Technical planning must settle this before implementation is considered complete.
- The concrete loading-step interface and sample deduplication contract are not yet established here. They belong to the implementation plan and must be compatible with the concurrently developed common program without guessing its contract.
- The demo scenario has no agreed concrete route yet. Coordinate selection must be coordinated with it rather than presenting a route-dependent example as verified in advance.
- Preserving community contributions means a later loading run may encounter confirmed, disputed, outdated or hidden samples. It must preserve that state rather than recreate the initial demonstration conditions.
- Joint presentation and routing checks cannot pass through document inspection alone. Their runtime evidence requires the relevant operations and frontend; this initiative does not claim their readiness or implement missing dependencies.
- The PRD defines requirements and acceptance behavior only. Implementation planning starts after the user confirms it.
