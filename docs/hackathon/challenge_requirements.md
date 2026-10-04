# Challenge requirements

Document state: 2026-10-04

## Why this document exists

The project is submitted to two partner challenges of HackYeah 2026 at once. Their rules decide what has to be delivered, in which language, by when and how it is judged - and in a few places they pull in different directions. This file keeps those external constraints in one place, so that agents and the team check them before shaping a task instead of rediscovering them from four PDFs.

This is not the product specification. The specification (`docs/product/specification.md`) decides what we build; this file lists what the organizers require from whatever we build. A conflict between the two is raised with the user, never resolved silently.

## Provenance

A working summary in our own words of four PDFs received by the team on 2026-10-03:

- City of Kraków: "RULES Cracow Without Barriers.pdf" (terms and conditions with the copyright transfer agreement template) and "KRYTERIA Kraków Bez Barier.pdf" (task description).
- Huawei: "RULES Imagine What_s Next.pdf" (challenge rules) and "CRITERIA Imagine What_s Next.pdf" (task description, technical requirements, deliverables).

The PDFs are not stored in the repository and they remain the authority. When the organizers announce a change, this file gets updated together with the date and the source of the change.

## Shared facts

- Event: HackYeah 2026, 3-4 October 2026, Tauron Arena Kraków. Organizer of the event and submission platform: PROIDEA sp. z o.o.
- Teams of up to six people.
- Kraków: work starts no earlier than 11:00 on 3 October and the solution is submitted no later than 11:00 on 4 October, on the HackTribe platform. Changes made after the deadline are not considered.
- Huawei: follows the official HackYeah 2026 schedule; the submission deadline is not stated in the PDFs and has to be checked in that schedule. Results are announced on 4 October at the closing ceremony.

## Challenge 1: "Kraków bez barier" (City of Kraków)

### Goal

A tool that lets residents and tourists judge the accessibility of places and routes against their individual needs, and that is at the same time a source of information about the accessibility of what the city offers. It shows concrete barriers and amenities instead of an "accessible / not accessible" label, and it has potential for further development, commercialization and scaling to other cities.

The prototype is narrowed to a chosen user group or a chosen kind of needs - the brief gives wheelchair users and parents with baby strollers as an example.

### What the prototype has to do

- Present information about concrete barriers and amenities that is as current as possible: stairs, thresholds, ramps, elevators, entrance width, surface, toilet, places to rest.
- Show for every piece of information its source, the date it was obtained or last confirmed, and its reliability status.
- Use available data sources without the City maintaining a database by hand.
- Not require access to internal systems of the City Hall (UMK) or municipal units (MJO).
- Address the needs of the chosen user group.
- Be easy to use and easy to deploy for potential adopters (hotels, event organizers and similar).
- Show potential for development, commercialization and scaling to other cities or sectors.

### Technical and organizational requirements

- Any technical form (web or mobile) is fine, as long as the main scenario can be demonstrated: find a place or a route and show the accessibility information that matters to the chosen group.
- The architecture separates data acquisition and updates from presentation. The team names the main components, the data flow, and how new sources, place categories and geographic areas are added.
- Only publicly available data and services, on their providers' terms. For city data: the concrete datasets or public APIs, how they are fetched, how often they are updated and what happens when a source is unavailable.
- Every accessibility fact can carry its source, the date it was obtained or last confirmed, and a reliability status. Data from user reports or other unverified sources is clearly distinguished from confirmed data. There is a way to correct wrong or outdated data.
- Digital accessibility: WCAG 2.2 level AA as the development goal. Already in the prototype: keyboard support, screen reader support, readable content, sufficient contrast, and a text alternative for information shown only on the map. The evaluation includes a list of what already works and what still needs work.
- A proposal for running and maintaining the solution outside the City's infrastructure: who is responsible for hosting, updates, security, handling reports, and the running costs. The prototype does not have to stay online after the hackathon.
- Basic data protection and security rules: what user data is collected, how reports and accounts (if any) are protected, secure connections. The app should not ask about a disability when preferences about barriers and amenities are enough to match the results.
- Suitable for development and deployment by others: external provider dependencies, licences of the data and components used, portability to other infrastructure, how to add another city. The technology choice is up to the team.

