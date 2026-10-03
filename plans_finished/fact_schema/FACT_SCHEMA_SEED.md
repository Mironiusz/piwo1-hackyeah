# Seed: Shape of Q-10 of the MVP plan, the domain model and database schema of facts and votes

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was one short message in English, in which "Q-10" refers to the open question Q-10 of `plans/mvp/MVP_PLAN.md`. The name of the initiative was then chosen by the user from options the agent offered; the agent question was asked in Polish and is quoted verbatim, the options offered being part of the question, followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

User request:

```text
Q-10 shape
```

Agent question 1, original in Polish:

```text
Gdzie założyć shape dla Q-10 i z jakim prefiksem? Regulator domyślnie C:40, bo w prośbie nie ma wartości.

Opcje:
- plans/mvp/ -> DOMAIN_MODEL (Recommended): Osobne zadanie w inicjatywie mvp (DOMAIN_MODEL_SEED.md, DOMAIN_MODEL_SHAPE.md), tak jak DEPLOYMENT w demo_environment. Zgodne z zapisem 'Decided in this plan' w Q-10 i z tym, że model został przy plans/mvp/.
- plans/domain_model/ -> DOMAIN_MODEL: Nowa inicjatywa, jak Q-1..Q-9. Wymaga poprawienia zapisu Q-10 w MVP_PLAN.md ('Decided in this plan' -> odesłanie do plans/domain_model/).
- plans/fact_schema/ -> FACT_SCHEMA: Nowa inicjatywa z nazwą akcentującą schemat bazy faktów i głosów zamiast 'modelu domenowego'.
```

Agent question 1, English translation by the agent:

```text
Where should the shape for Q-10 be set up, and with what prefix? The regulator is C:40 by default, because the request carries no value.

Options:
- plans/mvp/ -> DOMAIN_MODEL (Recommended): A separate task in the initiative mvp (DOMAIN_MODEL_SEED.md, DOMAIN_MODEL_SHAPE.md), like DEPLOYMENT in demo_environment. Consistent with the entry 'Decided in this plan' in Q-10 and with the model having stayed with plans/mvp/.
- plans/domain_model/ -> DOMAIN_MODEL: A new initiative, like Q-1..Q-9. Requires correcting the entry of Q-10 in MVP_PLAN.md ('Decided in this plan' -> a pointer to plans/domain_model/).
- plans/fact_schema/ -> FACT_SCHEMA: A new initiative with a name stressing the database schema of facts and votes instead of the 'domain model'.
```

User answer 1:

```text
plans/fact_schema/ -> FACT_SCHEMA
```
