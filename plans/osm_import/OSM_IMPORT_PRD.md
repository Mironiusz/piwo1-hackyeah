# PRD: OpenStreetMap copy read and common demo loading

Document state: 2026-10-04, approved by the user; technical planning authorized

## Business goal

Let the team load the three required demo resources through one manual loading program, and let clients read the date of the OpenStreetMap copy currently in use. The demo can start with open accessibility information, its own base map and marked sample contributions, while telling people how fresh its open data are.

This PRD implements the closed interview of `OSM_IMPORT_SHAPE.md` under M6 and M10 of `docs/product/specification.md`. It retains the ownership handoff of `MVP.md`, section Initiatives: `osm_importer` supplies the actual OpenStreetMap import and matching walking-routing data; this initiative supplies the copy-date read and the common loading flow.

## Problem and its consequences

The demo needs an OpenStreetMap copy with matching walking-routing data, a map tile archive and sample reports and geozones. Without a common loading flow and an agreed step contract, each resource can have an unrelated loading procedure, or the program can incorrectly claim completion while a required resource is missing.

Clients need the date of the source state in use. Showing the download date, the loading date or a guessed date would misrepresent the freshness of the accessibility information.

Loading can fail after an earlier step has committed its effects. A retry that duplicates sample contributions, removes community contributions or incorrectly reports that the committed copy was rolled back damages the demo's data and the operator's understanding of its state.

## Scope

- Public reading of the current OpenStreetMap copy date under the existing programming-interface contract.
- One manually started loading flow that consumes the existing importer and the tile and sample steps delivered by their initiatives.
- A written loading-step contract handed to those initiatives before they implement their integrations.
- Truthful reporting of complete loading, incomplete loading and effects already committed.
- Manual recovery by repeating the entire flow with repeat-safe steps, as the user chose in question Q-1 of the shape.
- Verification of the read behavior, orchestration, partial failures and repeat safety, with English documentation of the loading flow and the step handoff.

## Out of scope

- Building a second importer or changing the selected source, coverage, tag mapping, reconciliation rules or walking-routing data preparation.
- Producing the tile archive or the sample dataset and implementing their loading steps; `map_tiles` and `sample_data` own those steps.
- Delivering shared backend foundations, changing shared storage or introducing new authentication, voting or fact-status rules.
- Computing routes, starting or restarting the routing service, or changing deployment configuration.
- Loading at service startup, scheduled refreshes, automatic retries, selective resumption of unfinished steps or deleting demo data.
- A guarantee that all three loading effects are rolled back together when any step fails.
- Performing hosted-demo operations without the user's separate explicit request.

## Functional requirements

FR-1. Current copy date. Clients can publicly read the calendar day in Europe/Warsaw of the OpenStreetMap source state currently in use. The result is empty in the established form before the first published copy exists. The existing request, response and session rules remain unchanged. Reading the date changes no stored data.

FR-2. Manual loading. A member of the team can manually start one common loading flow after the existing preparation requirements are met. The flow consumes the importer already assigned to `osm_importer`. Service startup and restart never trigger loading, and no schedule triggers it.

FR-3. All required effects. Complete loading includes the OpenStreetMap copy with its matching prepared walking-routing data, the map tile archive and the sample reports and geozones marked as sample data. Complete success requires every required effect to succeed. A missing, failed, unfinished or uncertain required effect must not be silently treated as complete success. Preparing routing data does not mean that the routing service has started serving them.

FR-4. Step handoff. Before the tile and sample integrations are implemented, the initiative supplies a written common loading-step contract that identifies the required inputs, observable outcomes, failure reporting and repeat-safety obligations. Adrian adds the tile step through `map_tiles`, and Mateusz adds the sample step through `sample_data`. This initiative composes their delivered steps without taking ownership of their data production or loading rules.

FR-5. Truthful partial outcomes. When a loading attempt fails, the operator can distinguish full completion from incomplete loading and can identify required effects that succeeded, failed or were not completed. A copy that the importer already committed remains a committed copy even if preparing its activation or another loading step fails. An uncertain commit remains explicitly uncertain. The common program preserves these distinctions and never claims a proven rollback or complete success when the importer has not established it.

FR-6. Repeat-safe manual recovery. After partial success, the operator fixes the cause and manually starts the entire loading flow again, including previously successful steps. Every step is safe to repeat. A retry preserves community reports, votes and accounts and does not duplicate sample contributions. Repeating the same source state does not duplicate imported data or copy history under the importer's established rules. This is the user's choice of option A on 2026-10-04 in the shape interview.

FR-7. Verification and instructions. English documentation explains the prerequisites, manual loading, complete and partial outcomes, the copy date and the full-flow retry procedure. Verification covers the acceptance criteria below. Loading failures and instructions do not expose hosting secrets or personal information about contributors.

## Acceptance criteria

AC-1 (FR-1). With a reachable, prepared data store and no published copy, a public copy-date request succeeds and returns the existing contract's empty-copy result. It supplies no invented date and writes no data.

AC-2 (FR-1). With source states of 1 and 2 October 2026 published on later days, reading freshness returns 2 October 2026, whatever their download and publication dates. The result follows the current source state, rather than the order in which a client happened to request it.

AC-3 (FR-1). For a source state at 23:30 UTC on 1 October 2026, reading freshness returns 2 October 2026 in Europe/Warsaw. Cases on both sides of a local day boundary and in both winter and summer time give the correct local calendar day. The existing rules for absent, valid and invalid session credentials apply unchanged.