### Validation during the presentation

- A working demo for the chosen group: state its needs, check at least one place or route, show the concrete barriers and amenities that let the user judge the result on their own.
- Show where the information comes from, when it was obtained or confirmed, and how the app marks incomplete, outdated or unverified data. Sample data used in the demo is clearly marked as sample data.
- At least one case where data is contradictory, incomplete or the source is unavailable, with an explanation of what the user sees then. Missing information is never shown as a confirmation of accessibility.
- A basic accessibility check of the main scenario: keyboard, screen reader, contrast, text form of map information, plus the known limitations of the prototype and a plan to remove them.
- A short plan from prototype to service: who owns the product, how data is collected and verified, how hosting and maintenance are financed, next steps and the conditions for launching in another city.

### Formal deliverables

- Project title, team ID, project description - submitted on HackTribe, in Polish.
- Description of the solution and of the problem it solves; the target group and how the solution is used.
- Description of the data sources and of how their freshness and reliability are assessed.
- A business model proposal and development options.
- A presentation in PDF, at most 10 slides.
- A video of at most 3 minutes (mp4) presenting the project, placed in an accessible, open repository.
- Optional: code repository, screenshots, demo link, graphics and other materials.

### Data sources named in the brief

- Open data portal of the City of Kraków (otwartedane.um.krakow.pl) - JSON, CSV, XLSX and APIs depending on the dataset.
- Municipal spatial information system MSIP (msip.krakow.pl) - downloads and WMS/WFS services; scope and terms checked per dataset.
- National open data portal (dane.gov.pl) - complementary data and data for other cities.
- OpenStreetMap - map and routing base; the licence terms and attribution have to be respected.

Other open sources, information from venue owners and user reports are allowed too. The brief stresses that information being published on the internet does not by itself make it legal to fetch automatically or use commercially - for every source the team states its origin, terms of use, freshness and verification method.

### Judging

The two Kraków documents give two different sets of criteria:

| Source                                 | Criteria and weights                                                                                                                                                                                                                                                    |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Terms and conditions (RULES), point 9  | Idea 30%, Technical aspects 30%, Design 20%, Relation to category 10%, WOW factor 10%                                                                                                                                                                                   |
| Task description (KRYTERIA), section 8 | Relation to the challenge and usefulness for the chosen group, including ease of use 25%, Prototype quality and completeness 20%, Data reliability, presentation and updates 15%, Deployment potential and scalability 20%, Business model and commercial potential 20% |

The RULES definitions: Idea - creativity and how far the problem is solved; Technical aspects - use of different technologies, interaction archiving, algorithms and code quality; Design - solution architecture, scalability and readiness for production deployment; Relation to category - compliance with the task description; WOW factor - originality, including features beyond the requirements. The task description adds that business potential weighs especially strongly. A project needs at least 50% of the points to receive the prize.

### Prize and rights

- 5 000 PLN including tax, paid by PROIDEA within 180 days of the results.
- After accepting the prize, the authors' economic copyrights to the awarded solution are transferred to Gmina Miejska Kraków under the agreement attached to the rules: unconditional transfer with a broad list of fields of exploitation (including modification, decompilation, sublicensing for maintenance), handover of a GitLab repository with complete, runnable source code within 7 days with a joint build-and-run check, and declarations that the authors have not granted any licences and that the work does not infringe third-party rights.

Mentors for this challenge are available in the mentor zone and on Discord (names in the task description).

## Challenge 2: "Imagine What's Next" (Huawei)

### Goal

