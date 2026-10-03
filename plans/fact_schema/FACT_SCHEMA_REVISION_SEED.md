# Seed: First schema revision of facts and votes with its tests, split out of the decision on the domain model

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one conversation, as answers to two questions the agent asked together in phase B of `plan-prd` for the task `FACT_SCHEMA` of `plans/fact_schema/`. The first answer is an offered option followed by a remark of the user, the second is an offered option, so both are quoted together with the agent questions they answer. All are quoted verbatim in Polish, the options offered with each question being part of the question, and each is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

Agent question 1, original in Polish:

```text
Jak podzielić Q-10, skoro rewizja i testy na bazie nie mają jeszcze szkieletu backendu (Q-11) ani lokalnej bazy (Q-4, z blokującym pytaniem o konto tworzące PostGIS)?

Opcje:
- Dwa etapy (Recommended): Plan teraz: docs/product/schema.md z docelowym DDL, propozycja wersji 4 specyfikacji (M4, M9, M11 + schema.md jako część spec), zmiana AC-6 w MVP_PRD, zamknięcie Q-10 w MVP_PLAN. Q-9 (api_contract) dostaje od razu nazwy zasobów i statusów. Rewizja Alembic, kod reguł i krytyczne testy AC-1..AC-12 idą do drugiego etapu, który startuje po Q-4 i szkielecie. Wymaga dopisania podziału do PRD (FR-15 i AC-1..AC-12 przechodzą do etapu 2).
- Plan buduje też szkielet: Ten plan dodaje minimalny backend: pakiet, konfigurację, połączenie, alembic env, conftest, docker compose z PostGIS. Wszystko domknięte w jednym przebiegu, ale przejmuje decyzje Q-4 i Q-11 innych ról i zgaduje ich kontrakty (nazwy modułów, konto PostGIS).
- Jeden plan, czekamy: Piszę cały plan, ale kroki rewizji i testów zostają w Open questions, aż Q-4 i szkielet się zamkną. Plan zostaje 'in progress', plan-implement nie ruszy nawet części z dokumentacją.
```

Agent question 1, English translation by the agent:

```text
How do we split Q-10, given that the revision and the database tests have neither a backend skeleton (Q-11) nor a local database (Q-4, with a blocking question about the account that creates PostGIS) yet?

Options:
- Two stages (Recommended): The plan now: docs/product/schema.md with the target DDL, a proposal of version 4 of the specification (M4, M9, M11 + schema.md as part of the spec), the change of AC-6 in MVP_PRD, closing Q-10 in MVP_PLAN. Q-9 (api_contract) gets the names of the resources and statuses at once. The Alembic revision, the code of the rules and the critical tests AC-1..AC-12 go to a second stage, which starts after Q-4 and the skeleton. Requires adding the split to the PRD (FR-15 and AC-1..AC-12 move to stage 2).
- The plan also builds the skeleton: This plan adds a minimal backend: package, configuration, connection, alembic env, conftest, docker compose with PostGIS. Everything closed in one run, but it takes over the decisions of Q-4 and Q-11 of other roles and guesses their contracts (module names, the PostGIS account).
- One plan, we wait: I write the whole plan, but the steps of the revision and the tests stay in Open questions until Q-4 and the skeleton are closed. The plan stays 'in progress', plan-implement will not start even the documentation part.
```

User answer 1, original in Polish:

```text
Dwa etapy, ale pamiętaj że importer i backend muszą współdzielić schemat (przynajmniej część schematu)
```

User answer 1, English translation by the agent:

```text
Two stages, but remember that the importer and the backend have to share the schema (at least part of the schema)
```

Agent question 2, original in Polish:

```text
Jeśli dwa etapy, gdzie ma żyć etap 2 (rewizja + kod reguł + testy krytyczne)?

Opcje:
- Drugie zadanie w fact_schema (Recommended): plans/fact_schema/FACT_SCHEMA_REVISION_SEED/PLAN.md, właściciel nadal db. Zgodne z Twoją decyzją z pytania 1 shape'u, że ta inicjatywa buduje pierwszą rewizję. Startuje, gdy Q-4 i szkielet istnieją.
- Pakiet roboczy plans/mvp/: Jak zrobiły osm_data_source i geocoding: fact_schema kończy się na decyzji i schema.md, budowa idzie do work package MVP. Odwraca decyzję z pytania 1 shape'u i wymaga poprawki wpisu w decision_registry.
```

Agent question 2, English translation by the agent:

```text
If two stages, where does stage 2 (revision + code of the rules + critical tests) live?

Options:
- A second task in fact_schema (Recommended): plans/fact_schema/FACT_SCHEMA_REVISION_SEED/PLAN.md, the owner is still db. Consistent with your decision in question 1 of the shape that this initiative builds the first revision. It starts when Q-4 and the skeleton exist.
- A work package of plans/mvp/: As osm_data_source and geocoding did: fact_schema ends with the decision and schema.md, the build goes to a work package of the MVP. Reverses the decision of question 1 of the shape and requires correcting the entry in decision_registry.
```

User answer 2, original in Polish:

```text
Drugie zadanie w fact_schema (Recommended)
```

User answer 2, English translation by the agent:

```text
A second task in fact_schema (Recommended)
```
