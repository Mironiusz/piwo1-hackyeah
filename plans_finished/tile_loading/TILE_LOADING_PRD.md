# PRD: Tile-archive step of the common demo-loading program

Document state: 2026-10-04, approved by the user; technical planning authorized

## Business goal

Let the common loading program of the hosted demo put the map tile archive of Kraków in place, check it and report it truthfully, so that the program meets its tile requirements (`plans/osm_import/OSM_IMPORT_PRD.md` FR-3, FR-4, AC-4, AC-6, AC-9, AC-10) and `plans/osm_import/` can resume (`plans/osm_import/OSM_IMPORT_PLAN.md` D-21). A person who opens the hosted demo then sees the map of Kraków drawn from the archive the project itself serves.

This PRD implements the closed interview of `TILE_LOADING_SHAPE.md`, held at C:40.

## Problem and its consequences

- The approved PRD of `plans/osm_import/` makes the tile archive a required effect of complete loading and asks for a written contract of the tile step. `plans_finished/map_tiles/` delivered the archive as a file handed over by hand and built no step (`plans_finished/map_tiles/MAP_TILES_PLAN.md` D-1), so the common program has nothing to compose and can never report complete loading.
- Without a step, the archive reaches the server only by a person copying it into the place the demo serves. A copy that is interrupted or of the wrong file is then served to browsers unchecked, and nothing tells the operator about it.
- The documents of the repository disagree on how the archive reaches the server: `plans_finished/map_tiles/` says by hand, while check 3.4 of `FINAL_CHECKLIST.md`, `MVP.md`, `docs/deployment/hosted_demo.md` and `plans_finished/backend_architecture/` say a step of the loading program writes it. As long as they disagree, nobody owns the step.

## Scope

- A step that takes the archive from a source place where a person put it by hand, checks it against the recorded value of the archive and puts it into the place the demo serves, never leaving a partly written or unchecked file under the served name.
- A repeat behavior that keeps a correct archive in place without rewriting it and replaces any other file under the served name.
- Truthful failure with a reason the loading program can show, leaving the served file as it was.
- A command of the step's own, usable on the server before the common program exists, excluded mutually with the common program.
- A written contract of the step for `plans/osm_import/` to compose.
- The correction of every document that names `plans_finished/map_tiles/` or Adrian as the supplier of the tile step or says that no step exists, including the instructions for putting the archive on the server.
- Verification of the acceptance criteria below.

## Out of scope

- Producing or cutting the archive, the style and the fonts. They belong to `plans_finished/map_tiles/`, and the server uses the file Adrian produced.
- The common loading program, its exclusion, its summary and the composition of the tile step into it. They belong to `plans/osm_import/`, which composes delivered steps without taking ownership of their loading rules.
- The server part that serves the archive to browsers, the storage of the services and the commands of the hosted demo. They belong to `plans/deployment_config/`.
- Handing the file from Adrian to the operator and putting it into the source place on the server. These are steps of a person.
- Accepting an archive other than the recorded one, a new cut on the server, and removing the source file after loading.
- Any operation in the hosted demo environment without the user's separate explicit request.

## Functional requirements

FR-1. Loading. The step takes the archive from the source place, checks that it is the recorded archive, writes it into the served place under a temporary name, checks the written copy again and only then puts it under the served name in one atomic replacement. Under the served name a reader never finds a partly written or unchecked file.

FR-2. Repeat. When the file under the served name is already the recorded archive, the step writes nothing and reports the effect as unchanged, which completes it; the source place is not needed then. When the file under the served name is missing or is another file, the step loads the archive as FR-1 says, replacing the other file. This is the user's choice of 2026-10-04 in the interview.

FR-3. Failure. A missing source file, a source file that is not the recorded archive, a copy that fails or a written copy that is not the recorded archive end the step as failed, with a reason the loading program can show, and leave the file under the served name as it was. The step never reports success it has not established.

FR-4. Own command. Besides the step the common loading program composes, a person can run the step on its own with a command of its own, before the common program exists. The common program later calls the same step, not the command. This is the user's choice of 2026-10-04 in the interview.

FR-5. Exclusion. The command of FR-4 and the common loading program exclude each other in the way a standalone OpenStreetMap import and the common program do: a run started while the other one is active refuses at once and writes nothing.

FR-6. The contract of the step. The inputs, the outcomes, the failure reasons, the repeat behavior of FR-2 and a finite whole-step execution budget are written down for `plans/osm_import/` to compose. The failure reasons are fixed codes and reveal no location on the server.