An innovative system feature or mobile application for an OpenHarmony-based device, in one or more of three areas: Intelligent Experiences (AI, agents, context awareness, on-device AI), Spatial Experiences (spatial UI, sensing, positioning, interaction with the surroundings) and Human-Centric Technology (accessibility, inclusive design, digital wellbeing, responsible technology). Ideas that combine areas with a purpose score higher on originality.

### Technical requirements

- Implementation: native ArkTS with ArkUI or C/C++ platform APIs, or a supported cross-platform framework such as React Native for OpenHarmony (RNOH), or OpenHarmony/Oniro system frameworks.
- Target HarmonyOS, OpenHarmony or Oniro; API 20 or later, declared as the minimum API level where applicable; an SDK and environment compatible with the chosen version.
- Runs on an OpenHarmony or HarmonyOS emulator or a compatible device.
- Reproducible setup, build and launch instructions.
- Uses or improves at least one platform, device or system capability.
- Recommended (optional) toolchain: DevEco Studio, SDK Manager, hvigor, HDC, application signing, emulator or device.
- A cross-platform submission must include the OpenHarmony or HarmonyOS target with its native container, bridge and build configuration. An Android, iOS, web or desktop build alone is not sufficient.
- An improvement is delivered as an installable application or component that adds or improves a capability without modifying the system itself, with an explanation of what it does, how it integrates, how to install it and how to verify it.

### Use of AI

AI tools are allowed and encouraged. A team that used AI tools during development, or whose solution has an AI feature, publishes `AI_WORKFLOW.md`: the models, coding agents, MCP servers, skills and other tools used; the main prompts, reusable instructions and configuration; the workflow from idea and architecture to implementation, testing and debugging; how generated output was reviewed and validated; known limitations, failed approaches and lessons learned. For an AI feature additionally: model or service, inference flow, data handling, limitations, validation and privacy. Keys, credentials and personal data are removed before publishing.

### Deliverables

1. A public source code repository.
2. Reproducible setup, build, installation and launch instructions.
3. A working `.hap` package.
4. A short recorded demonstration.
5. A concise architecture and implementation description.
6. `AI_WORKFLOW.md`, because AI-assisted tools are used.
7. Additional AI integration documentation if the solution has AI features.

All submissions, presentations, demonstrations and project documentation are in English. The submission identifies pre-existing and third-party components and the use of AI tools. The solution has to be created or substantially developed during the challenge; pre-existing code, templates and AI tools are allowed when the team has the right to use them.

### Judging

Each jury member scores every criterion from 1 to 10; the final score is the weighted average. A prize may be withheld below 50% of the maximum score.

| Criterion                                        | Weight | What the jury looks at                                                                                                          |
| ------------------------------------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------------- |
| Originality                                      | 20%    | new idea or fresh take; combining challenge areas with a purpose                                                                |
| Demonstrated usefulness                          | 20%    | who uses it and which problem it solves; the challenge area visible in what the app does; a working narrow solution over slides |
| Technical execution                              | 20%    | works as described; justified architecture; readable modular code; behavior on errors, timeouts, missing data; tests; hygiene   |
| Use or enhancement of platform capabilities      | 20%    | real use of system services, APIs, distributed features; an app that would run unchanged on any OS scores lower                 |
| Quality of the demonstration                     | 10%    | the solution running, emulator by default; clear what was built during the hackathon                                            |
| Reproducibility and transparency of the workflow | 10%    | build from README alone; documented dependencies and versions; commit history showing progress; AI use described                |

Repositories may go through an automated technical pre-review before the jury.

### Prizes and rights

- 12 000 / 8 000 / 5 000 PLN for places 1-3, reduced by due taxes, paid by PROIDEA within 60 days after the winners provide their data.
- Participants keep ownership. Accepting a prize grants Huawei Polska and Huawei Technologies a non-exclusive, royalty-free licence for 3 years to evaluate, demonstrate and promote the solution, without the right to commercialize it.
- Every submitting participant grants Huawei and PROIDEA a licence to use the project name, team name, description, screenshots, presentation materials and demo recordings in communication about the challenge.

