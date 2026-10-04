# PRD: Sample reports and geozones for the demo

Document state: 2026-10-04, rewritten for the dataset of the demo scenario after the shape was reopened; approved by the user, technical planning authorized

## Business goal

Give the team the clearly marked sample community contributions that the demo scenario of `stage7_demo_scenario` relies on in Czyżyny. These are the eight facts of the bundled HarmonyOS demonstration, placed on real ways around the route from the Tauron Arena to Ogród Doświadczeń. Before the pitch they stand in the reliability and moderation states the scenario needs. Above all the contradiction scene must be ready: a high-kerb report contradicted by a real lowered kerb, exactly one anonymous confirmation below the confirmation threshold.

This delivers the data and loading part of FR-18 of `plans_finished/mvp/MVP_PRD.md` and check 3.3 of `FINAL_CHECKLIST.md`, written from the demo scenario as that check requires. The frontend remains responsible for the visible sample mark of MVP AC-17, and the complete demonstration remains with `stage7_demo_scenario`.

## Problem and its consequences

The first approved dataset - four unverified examples with one confirmation of weight 0.5 each - cannot serve the scenario. One anonymous confirmation brings such a report to 1, not 2, so the scene in which the presenter's vote confirms a report and changes the route (MVP AC-9) would fail. The confirmed ramp, the disputed geozone, the stairs to avoid and the flagged and hidden facts the scenario names would not exist either. On 2026-10-04 the user therefore replaced that dataset with the scenario's.

The bundled HarmonyOS facts cannot be copied as they stand. Their positions lie on a schematic network, not on real ways, and their votes of weight 1 assume accounts the samples do not have. Unmarked or misplaced samples could be mistaken for real observations or break the scenes they serve. Repeated loading could duplicate the samples or reset contributions made during the demo.

## Scope

- Eight sample facts, S-1 - S-8, with the content of the bundled HarmonyOS demonstration: type, point or geozone with its radius, number of steps and the Polish description.
- Real places for them in Czyżyny, proposed by the agent from public OpenStreetMap data under the user's delegation, meeting the placement conditions of the scenario, with the evidence recorded.
- Sample votes without an account that give each fact its intended status, with S-5 at a confirmation weight of 1.5.
- The flagged state of S-6 and S-7 and the flagged and hidden state of S-8.
- Dates of the facts, votes and moderation relative to the first successful loading.
- Stable reserved identifiers of the eight facts, documented as a convention the community-fact operations must accept.
- The sample-loading step consumed by the common loading program, with a truthful result and safe repetition after a partially completed loading flow.

## Out of scope