FR-7. Corrected documents. In the same change, every document that names `plans_finished/map_tiles/` or Adrian as the supplier of the tile step, or says that no step exists, names this initiative and the step instead: `MVP.md`, `FINAL_CHECKLIST.md`, `docs/setup/MAP_SETUP.md` with the instructions for putting the archive on the server, `docs/deployment/loading_program.md`, the PRD, plan and handoff of `plans/osm_import/`, and open question 3 of `plans/deployment_config/DEPLOYMENT_CONFIG_SHAPE.md`. This is the user's choice of 2026-10-04 in the interview, given by Rafał as the lead; it does not replace the ruling of Mateusz, Kuba or Adrian on their documents.

## Acceptance criteria

AC-1 (FR-1). With the file of Adrian, 34 785 215 bytes with the recorded value of `docs/setup/MAP_SETUP.md`, in the source place and nothing in the served place, one run leaves under the served name a file with the recorded value, leaves no temporary file behind and reports the archive as loaded.

AC-2 (FR-1, FR-3). When a run stops after writing part of the temporary copy, the served name holds exactly what it held before the run: nothing, or the earlier file. A reader of the served name during a run finds either the earlier state or the complete checked archive, never a part of a file.

AC-3 (FR-2). With the recorded archive under the served name and the source place empty, a run writes nothing, leaves the served file untouched and reports the effect as unchanged and complete.

AC-4 (FR-2). With a file of another value under the served name and the file of Adrian in the source place, a run leaves the recorded archive under the served name and reports it as loaded.

AC-5 (FR-3). Each of four inputs - no source file; a source file cut short to 1 000 000 bytes; a source file of the right size with one changed byte; a written copy that does not match - ends the run as failed with a fixed reason, leaves the served name as it was and starts no later step of the common program. No reason and no message names a location on the server.

AC-6 (FR-4). The command of FR-4, run on its own, reaches the same states and outcomes as AC-1 - AC-5 and tells the person whether the archive is in place or why it is not.

AC-7 (FR-5). While the common program is running, the command of FR-4 refuses at once, writes nothing and leaves the running program undisturbed. While the command is running, the common program refuses at once and starts none of its steps.

AC-8 (FR-6). The written contract names the inputs, the outcomes loaded and unchanged, every failure reason, the repeat behavior and the value of the whole-step budget. A run that reaches its budget ends as failed, and the served name then holds either the earlier state or the complete checked archive.

AC-9 (FR-7). After the change none of the documents of FR-7 names `plans_finished/map_tiles/` or Adrian as the supplier of the tile step or says that no step exists. `docs/setup/MAP_SETUP.md` tells the person where to put the file, how to run the step and how to read its outcome, and check 3.4 of `FINAL_CHECKLIST.md` names this initiative.

## Domain rules

- The archive of the hosted demo is the file Adrian produced on 2026-10-03 from the Protomaps build `20261003`, identified by its recorded SHA-256 value in `docs/setup/MAP_SETUP.md`, and it is not cut again on the server. The step accepts no other file.
- The source place lies outside the served place, so that no unchecked file is ever served.
- The browser takes the archive from the host of the page and from nowhere else (`docs/product/specification.md`, Personal data).
- The archive is never committed (`plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md` D-5).
- The base map is a background: not a source of facts and without a date in the interface (`plans_finished/map_tiles/MAP_TILES_SHAPE.md`, Domain rules).
- The step only puts a file in place. It does not start, restart or configure the server part that serves it.
- No address, host, login or secret of the server enters the repository (`docs/standards/standard_config.md`; `CLAUDE.md`, section Target environment).

## Dependencies and impact on other modules

- `plans/osm_import/`, owned by Mateusz, composes the step into the common loading program, which shows its outcome, stops at its failure and holds the shared exclusion through it. Its PRD, plan and handoff are corrected by FR-7, and it resumes once this initiative delivers the step (`plans/osm_import/OSM_IMPORT_PLAN.md` D-21).
- `plans/deployment_config/`, owned by Kuba, gives the loading program on the server the source place to read and the served place to write, and serves the served place at the address the frontend asks for. Until it does, the step can be verified only on a machine of the team.
- `plans_finished/map_tiles/`, owned by Adrian, supplies the file and its record. Its D-1 stays true: it builds no step.
- The shared backend foundations supply the configuration, the logging and the exclusion the step and its command use.
- Check 3.4 of `FINAL_CHECKLIST.md` verifies the loading of the archive through the common program.

## Risks and notes

- The map must show at the public link before 10:00 on 4 October 2026. The common program and the server part do not exist yet, so for that check the archive most likely reaches the server by hand. This initiative does not change that deadline and does not depend on it.
- Mateusz, Kuba and Adrian have not confirmed the dependencies above or the corrections of their documents.
- The step can be verified on the server only after `plans/deployment_config/` delivers the two places and the server part.
- Accepting only the recorded archive means that a new cut of the archive needs a new record and a change of the step.
- The archive exists as one file on one machine; if it is lost, it has to be cut again as `docs/setup/MAP_SETUP.md` describes, which changes its value.
