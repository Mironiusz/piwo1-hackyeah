# PRD: Implement the OpenStreetMap importer for Kraków

Document state: 2026-10-04, approved by the user; technical planning authorized

Scope amendment approved by the user on 2026-10-04: include Valhalla walking-routing data preparation and publication of the routing-data pointer. This amendment also reconciles the existing vote-history requirements with specification version 10; anonymous vote hashes remain until demo deletion.

## Business goal

Give the project its first complete OpenStreetMap copy for Kraków, so that the app can show initial accessibility information and the routing engine can use the pedestrian network before anyone contributes a report. The team can refresh that copy manually without losing community knowledge or presenting incomplete data as current.

This initiative delivers the importer, its verification and operating instructions separately from the MVP initiative. It implements the scope of `OSM_IMPORTER_SHAPE.md` under `docs/product/specification.md` version 10, especially M2, M3, M4 and M6. It does not reopen the choice of source or the approved tag rules.

## Problem and its consequences

The source and tag mapping have been decided, but a decision alone does not supply the network and facts the app consumes. Downloading data without completing the import leaves the main demo scenario unavailable.

A refresh can also damage existing knowledge: facts may disappear from OpenStreetMap while users still confirm them, or return after being marked as removed. Losing their identities or votes makes the reliability information wrong. Publishing only part of a refresh can leave facts and the network describing different source states.

The importer is extracted from work previously assigned to the MVP. Without an explicit ownership handoff, two people may build it independently or assume the other owns its prerequisites.

## Scope

- The first complete import and later manual refreshes from the already selected OpenStreetMap source, covering Kraków under the agreed administrative-area rules.
- The pedestrian network, including the order and positions of its points, and the barriers, amenities and way attributes required by the product and routing decisions.
- Source provenance, the date of the source state and the last OpenStreetMap edit of each fact's element.
- Reconciliation of existing OpenStreetMap facts with each fresh copy, preserving their identities and vote histories.
- Complete-copy publication, failure handling, prevention of overlapping imports and handling of a source state already in use.
- Preparation of the matching pedestrian-network file and Valhalla walking-routing data, and publication of the routing-data pointer after the database copy is committed.
- Verification and English documentation covering operation, the imported data, source provenance and failure outcomes.

## Out of scope

- Selecting a different source or changing product rules and tag thresholds. Existing decisions are inputs to this work.
- Delivering the shared backend setup or shared database schema. Those prerequisites remain with their owners; the importer consumes their agreed contracts.
- Computing routes, starting or restarting the routing service, ingesting public transport data, the frontend, address search, base map tiles or an import action available to app users. Preparation of walking-routing data is included.
- The copy-read operation and the common demo-loading program, retained by `osm_import`, which consumes this importer.
- A scheduled refresh, extending coverage to another city, or writing reports back to OpenStreetMap.
- Running the importer against the hosted demo or changing its services without the user's explicit request.

## Functional requirements

FR-1. Team-controlled operation. A team member can start the first import and subsequent refreshes. App requests never start an import, and no refresh runs on a schedule.

FR-2. Coverage and network. A successful run supplies the complete Kraków copy under the area rules already decided for the source. It includes the pedestrian network of M2 with the geometry and ordered point positions needed by routing. It excludes ways that M2 forbids pedestrians to use.

FR-3. Accessibility information. The importer applies M6 independently of a person's preferences. It retains the distinction between present, explicitly absent, absent by default and unknown attributes wherever those rules require it. Only a present barrier or amenity becomes an OpenStreetMap fact; an absent or unknown item never becomes a positive accessibility claim or a votable fact.

FR-4. Provenance and dates. Every imported fact retains its OpenStreetMap origin and the last edit of the element that gives it. Every complete copy retains the source-state date. The date of download never substitutes for either date. Required provenance that cannot be established causes a failed run.

FR-5. Complete database publication. The network, accessibility information, reconciliation and copy date become current together. Failure during acquisition, validation, processing or database publication before commit leaves the previous complete copy unchanged. A failed first database import exposes no partial copy and no invented freshness date. Routing-pointer publication happens after commit and follows the separate failure rules of FR-13.

FR-6. Stable identity. A fact is matched by its OpenStreetMap element type and identifier together with its fact type. A matching fact keeps its identity and all votes when the source attributes change. A new identity creates a separate fact with no votes and the status unverified. Independent user reports are never merged with it automatically.

FR-7. Disappearing facts. When a fresh copy no longer contains an OpenStreetMap fact, confirmations and denials are evaluated using M4. If confirmations outweigh denials, the fact becomes a user fact with its vote history and date of last confirmation. Otherwise it becomes outdated because it was removed in OpenStreetMap, keeps its vote history and is excluded from the map and routes.