- Building or changing OpenStreetMap import, routing, voting, moderation operations, account operations, frontend views or map tiles. Their implementation initiatives retain those responsibilities.
- Writing or executing the hosted demonstration, choosing a replacement destination for the route and verifying the actual planned route, which belong to `stage7_demo_scenario`, with Mateusz and Rafał.
- Changing the product specification, the structure of the stored data, the public programming interface or the reliability rules. Documenting the identifier convention changes none of them.
- Fabricating or modifying OpenStreetMap observations to produce the contradiction.
- Creating sample accounts or votes attributed to an account, existing or deleted (the user's decision on Q-3).
- Automatic loading on application startup, scheduled loading, deleting sample content, resetting contributions or restoring the scenario's starting state after a live vote. Restoration after an early vote belongs to the server owner, as the scenario decides.
- Operating the hosted demo or using real personal data to fabricate sample authors.
- Changing the bundled HarmonyOS demonstration; Kuber decides whether it follows the departure on S-5.

## Functional requirements

FR-1. Dataset content. Supply these eight facts, each a sample user report and never an OpenStreetMap fact. The descriptions are the Polish texts of the bundled demonstration as they are. The placeholders of S-6 and S-8 imitate content a moderator would hide and contain no real personal data.

| Fact | Kind and type                   | Steps | Description                                                       | Intended status before the run      | Moderation         |
| ---- | ------------------------------- | ----- | ----------------------------------------------------------------- | ----------------------------------- | ------------------ |
| S-1  | Point, high kerb                | -     | none                                                              | Confirmed                           | none               |
| S-2  | Point, stairs                   | 4     | `Brak poręczy po prawej stronie.`                                 | Unverified                          | none               |
| S-3  | Point, ramp                     | -     | none                                                              | Confirmed                           | none               |
| S-4  | Geozone of 25 m, poor surface   | -     | `Remont chodnika, rozkopana nawierzchnia.`                        | Disputed                            | none               |
| S-5  | Point, high kerb                | -     | none                                                              | Unverified, confirmation weight 1.5 | none               |
| S-6  | Point, stairs                   | 3     | `Schody pod domem pana [nazwisko], zawsze zastawione jego autem.` | Unverified                          | flagged            |
| S-7  | Geozone of 50 m, narrow passage | -     | `Rusztowanie na całej szerokości chodnika.`                       | Disputed                            | flagged            |
| S-8  | Point, high kerb                | -     | `tekst z numerem telefonu, ukryty.`                               | Unverified                          | flagged and hidden |

FR-2. Real places. Place every fact on real ways of Czyżyny so that it meets its placement condition, and record the source evidence. The schematic positions of the bundled demonstration are never used as places.

- S-1 at a crossing of ul. Stanisława Lema near the Tauron Arena, off the planned route.
- S-2 within 15 m of a stretch of the route along al. Pokoju that map data does not tag as steps, where a way around exists.
- S-3 within 50 m of the route, by the entrance to the park near Ogród Doświadczeń.
- S-4 beside the shortest way along al. Pokoju, so that the route bends around it, holding neither the start nor the end.
- S-5 within 5 m of a real lowered kerb, on the same stretch, at a crossing the route takes.
- S-6 off the route; S-7 off the route near ul. Medweckiego; S-8 anywhere.

The agent proposes the places from public OpenStreetMap data, under the user's delegation of 2026-10-04. The proposal is evidence for planning, not a check against the imported copy or the actual route.

FR-3. Real contradiction. S-5 is contradicted by OpenStreetMap under M2: a lowered kerb point of the imported copy lies on the same stretch as the report, no more than 5 m from it. A missing tag never establishes a contradiction, and the samples never modify the source copy to satisfy this requirement.

FR-4. Sample votes and statuses. Every sample vote is cast without an account, weighs 0.5 and has its own fictional voter. Each vote of weight 1 of the bundled demonstration becomes two such votes, and S-5 gets three confirmations. The first confirmation of every fact is its author's vote, cast when the fact is created. The intended statuses follow from these votes under M4:

| Fact | Confirmations | Denials | Persons | Status     |
| ---- | ------------- | ------- | ------- | ---------- |
| S-1  | 2             | 0       | 4       | Confirmed  |
| S-2  | 1             | 0       | 2       | Unverified |
| S-3  | 2             | 0       | 4       | Confirmed  |
| S-4  | 1             | 1       | 4       | Disputed   |
| S-5  | 1.5           | 0       | 3       | Unverified |
| S-6  | 1             | 0       | 2       | Unverified |
| S-7  | 1             | 1       | 4       | Disputed   |
| S-8  | 1             | 0       | 2       | Unverified |

No real account, address or browser characteristic is used to fabricate a voter. No sample voter can be the presenter, who therefore remains eligible to confirm S-5, and the presenter's one confirmation of weight 0.5 brings S-5 to 2. Later votes follow the ordinary product rules.

FR-5. Dates. The creation of each fact, every sample vote and every flag and hiding are dated relative to the instant of the first successful loading, by the offsets of the bundled demonstration, from 0.1 to 2 days back. Each date keeps the Europe/Warsaw offset in force at its own instant. A flag or a hiding is never earlier than the fact it concerns. No sample date ever lies after the loading. A repeated loading keeps the dates first written.

FR-6. Moderation state. The loading step itself flags S-6 and S-7 and flags and hides S-8 when it creates them; the moderation operations are not needed for it. A hidden fact is always flagged as well.

FR-7. Reserved identifiers. The eight facts keep stable reserved identifiers outside the range of ordinary facts. They are documented in the product's stored-data documentation as a convention: such identifiers belong only to sample data, and the community-fact operations must accept them. The convention awaits Kuba's confirmation as the owner of that documentation.

FR-8. Required loading effect. Supply the sample step of the common, manually invoked loading flow after the OpenStreetMap data needed for validation are available. Report complete sample success only when all required facts, votes and moderation states are loaded and their spatial and contradiction prerequisites hold. Missing or invalid prerequisites and unsuccessful loading produce a failure visible to the common program.

FR-9. Repeat-safe loading. A manual retry of the whole flow does not duplicate the facts or their sample votes. It does not overwrite later votes, flags or moderation decisions and does not alter unrelated reports, votes and accounts. It never restores a fact to its starting state after people have contributed to it.

## Acceptance criteria

AC-1 (FR-1, FR-4, FR-6, FR-8). With the required source copy available and no samples yet, one successful loading creates exactly the eight facts of FR-1 with their types, kinds, radii, steps and descriptions, and exactly 25 sample votes without an account. The statuses derived from those votes are those of FR-4. S-6 and S-7 are flagged, S-8 is flagged and hidden, the others are neither. No account is created.

AC-2 (FR-2, FR-3). The recorded evidence shows, for each fact, the source elements and measurements that meet its placement condition in public OpenStreetMap data. Against the imported copy, loading confirms the conditions it can check without a route: S-5 within 5 m of a lowered kerb point on the same stretch, and every point fact within 15 m of its intended stretch. The route-dependent conditions - on the route or off it, the way around S-2, S-3 within 50 m, S-4 bending the route - remain AC-5.

AC-3 (FR-1, FR-7, jointly with `community_facts_api`). Reading the visible facts through the existing fact operations returns the sample mark, the user-report source, the dates and the vote-derived status. Their reserved identifiers are accepted by reading, voting and flagging. S-8 is not returned to the public.

AC-4 (FR-1, jointly with `frontend_app`). With the samples loaded and the frontend available, every visible sample carries its sample mark on both the map and its list entry, meeting MVP AC-17, and its details show the source, date and status. This is a joint presentation check, not an extension of this initiative into frontend implementation.

AC-5 (FR-2 - FR-4, jointly with `route_planning`, `community_facts_api`, `frontend_app` and `stage7_demo_scenario`). On the actual route for the wheelchair preset, S-2 marks its stretch as a barrier and an alternative avoids it, S-3 is listed among the amenities, S-4 is avoided, and S-1, S-6 and S-7 lie off the route. Before the presenter's vote S-5 is unverified at 1.5 while its segment follows OpenStreetMap. One confirmation without an account brings it to 2 and confirmed, and the route is planned again around it. A local rehearsal does not count as the hosted result.

AC-6 (FR-8). When the source copy is absent, the lowered kerb next to S-5 is missing or no longer lowered, S-5 lies more than 5 m from it or on another stretch, or a point fact lies farther than 15 m from its intended stretch, the sample step reports failure. The common program does not claim that the demo data or the contradiction are ready.

AC-7 (FR-5). After loading at a known instant, every sample date lies 0.1 to 2 days before it, none after it, and each keeps its Europe/Warsaw offset. A repetition on a later calendar day keeps every date first written.

AC-8 (FR-9). After a successful first loading, immediately repeating the entire flow leaves exactly the same eight facts, 25 sample votes and moderation states, with no duplicate or refreshed vote. Unrelated reports, votes and accounts remain unchanged.

AC-9 (FR-9). After first loading, a person confirms S-5, flags another fact, and a moderator restores S-8 or hides a flagged fact (M11). Repeating loading preserves those contributions and decisions. No sample is reset to its starting status or moderation state.

AC-10 (FR-8, FR-9). When a loading flow is incomplete because the sample step or another required step fails, the common program reports incomplete loading. After the cause is fixed and the entire flow is repeated manually, a successful result has all eight facts and their 25 sample votes, with no duplicates and with existing community contributions preserved.

## Domain rules

- `docs/product/specification.md` prevails. This initiative uses M2 - M5, M8, M10 and M11 without adding exceptions for sample content.
- The content of the facts comes from the bundled HarmonyOS demonstration as it stood on 2026-10-04. Their places come from real OpenStreetMap ways, and their weights are re-expressed as votes without an account. The departure on S-5, a total of 1.5, is the scenario's.
- A sample mark describes provenance; it does not confer confirmation or accessibility. Status is derived from votes on every read under M4. Loading writes votes, never a status, and never freezes a status.
- A lowered kerb point on the same stretch, within 5 m, establishes the contradiction of S-5 under M2. Missing information establishes neither accessibility nor contradiction.
- OpenStreetMap prevails over the contradicting report until the report's confirmations reach 2. The unverified report remains visible as M7 requires.
- A visible geozone whose type matches the profile changes routing under M2 and M5 unless it is outdated or hidden, whatever its status. Its sample mark does not change this behavior.
- A flagged fact stays public until it is hidden (M11); a hidden fact is not shown to the public and changes no route.
- Sample dates are displayed as calendar days in Europe/Warsaw. No fabricated OpenStreetMap edit date replaces source evidence.
- Sample voters are entirely fictional. Preparing them does not use or disclose information about real people.

## Dependencies and impact on other modules

- `schema_first_revision` supplies the stored-data contract needed for local verification. No change to that contract is agreed here.
- `osm_importer` supplies the real pedestrian network, its kerb points and accessibility attributes. The dataset consumes them and preserves their provenance.
- `osm_import` owns the common loading flow and consumes the sample step. That initiative is paused by the user's decision; its session agreed to consume the step's result without assuming the size of the dataset. Its full-flow retry requires sample loading to preserve contributions and avoid duplicates.
- `community_facts`, Kuba's data layer and status evaluator, and Kuba as owner of the stored-data documentation that records the identifier convention.
- `community_facts_api`, Marek's reading, voting, flagging and moderation operations, which must accept the reserved identifiers. They do not exist yet, so AC-3 and AC-5 wait for them.
- `route_planning` and `frontend_app` supply the route assessment and presentation needed for the joint checks AC-4 and AC-5.
- `stage7_demo_scenario`, Rafał's initiative, supplies the content and placement conditions and uses the samples for the run. Its PRD still awaits the user's confirmation. Mateusz and Rafał verify the places against the imported copy and the actual route. If the route lacks a lowered kerb or a way around S-2, Mateusz chooses a replacement destination, and the affected places move with it.
- Kuber owns the bundled HarmonyOS demonstration and decides whether it follows the departure on S-5.
- The initiative's stage is 4. Preparation starts from the agreed documents; verification waits for the delivered dependencies, as `FINAL_CHECKLIST.md`, section Stages, distinguishes.

## Risks and notes

- Public OpenStreetMap data can differ from the copy the importer uses. The proposed places are planning evidence. Loading fails visibly when the imported copy does not support them; it never relocates a fact or invents a contradiction.
- The actual route is not known until routing runs on the imported copy. A proposed place can turn out to be on the route where it should be off it, or the reverse, and only the joint check AC-5 settles it.
- The presenter's confirmation of S-5 needs an identity that has not voted on S-5 the same day. A rehearsal from the same network and browser, or a reverse proxy that hides the client address, can consume or share that identity. This belongs to the scenario and to `community_facts_api`, but it decides whether the scene works.
- The reserved-identifier convention is not confirmed by Kuba, and the operations that must accept it are not built. A later positive-only validation would hide the samples.
- A live vote before the pitch changes the starting state. Loading deliberately does not restore it.
- The descriptions of S-6 and S-8 look like personal data by design. They are placeholders, and the hosted link is withheld until the pitch, as the scenario decides.
- The bundled demonstration may change after 2026-10-04. The dataset follows the content recorded here, not later edits, unless a new decision says otherwise.
- Implementation planning starts only after the user confirms this PRD.
