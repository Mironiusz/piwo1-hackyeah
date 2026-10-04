# PRD: Choice of the environment in which the MVP demo runs

Document state: 2026-10-03

## Business goal

By 11:00 on 4 October 2026 the MVP of `plans_finished/mvp/` is reachable at a public link given in the Kraków submission on HackTribe, so the jury can open it on its own, also on a phone, and the live demo runs from the same place. The brief lists a demo link as optional, but a link the jury can try on its own supports the criteria of usefulness and ease of use (25%) and of prototype quality and completeness (20%) of the Kraków task description, and the WOW factor of the terms and conditions. This task makes the decisions that goal needs; the task `DEPLOYMENT` of the same initiative delivers the deployment itself.

The same decision resolves the open entry Target environment for the demo in `docs/standards/decision_registry.md`, so that during the night before the deadline the agent works in that environment with permissions the team set on purpose, instead of having none at all.

## Problem and its consequences

Where the demo runs was not decided in phase B of `plans_finished/mvp/`; the user handed the decision to the db person of the team. As long as it stays open:

- nobody can prepare the environment, and every hour taken from the night before 11:00 on 4 October shortens the time for the video, the checks and the fixes,
- `plans_finished/mvp/MVP_PLAN.md` cannot be closed, because its open question Q-7 waits for this decision, and the backend architecture of its Q-11 is decided only after Q-7,
- the agent has no access to any target environment, so reading an error at 02:00 or deploying a fix needs a human every time,
- people outside the team, the jury included, would leave personal data in a service nobody owns and nobody is due to delete.

## Scope

- The choice of the hosting for the demo, recorded with its reason.
- The three permission levels of the agent for the hosted demo environment, in the rules of the repository.
- Recording the decision where people look for it: the deferred decisions registry and the MVP plan.
- The extension of the privacy information requirement of `plans_finished/mvp/MVP_PRD.md` with the deletion of the demo.

## Out of scope

- The other technical decisions delegated in the same conversation, each with its own initiative: `plans_finished/api_contract/`, `plans_finished/routing_engine/`, `plans_finished/osm_data_source/`, `plans_finished/frontend_stack/`, `plans_finished/osm_barrier_mapping/`, `plans_finished/local_database/`, `plans_finished/geocoding/`, `plans_finished/account_sessions/`.
- The deployment configuration with written instructions, the secure connection of the public link, and making the routing service unreachable during the live demo. The user moved them on 2026-10-03, in phase B of this task, to the task `DEPLOYMENT` of this initiative (`plans_finished/deployment/DEPLOYMENT_SEED.md`). Reason: the configuration names how the service and the worker start, which `plans_finished/mvp/MVP_PLAN.md` decides in Q-11 only after its Q-7 is closed by this task, so keeping them here made each wait for the other.
- Standing the hosted environment up: creating the account with the hosting provider, the first deployment and checking the main scenario at the public link before the submission. The team took it out of this initiative on 2026-10-03; the db person does it, using what this initiative delivers.
- Deleting the environment on 4 October 2026, and written instructions for it. The deletion is a step of the owner of the repository on that day. The agent proposed instructions for it in this PRD, and the user cut them at the gate on 2026-10-03.
- Building the privacy information page. It belongs to `plans_finished/mvp/`; this task changes only the requirement for it.
- The hosting part of the business model in the Kraków presentation, a deliverable outside the app.
- Keeping the app online after the hackathon. The brief does not require it, and the team decided to delete the demo after the results.

## Functional requirements

FR-1. Choice of the hosting. The demo runs on a hosted service reachable at a public link. The live demo, the link in the HackTribe submission and, where the team records it from the link, the video use that same service. The choice is recorded with its reason and its expected cost. It carries what `plans_finished/routing_engine/` and `plans_finished/frontend_stack/` decided, and it allows what the task `DEPLOYMENT` needs from it: a secure connection for the public link, and making the routing service unreachable for the app during the live demo.

FR-2. Permission levels of the agent. The rules of the repository for the agent, in the section Target environment, carry the three permission levels for the hosted demo environment as described in the section Domain rules, the same in every place where those rules are kept.

FR-3. The decision recorded. The entry Target environment for the demo of `docs/standards/decision_registry.md` moves to the resolved section with one sentence about how it turned out and where it lives now, and the open question Q-7 of `plans_finished/mvp/MVP_PLAN.md` is closed with a pointer to this initiative.

FR-4. Privacy information about the deletion. The privacy information requirement FR-20 and its criterion AC-19 of `plans_finished/mvp/MVP_PRD.md` are extended: in the hosted demo the privacy page states, in Polish and English, that the demo and all its data are deleted on 4 October 2026, after the results are announced. The MVP PRD has already passed its gate, so the extension is made with the user's confirmation and marked there as a change coming from this initiative.