FR-8. Returning facts. When a later copy restores the same fact type on the same OpenStreetMap element, the original fact becomes an OpenStreetMap fact again with the fresh source attributes and edit date, keeping all votes. An independent user report nearby remains separate.

FR-9. Community information. An import never creates, deletes or changes the weight of a vote. It does not overwrite independent user facts, geozones or moderation decisions. A fact still present in OpenStreetMap retains the reliability status its votes give it under M4, rather than being reset by a refresh.

FR-10. Repeated and concurrent runs. Imports do not overlap. A second trigger during an active run is skipped. Processing the source state already in use changes no data or date and creates no duplicates. An older source state is refused without changing the current copy.

FR-11. Operator outcomes. The operator can distinguish a successful publication, an unchanged copy, a skipped concurrent run and a failed run. Instructions explain the first import, refresh, verification and what remains available after each failure.

FR-12. Verification and source documentation. Verification covers the source, area, network, mapping, dates, reconciliation and complete-copy rules. Tests use invented elements; real OpenStreetMap extracts and their slices stay outside the repository. Documentation identifies the selected source, its attribution and terms recorded by the source initiative, how freshness is determined and how a copy is checked.

FR-13. Matching walking-routing data. Before publishing a new database copy, the run prepares the pedestrian-network file and Valhalla walking-routing data from the same validated source and network-selection rules. The prepared data retain the source-copy instant. Preparation failure leaves the previous database copy and routing-data pointer unchanged. After a successful database commit, the run publishes the pointer to the matching prepared data. A later failure must report that the database copy was committed; it must not claim rollback. Routing remains unavailable while the service serves a different copy, rather than returning a route combining source states. Starting or restarting that service remains outside this initiative.

## Acceptance criteria

AC-1 (FR-1, FR-2). With no copy in use, a team-triggered run on a valid source supplies the agreed network and accessibility information for Kraków. Ordered point positions are available to the routing consumer. Examples of allowed pedestrian ways are included and forbidden ways are excluded under M2. No end-user request or schedule starts another import.

AC-2 (FR-3, FR-6). Invented elements exercise every barrier and amenity of M6, including exact thresholds, unlisted values, missing tags, sidewalk attributes and the default of no stairs. Only present items produce facts; explicitly absent, default and unknown values remain distinguishable. New facts have no votes and are unverified. Changing a preference profile does not change the imported information.

AC-3 (FR-4). A source reflecting 2 October and downloaded on 3 October supplies a copy date of 2 October in Europe/Warsaw. A fact edited at 23:30 UTC on 1 October supplies the calendar day 2 October in that zone. Missing or invalid required source dates cause failure without publication.

AC-4 (FR-5). Starting without a copy, a failed download, rejected source, processing failure or database publication failure before commit leaves no partial copy. Starting with a complete copy, each such failure leaves that copy's network, imported facts and date unchanged and preserves the existing vote history. A successful database refresh makes all parts of the new database copy current together. A post-commit routing-pointer failure is checked separately by AC-14.

AC-5 (FR-6, FR-9). A changed source element that still gives the same fact updates the imported attributes and edit date while retaining that fact and every vote. Two votes of weight 1 confirming the fact still yield confirmed after refresh; votes that make it outdated still yield outdated. No refresh adds a confirmation of its own or changes an independent user report, geozone or moderation decision.

AC-6 (FR-7). When a fact disappears, weighted confirmations of 1.5 against denials of 0.5, over the latest votes selected by M4, convert it to a user fact with its last confirmation date and all historical votes. No votes, only denials, or a tie of 0.5 against 0.5 instead make it outdated because it was removed in OpenStreetMap. That removal reason is available to consumers so the fact is excluded from the map and routes.

AC-7 (FR-7, FR-9). A person's older vote is not counted in place of their latest one; persons outside the five most recent do not affect conversion. A vote detached from a deleted account keeps its weight and counts as a separate person under M4. Anonymous vote hashes remain available until demo deletion and keep grouping that person's votes. Refresh preserves the full history in each case.

AC-8 (FR-8). Both a converted fact and a fact outdated because of removal return as the original OpenStreetMap fact when their source identity and fact type reappear. Their votes remain attached. A separate user report of the same type 5 m away is neither merged nor overwritten.

AC-9 (FR-6, FR-10). Repeating the current source state produces the unchanged outcome with identical imported data, fact identities, votes and copy date. An older state produces failure with the same preservation. Where a split or recreated element has a new identifier, it produces a new fact without borrowing votes from the old identity.

