# Seed: Backend architecture with the worker, Q-11 of the MVP plan

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one message of one conversation, by the user, who then confirmed the initiative name `backend_architecture` and the task prefix `BACKEND_ARCHITECTURE` proposed by the agent. The message is quoted verbatim in Polish and followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

User message, original in Polish:

```text
Q-11, zaczynamy powoli
```

User message, English translation by the agent:

```text
Q-11, we start slowly
```

The message names Q-11 of `plans/mvp/MVP_PLAN.md`, section Open questions. That entry, as it stood when the request was made, is quoted below verbatim, so that this record keeps what was asked for if the MVP plan changes later. The quote is in English in the original.

```text
Q-11. The backend architecture with the worker, owner: backend. On 2026-10-03 the user decided, in phase B of `plans_finished/api_contract/`, that it is decided in a separate initiative set up later, and that the implementation of the operations of D-12 goes with it. It decides what the settled decisions leave to it: how the one backend process of D-3 is started, and the names of the modules and functions of the address search (`plans_finished/geocoding/GEOCODING_PLAN.md` D-2); the form of the trigger of the import and refresh run of D-4 and the machine it runs on; the names of the module and the constants of the tag rule of D-5 and of its functions (`plans_finished/osm_barrier_mapping/OSM_BARRIER_MAPPING_PLAN.md` D-14, D-16); how the backend process builds the route graph of D-9 when it starts and rebuilds it when the copy in use changes; the placement of the backend process, the worker, PostgreSQL with PostGIS and the static frontend on the server of D-10, and whether the import runs there or on a team machine; the periodic task of the worker that clears the identifier of a vote without an account 30 days after the vote (`docs/product/schema.md`, section Who writes what, part of D-11); and the structure that implements the operations of D-12. The work package of D-7, the task `SCHEMA_REVISION` of `plans/schema_revision/` and the task `DEPLOYMENT` of `plans/deployment/` wait for it (Risks). Q-11 was split out of the former Q-10 on 2026-10-03 at the user's request, when Q-10 was narrowed to the domain model, because the former condition of Q-10, "once Q-1 - Q-9 are settled", blocked the domain model on decisions it does not depend on; the owners of the former Q-10 and of Q-11 were proposed by the agent.
```
