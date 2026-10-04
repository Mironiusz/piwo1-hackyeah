# Frontend standard

Document state: 2026-10-04

Status: ready - full content. The full description of this standard's position relative to the others is in `docs/standards/README.md`.

## Why this document exists

The frontend is where a person meets the product: a phone-first web app whose whole main scenario has to work with a keyboard and a screen reader, in two languages. The other standards of the repository were written for a Python service, so frontend code written before this document existed had nothing a review could pass or fail it against. Under the strict deviation rule that leaves two outcomes for the first frontend merge request - it stalls or it goes in unchecked.

This standard settles four questions: what the frontend is built in, what its code unit is, which rules it takes from the product, and which automatic gates check it. It is deliberately short. The frontend person chose the workflow core plus one short standard over a full frontend profile mirroring the Python one; what was left out on purpose is named in the last section before the checklist.

## Scope and boundaries

This standard is responsible for frontend code in `frontend/`: its technology, its code unit and documentation, the rules it takes from the product, and its automatic gates. Frontend code is held to this standard and to the six standards of the workflow core. The Python profile does not apply to it.

What is not here:

- The contract of the programming interface between the frontend and the backend - that is `docs/product/api_contract.md`, decided in `plans_finished/api_contract/`. This standard only says that the frontend shows what the interface returns.
- The visual design of the screens. The design direction is an input the technology has to be able to build, recorded in `PRODUCT.md` and `.impeccable/briefs/`.
- The rules of the workflow core - the agentic chain, the task artifacts, review, documentation, formatting and git. They apply to frontend code unchanged and are not repeated here; where a section below names one of them, it says only what the rule means for a frontend file.

## Deviation rule

The standard describes the target state and applies in full from the first commit. A project created from the template has no legacy code, so there is nothing to protect with a transition period - code that does not comply with the standard blocks review regardless of who wrote it and when.

When the repository has legacy code, relaxing this rule to the soft version is to be an explicit decision recorded in `docs/standards/README.md` together with the date and the reason. It is not a state that takes effect on its own.

## Technology

The frontend is a single-page application written in TypeScript with React, built by Vite into static files. It is created from the official Vite template for React with TypeScript, which fixes the versions: React 19.3, Vite 8.3 and TypeScript 6.0.

TypeScript stays on the version of the template, not on the newest major version. The template is the combination its authors keep working together.

Nothing is rendered on the server. The page, its scripts and styles, the fonts, the map tiles, the map fonts and sprites and the programming interface are all served from one host, so the frontend calls the interface on its own origin. No package of the frontend is loaded from a content delivery network at run time: everything is installed with npm and built into the static files.

The map is drawn by MapLibre GL JS, used directly from one React component, without a wrapper library. The app has one map, and a wrapper would add a dependency between React and the map that no requirement asks for.

The map of Kraków is one archive of vector tiles in the PMTiles format, cut out of the daily Protomaps build of OpenStreetMap data for the bounding box of the administrative boundary of Kraków, zoom 0 to 15. The archive lies on the server of the project next to the frontend files, and the browser reads it in byte ranges through the protocol of the `pmtiles` library. It is not committed to the repository: it is a binary file of tens of megabytes that changes with every build.

The style of the base map comes from the Protomaps style package, with the colors set to the design direction and the labels in the language of the interface. The fonts and sprites the style needs are copies served by the project, and the style never points at an outside host. Whether these copies are committed or fetched by a script is decided by the initiative `map_tiles` of `MVP.md`, which sets up the map.

The attribution control of the map is always open, never collapsed, and shows the OpenStreetMap attribution stored in the archive. The interface shows no separate date for the base map, because a second date on the screen would present the base map as a source of facts, which it is not. The key of the build the archive was cut from is written down next to the file when it is produced.

The two typefaces of the design direction are installed as npm packages and built into the static files, never loaded from an outside host.

The rejected variants, the facts behind each choice and the command that cuts the tile archive are in `plans_finished/frontend_stack/FRONTEND_STACK_PLAN.md`, D-1 - D-7 and D-9. A new run time dependency is added only with its reason stated in the merge request.

## Code unit and documentation