## What both challenges need, side by side

| Item                       | Kraków                                                            | Huawei                                              |
| -------------------------- | ----------------------------------------------------------------- | --------------------------------------------------- |
| Language of the submission | Polish (HackTribe)                                                | English (everything)                                |
| Working solution           | prototype or demo of the main scenario                            | `.hap` running on an emulator or device             |
| Code repository            | optional; GitLab handover after winning                           | public, required                                    |
| Presentation               | PDF, at most 10 slides                                            | not required                                        |
| Video                      | mp4, at most 3 minutes, in an open repository                     | short recorded demo                                 |
| Architecture description   | components, data flow, adding sources, categories and cities      | concise architecture and implementation description |
| Data sources               | origin, terms of use, freshness, reliability, unavailability plan | not required                                        |
| Business model and scaling | required, weighs heavily                                          | not required                                        |
| Accessibility of the UI    | WCAG 2.2 AA goal, check of the main scenario                      | not required, fits Human-Centric Technology         |
| Tests                      | not required                                                      | evidence of tests for key scenarios                 |
| Build instructions         | not required                                                      | reproducible, required                              |
| AI documentation           | not required                                                      | `AI_WORKFLOW.md`, required                          |

## Conflicts and open points

Recorded here so nobody discovers them at 10:30 on 4 October. None of them is resolved by this file.

1. Language. Kraków wants the submission in Polish, Huawei wants everything in English. Resolved on 2026-10-03: the repository is written in English (`CLAUDE.md`, section Language and communication style), the Kraków submission text is prepared in Polish.
2. Rights. The Kraków prize transfers the economic copyrights to the City, with a declaration that the authors have not granted any licences; the Huawei prize grants Huawei a non-exclusive licence, and Huawei requires a public repository - an open-source licence file in that repository would also grant licences to everyone. Whether both prizes can be accepted and which licence the repository carries needs clarification with the organizers. This is not legal advice. Entry in `docs/standards/decision_registry.md`.
3. The Kraków transfer agreement template names a different work ("Krakowskie cyfrowe centrum wolontariatu"), most likely a leftover from another edition - to clarify with the organizers if we win.
4. Kraków has two different sets of judging criteria (RULES versus the task description). Both are listed above; which one the jury uses is to be asked of the mentors.
5. Without a HarmonyOS package there is no valid Huawei submission - a web build alone is explicitly not sufficient. The port is optional for Kraków, mandatory for Huawei. Entry in `docs/standards/decision_registry.md`.
6. The Kraków brief asks to narrow the prototype to a chosen user group, and Huawei prefers a working narrow solution; our idea mentions routes for people with different disabilities. The size of the target group is a question for the specification.
7. The Kraków brief says the app should not require disclosing a disability when barrier and amenity preferences are enough. Information about a disability is health data, a special category under Article 9 of the GDPR. Route profiles named after a disability have to be built from barrier preferences, which is a question for the specification.
8. Every data source needs its terms checked before use: OpenStreetMap data is under the ODbL with attribution and share-alike obligations, and information published online is not automatically free to scrape or use commercially.
9. The Huawei submission deadline is not in the PDFs and has to be checked in the HackYeah 2026 schedule.
10. Two decisions of the team knowingly do not meet points of the Kraków brief, both taken by the user on 2026-10-04 after the conflict was raised. The hosted demo is served over plain HTTP, while the brief lists secure connections among the basic data protection and security rules (`plans/mvp/MVP_PLAN.md` D-10). If the optional public transport routes are built, a public transport segment without accessibility data is shown as green, while the brief says missing information is never shown as a confirmation of accessibility (`docs/product/specification.md` M7 and O9, `plans_finished/valhalla_routing/`). The Kraków submission states both in the description of data protection and of the data sources, as known limitations of the prototype.