AC-4 (FR-1, FR-2, FR-3). A manually triggered loading attempt with all prerequisites and steps available completes the three required effects: the copy and matching prepared walking-routing data, the tile archive and marked sample contributions. The program reports full loading success. Reading freshness returns the published source-copy day. Routing-service activation remains a separate existing operation.

AC-5 (FR-2, FR-6). Starting or restarting the service, including after a fix, triggers zero loading attempts and preserves previously loaded resources and community contributions. Another loading attempt occurs only when a member of the team starts it manually.

AC-6 (FR-3, FR-4). With a required tile or sample integration absent, the loading program cannot report complete loading. The written step contract covers inputs, observable success, failure and repeat safety for both integrations, with their ownership preserved.

AC-7 (FR-3, FR-5). When the importer fails before committing a fresh copy, the loading attempt does not report complete success. With a previous complete copy, its imported data and freshness date remain unchanged. With no previous copy, reading freshness still returns the empty-copy result.

AC-8 (FR-3, FR-5). When the importer commits a copy but fails to complete publication of the matching routing-data selection, the common program reports incomplete loading and preserves the fact that the copy was committed. Reading freshness returns that committed source-copy day. If the importer instead reports an uncertain commit, the loading result retains the uncertainty and claims neither proven rollback nor complete success.

AC-9 (FR-5, FR-6). At 08:00 the OpenStreetMap step commits its copy and completes its matching prepared routing-data publication. At 08:10 the subsequent tile or sample step fails. The program reports incomplete loading, identifies completed and incomplete effects and does not claim that the copy was rolled back. The published date remains readable. At 08:15 the operator fixes the cause and starts another attempt; that attempt includes every required step, including the previously successful OpenStreetMap step. If every step succeeds, full loading success is reported, community contributions remain and the number of records representing each sample contribution is still one.

AC-10 (FR-6). After a complete successful loading, manually repeating the full flow with the same source state and sample dataset leaves imported identities, copy history, community reports, votes and accounts unduplicated and preserved. The tile step can safely repeat, and each sample contribution remains represented once.

AC-11 (FR-5, FR-7). Instructions distinguish full loading success, incomplete loading with committed effects and an uncertain importer outcome. They explain that manual recovery repeats the entire flow and that loading failure does not establish a rollback of all previously successful steps. Reported failures contain no credentials or contributor-identifying records.

## Domain rules

The product specification prevails over historical planning artifacts. M6 governs manual refresh, complete-copy publication and freshness; M10 governs dates, truthful information and sample marking.

Freshness is the calendar day in Europe/Warsaw of the source state currently in use. It is not the day of download, loading or routing-service restart. Before a copy exists, the service has no freshness date to invent.

The importer owns atomic publication of the OpenStreetMap copy, its reconciliation and its metadata. The common program does not weaken that guarantee or extend it into a promise of atomic rollback across the tile and sample resources. A failed new import preserves the preceding complete copy according to M6; an already committed copy remains committed when a later loading effect fails.

Recovery repeats the entire loading flow by manual intent, under the user's option A. Repeating an already current OpenStreetMap state follows the importer's unchanged-copy rules; the common program does not manufacture another copy date or duplicate history. Every step must satisfy its repeat-safety obligations.

Sample reports and geozones remain marked as sample data. Loading and retry preserve community contributions and do not introduce new rules for access, votes or reliability status.

## Dependencies and impact on other modules

- `backend_skeleton`, owned by Marek, supplies the shared backend foundations. `schema_first_revision`, owned by Kuba, supplies the shared storage foundation. This initiative consumes their agreed contracts; the presence of a planning document does not prove that a runnable foundation exists.
- `osm_importer`, owned by Mateusz, supplies the actual import, its complete-copy and unchanged-copy rules, prepared walking-routing data and truthful publication outcomes. Its open integration questions must be settled before this initiative's executable integration plan can close.
- `map_tiles`, owned by Adrian, and `sample_data`, owned by Mateusz, supply their loading steps and consume the common step contract. Both must implement repeat safety required by FR-6. Their absence prevents verification of complete three-part loading.
- `deployment_config`, owned by Rafał, starts the common program through the existing manual deployment flow. Service startup and routing-service activation remain its separate responsibilities under the existing instructions.
- Clients use the existing copy-date contract. This initiative changes no client interface. Source attribution and presentation remain with the frontend.
- Check 3.2 of `FINAL_CHECKLIST.md` verifies this initiative's copy-date read and OpenStreetMap loading effect after check 3.1. Checks 3.3 and 3.4 verify the sample and tile steps through the same common program; complete loading requires those effects too.

## Risks and notes

- The importer and shared backend integration contracts are unfinished, and the tile and sample integrations have not been delivered. This PRD describes required behavior; it does not claim that those prerequisites already work.
- A failed attempt can leave several resources in different completion states. Accurate outcomes and repeat safety are necessary; selecting option A does not provide either by itself.
- Recovery after an importer commit whose routing-data publication failed depends on the importer's agreed recovery behavior. Technical planning must verify that behavior and must not invent a substitute importer path.
- Full-flow repetition can take as long as its required steps. This PRD makes no measured duration or new timeout promise and does not change the importer's existing execution limits.
- The exact loading-step interfaces, order, failure control and sample deduplication mechanism belong to technical planning and the responsible initiatives. They remain to be verified and agreed before implementation.
- Verification can start with the copy read and orchestration, but complete end-to-end evidence needs all three delivered steps. A partial check is not evidence that the entire loading flow is ready.
- No hosted-demo operation is authorized by this PRD. It records no hosting address, host, login or secret.