## Acceptance criteria

AC-1 (FR-1). The recorded choice names the hosting, the reason for it, its expected cost, how it carries the routing and the frontend chosen in their initiatives, and how it allows a secure connection and an unreachable routing service. It names no address, host or login.

AC-2 (FR-2). Every place that keeps the rules of the repository for the agent carries the same three levels, with the content of the section Domain rules, and none of them still says that a level is defined together with the target environment.

AC-3 (FR-3). The registry entry is in the resolved section and no longer among the open decisions, and Q-7 of the MVP plan points to this initiative as decided.

AC-4 (FR-4). FR-20 and AC-19 of `plans_finished/mvp/MVP_PRD.md` require the statement about the deletion of the demo in both languages, and the MVP PRD records that the change comes from this initiative and was confirmed by the user.

## Domain rules

- Kept personal data in the app: the pseudonym and the password of an account, and the identifier of a vote without an account for 30 days (`docs/product/specification.md`, section Personal data).
- Anyone who gets the public link can create accounts, reports and votes, so the hosted demo holds personal data of people outside the team, jury members included.
- The hosted service and its database are deleted on 4 October 2026, after the results are announced, and no copy of the data is kept. The data therefore lives less than a day, and the 30-day deletion of vote identifiers never has to run in this environment.
- The owner of the repository is responsible for the personal data in the hosted demo and deletes the service and the database. The db person stands the environment up. The owner of the repository gets access to the hosting account that allows the deletion already when the environment is stood up.
- Permission levels of the agent in the hosted demo environment. Without asking: reading the repository, running local tools and tests, and reading the logs of the hosted service. On an explicit request: anything else in that environment, reading personal data from the demo database included. Forbidden unconditionally, even on explicit request: deleting the hosted service or its database, and changing the secrets of the hosting.
- No address, host, login or secret of the hosting enters the repository in any form (`docs/standards/standard_config.md`). The permission levels do not change this.
- The choice of the hosting is recorded in the repository by 22:00 on 3 October 2026, leaving the night for the deployment, checking the link, the video and fixes. The team set this deadline for the choice together with the configuration; whether it still binds the configuration is an open question of the task `DEPLOYMENT`.

## Dependencies and impact on other modules

- `plans_finished/routing_engine/` and `plans_finished/frontend_stack/` decide what the hosting has to carry: a routing engine on our own server or an external routing service, and a static frontend or one rendered on the server. Neither is decided on 2026-10-03, and the choice of FR-1 cannot rely on either before they are.
- The task `DEPLOYMENT` of this initiative waits for the choice of FR-1 and for the skeleton of the app in `plans_finished/mvp/`.
- `plans_finished/local_database/` decides how the team gets PostgreSQL with PostGIS locally; the hosted database has to meet the same database standard as the local one.
- `plans_finished/mvp/MVP_PRD.md` changes in FR-20 and AC-19 (FR-4), and `plans_finished/mvp/MVP_PLAN.md` gets Q-7 closed (FR-3), which lets its phase B continue towards Q-11.
- `docs/standards/decision_registry.md`: the entry Target environment for the demo is resolved by this task. The entry Technology stack and the Python profile of the standards is a blocker of it named in the registry; its backend part is decided in `plans_finished/mvp/MVP_PLAN.md` D-1, its frontend part in `plans_finished/frontend_stack/`.
- The rules of the repository for the agent change in the section Target environment. Every later session of the agent works under the new levels.
- The HarmonyOS port is an open entry of the registry. A public link does not prevent a second client from using the same service, but the demo is deleted after the results, so nothing after 4 October can rely on it.

## Risks and notes

- The deadline of 22:00 holds only if `plans_finished/routing_engine/` and `plans_finished/frontend_stack/` are decided earlier that evening, or if the hosting is chosen in a form that carries every variant they still consider. Otherwise the deadline moves; choosing the hosting on the assumption of one of their variants would be guessing their contract.
- Logs of a hosting platform usually hold the IP addresses of visitors, jury members included. The agent reads them without asking, so that personal data reaches the context of the model without a request each time. The team kept this level knowingly on 2026-10-03.
- Reading personal data from the demo database is allowed to the agent on an explicit request; the team did not put it among the forbidden actions.
- Whether submissions on HackTribe are public is not known, so it is not known how many people outside the team and the jury will get the link.
- Who pays for the hosting, if the chosen one is not free for a day of use, was not settled in the shape. The choice of FR-1 states the expected cost, and a non-zero cost goes to the team before it is accepted.
- The owner of the repository deletes the environment on the day of the results, after a night without sleep. If the deletion slips, the data of the jury stays online without anyone watching it; access granted at setup (Domain rules) makes the step possible, but not certain.
- Nothing here is legal advice about personal data.