AC-10 (FR-10, FR-11). During an active import a second trigger ends as skipped, without starting a competing import. The operator can distinguish that outcome from unchanged, success and failure. After the active run ends, another manually triggered run can proceed.

AC-11 (FR-11, FR-12). The English operating instructions cover prerequisites, the first run, refresh, each outcome and verification of the copy in use. Source documentation covers provenance, attribution, freshness and validation. The verification set uses invented elements and includes the acceptance scenarios above; no real source extract or slice is added to the repository.

AC-12 (FR-2, FR-13). On an invented source, the prepared network file uses exactly the same allowed pedestrian ways and ordered node identities as the stored network. Valhalla walking-routing data carry the source instant of that database copy. Base map tiles and public transport feeds are not produced by this run.

AC-13 (FR-5, FR-13). A failed routing-data build leaves the previous database copy and routing pointer unchanged, including on the first import. A database rollback leaves the old pointer unchanged. A successful database commit followed by pointer publication points to the matching prepared data. Publication never overwrites data the service already loaded.

AC-14 (FR-11, FR-13). If pointer publication fails after the database commits, the operator is told that the database copy was committed and routing activation is incomplete; the result never claims database rollback or complete success. Instructions distinguish the committed database copy, the selected routing data and the copy loaded by the routing service. Until the loaded copy matches, the routing consumer returns unavailable under its existing contract.

## Domain rules

The product specification prevails over historical initiative artifacts. M2 defines the pedestrian network, M3 the closed fact list, M4 identity and votes across refreshes, and M6 tag interpretation and complete-copy freshness.

Vote comparisons use only the latest vote of each of the five persons who voted most recently, with weight 1 for an account and 0.5 without an account. Detached votes retain their weight and count as separate persons under M4. Conversion does not require the confirmation threshold of 2: confirmations only need to outweigh denials. Reliability after conversion still follows M4.

Identity matching never uses distance. Splitting, joining or recreating an element can produce a new identity and a separate fact; the existing identity follows the disappearance rules. The importer does not infer that a new nearby element is the old one.

An outdated fact ordinarily remains on the map under the current specification. Removal in OpenStreetMap is the specific outdated reason that excludes it from the map and routes. A returning fact recovers its OpenStreetMap source without erasing votes or moderation decisions.

Anonymous vote hashes remain until the demo is deleted. Refresh neither clears them nor detaches anonymous votes. Only account deletion creates the detached vote histories described above.

The source-state date and last edit dates are interpreted as calendar days in Europe/Warsaw for display. Missing or unverified information never confirms accessibility, and no import makes a route guarantee accessibility.

## Dependencies and impact on other modules

- The completed source and barrier-mapping initiatives supply the selected source, coverage, validation and mapping decisions. They are inputs to technical planning, not work repeated here.
- The shared backend and schema owners supply the contracts and prerequisites the importer uses. The target schema now exists as part of the specification; its existence does not prove that a usable shared implementation has been delivered.
- Routing consumes the network, accessibility attributes and prepared Valhalla walking-routing data from the same source copy. Marek supplies the routing image and tools, service startup and served-copy checks, and the graph for the route with the fewest barriers. This initiative builds the walking-routing data and publishes their pointer; it does not restart the service.
- Map and fact consumers use the source, dates and removal information supplied by the importer. Presentation and visible attribution remain with the frontend owner.
- The MVP consumes the result of this initiative. Before overlapping implementation begins, record that this initiative supplies the importer and its tests while shared backend prerequisites remain outside it. On 2026-10-04 the user authorized the agent to apply necessary MVP ownership and dependency updates, superseding the original editing restriction.

## Risks and notes

- Ownership recorded on 2026-10-04: `MVP.md` and the MVP plan assign the importer, its tests and Valhalla walking-data preparation to `osm_importer`. `osm_import` retains the copy-read operation and common demo-loading program. This documentation handoff is not proof that shared backend prerequisites or vote-lock integration have been delivered.
- Technical planning must verify the current shared contracts, implementation ownership, execution entry point and resource limits. It must not invent substitute contracts to bypass a missing prerequisite.
- Incorrect source edits can remove many facts. A complete-copy refresh preserves integrity, but it does not prove that every source assertion is true; the fact statuses and user history remain necessary.
- The approved rules were recorded with some decisions made on behalf of the import and database owners. Any later correction must be reconciled with the specification before implementation, rather than silently applied by the importer.
- This PRD authorizes preparation and implementation planning. It does not authorize operations in the hosted demo. Source-term and performance checks needed for the technical plan are not claimed to have been repeated in this phase.