Frontend code lives in `frontend/` in the repository root, with its own `package.json` and lock file. The whole frontend application is one code unit in the sense of `standard_documentation.md`, and its durable memory is the group `agent_docs/memory/frontend/`.

Its pair of documents is `frontend/FRONTEND.md` and `frontend/FRONTEND_ALGORITHM.md`, next to the code. The pair is created by the initiative `frontend_app` of `MVP.md`, with the first screen applying a display rule of the product specification. Until then the condition stands in `agent_docs/memory/frontend/_shared.md`, as `standard_documentation.md` asks of a unit that has no domain rule to describe yet.

## Rules that come from the product

- The browser talks only to the server of the project. No address of another host stands in a request, a style, a font or a script of the frontend, so no service outside the project learns the IP address of the person or the area they look at.
- Frontend code holds no product rule. The segment states, the groups of the list, the status of a fact and the calendar day of a date are shown as received. A rule that existed only in the web page would have to be written again for a second client of the same programming interface.
- The map is never the only carrier of a piece of information and never holds the keyboard focus without a way out.
- Every interactive element is reachable with the keyboard and has a text name.
- Every text of the interface exists in both languages.

How the chosen technology meets the acceptance criteria behind these rules is in D-8 of the plan named above.

## Language

Code, names and documentation comments are in English. The texts of the interface live in one dictionary per language. The Polish texts are product content required by the specification, which prevails over the language rule of the repository core, and they stand only in the Polish dictionary.

## Comments

No line comments. A component, a hook or a function that needs explanation gets a documentation comment in the block form above it, in plain language. This is the rule of the repository core on docstrings, applied to TypeScript.

## Formatting

Frontend files are formatted by prettier with the configuration of the repository, the same tool and the same `.prettierrc` as for markdown: a width of 200 characters and double quotation marks.

The forbidden characters of `standard_formatting.md` apply to frontend files, the texts of the interface in both languages included. An icon is drawn as a graphic, never typed as a character.

## Tests of logic

Logic outside components - the state of the page, the mapping of codes to texts, the formatting of distances - has unit tests. No test uses the network.

## Gates

Frontend code has four automatic gates. The first three run from `frontend/`:

- the type check, `npx tsc -b`,
- the lint, `npx oxlint`, with the rule groups `react`, `jsx-a11y` and `typescript` turned on in `frontend/.oxlintrc.json` and every finding of `jsx-a11y` an error,
- the tests, `npx vitest run`,
- the forbidden characters check, `pytest tests/architecture/test_prose_style.py`, extended to the files `.ts`, `.tsx`, `.css`, `.html` and `.json` under `frontend/`.

The gates, their `make` targets and the extension of the test are set up by the initiative `frontend_app` of `MVP.md`, which writes the first frontend code. Until then this standard is checked by review alone.

The type check and the linter are those of the Vite template. The lint does not use type information, so a rule that needs it is not checked by the lint; that is why the type check is a gate of its own.

## What this standard does not cover

The names of frontend files and the split of the frontend into directories. A full frontend profile mirroring the Python one was decided against, so no standard covers them. The condition for writing such a rule is recorded in `docs/standards/README.md`, section Unresolved boundaries and debts.

## Checklist

- Does the change add no address of another host to a request, a style, a font or a script of the frontend?
- Is a new package installed with npm and built into the static files, and is the reason for a new run time dependency stated in the merge request?
- Does frontend code show the segment states, the groups of the list, the status of a fact and the calendar day of a date as received, without a product rule of its own?
- Is everything the map shows also available outside the map, and can the keyboard focus leave the map?
- Is every interactive element reachable with the keyboard, and does it have a text name?
- Does every text of the interface exist in both languages, with the Polish texts only in the Polish dictionary?
- Are code, names and documentation comments in English?
- Is the code free of line comments, with a documentation comment in the block form where an explanation is needed?
- Has the change gone through prettier with the configuration of the repository?
- Is the change free of the forbidden characters, the texts of the interface included?
- Does logic outside components have unit tests that do not use the network?
- Once the gates are set up: do the type check, the lint, the tests and the forbidden characters check pass?
- Is the tile archive kept out of the repository?
