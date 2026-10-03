# Seed: First schema revision of the domain model, split out of the decision on the model

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in the conversation of `plans/dependency_check/`, as an answer to a proposal of fixes the agent made there after a check of cyclic dependencies between the open questions of `plans/mvp/MVP_PLAN.md`. The answer accepts the proposal as a whole, so it is quoted together with the part of the proposal that concerns this initiative and with the closing questions of the proposal. Both are quoted verbatim in Polish, and each is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies. The other parts of the proposal are recorded in `plans/dependency_check/DEPENDENCY_CHECK_REVIEW.md`. One divergence from the original: the agent's message wrote the three arrows of the last paragraph of the proposal as the character U+2192, which `tests/architecture/test_prose_style.py` forbids in every file, fenced blocks included, so they are written here as `->`; nothing else differs.

Agent proposal, the part about this initiative, original in Polish:

```text
## Problem 1: Q-10 i szkielet backendu

**Skąd cykl.** [LOCAL_DATABASE_PLAN.md:53](plans_finished/local_database/LOCAL_DATABASE_PLAN.md:53) (D-8) mówi, że ścieżki plików i konfigurację Alembica ustala work package MVP, bo należą do szkieletu backendu, a ten kształtuje Q-11. W efekcie plan `fact_schema` nie może określić, gdzie i jak powstaje rewizja (FR-15), bez zgadywania. Dlatego:

- plan `fact_schema` zostaje otwarty, więc Q-10 się nie zamyka,
- bez Q-10 plan MVP się nie zamyka i szkielet nie powstaje,
- bez szkieletu nie da się dokończyć planu `fact_schema`.

Pętla się domyka bez względu na to, czy Q-10 zamyka się z planem, czy z implementacją. Sama dopisana reguła zamykania tego nie załatwi.

**Co proponuję: rozdzielić `fact_schema` na dwa zadania**, tak jak demo_environment rozdzielono na DEMO_ENVIRONMENT i DEPLOYMENT:

- **Zadanie `FACT_SCHEMA`** (obecne) to sama decyzja:
  - FR-1 - FR-14, czyli reguły i schemat docelowy zapisany w specyfikacji,
  - nowe wymaganie, które zamyka Q-10 wpisem decyzji D-8 w MVP_PLAN, tak jak FR-5 w routingu i FR-3 w demo_environment.
  - Całość da się zrobić od razu, bo dotyczy tylko dokumentów.
- **Nowe zadanie `SCHEMA_REVISION`** w `plans/fact_schema/`:
  - FR-15, druga połowa AC-13 ("the stored data matches it line by line") oraz AC-1 - AC-12, bo to wszystko testy na zapisanych danych,
  - startuje, gdy work package D-7 zbuduje szkielet z Alembikiem, czyli tak samo jak DEPLOYMENT.

Dlaczego tak, a nie inaczej:
- Zachowuje decyzję z pytania 1 w shape'ie `fact_schema` (rewizję buduje ta inicjatywa) i powtarza wzorzec, który już raz rozbił pętlę.
- Wyciągnięcie szkieletu przed zamknięcie MVP nic nie da, bo według D-8 zależy on od Q-11.
- Oddanie rewizji do work packege'u MVP też przecina pętlę, ale cofa twoją decyzję, więc tylko o tym wspominam.

Koszt: PRD `fact_schema` przeszedł już bramkę, więc zmianę trzeba oznaczyć jako zrobioną po bramce i potrzebne jest twoje potwierdzenie. Rewizja wyląduje po ścieżce Q-1 -> Q-7 -> Q-11 -> szkielet. Tego się nie przeskoczy, skoro szkielet zależy od Q-11.
```

Agent proposal, the part about this initiative, English translation by the agent:

```text
## Problem 1: Q-10 and the backend skeleton

Where the cycle comes from. LOCAL_DATABASE_PLAN.md:53 (D-8) says that the file paths and the Alembic configuration are set by the MVP work package, because they belong to the backend skeleton, which Q-11 shapes. As a result the plan of `fact_schema` cannot state where and how the revision is made (FR-15) without guessing. Therefore:

- the plan of `fact_schema` stays open, so Q-10 does not close,
- without Q-10 the MVP plan does not close and the skeleton is not built,
- without the skeleton the plan of `fact_schema` cannot be finished.

The loop closes whether Q-10 closes with the plan or with the implementation. An added closing rule alone will not fix it.

What I propose: split `fact_schema` into two tasks, the way demo_environment was split into DEMO_ENVIRONMENT and DEPLOYMENT:

- The task `FACT_SCHEMA` (the current one) is the decision alone:
  - FR-1 - FR-14, that is the rules and the target schema written in the specification,
  - a new requirement that closes Q-10 with a decision entry D-8 in MVP_PLAN, like FR-5 in routing and FR-3 in demo_environment.
  - All of it can be done right away, because it concerns documents only.
- A new task `SCHEMA_REVISION` in `plans/fact_schema/`:
  - FR-15, the second half of AC-13 ("the stored data matches it line by line") and AC-1 - AC-12, because all of these are tests on the stored data,
  - it starts when the work package of D-7 builds the skeleton with Alembic, the same way as DEPLOYMENT.

Why this and not something else:
- It keeps the decision of question 1 in the shape of `fact_schema` (this initiative builds the revision) and repeats the pattern that already broke a loop once.
- Pulling the skeleton ahead of the closing of the MVP changes nothing, because under D-8 it depends on Q-11.
- Handing the revision to an MVP work package also cuts the loop, but reverses your decision, so I only mention it.

Cost: the PRD of `fact_schema` has already passed its gate, so the change has to be marked as made after the gate and needs your confirmation. The revision lands after the path Q-1 -> Q-7 -> Q-11 -> skeleton. That cannot be skipped, since the skeleton depends on Q-11.
```

Agent proposal, the closing questions, original in Polish:

```text
## Do decyzji

1. Podział `fact_schema` (rekomendowany) czy oddanie rewizji do MVP? Czy nazwa `SCHEMA_REVISION` pasuje?
2. Czy routing dopasowuje się do FR-5?
3. Kto odbiera rolę moderatora?

Do tej pory nic nie zmieniłem. Odpowiadasz w imieniu osób od bazy i backendu, jak wcześniej? Jeśli tak, daj znać, które punkty wdrożyć.
```

Agent proposal, the closing questions, English translation by the agent:

```text
## To decide

1. Splitting `fact_schema` (recommended) or handing the revision to the MVP? Does the name `SCHEMA_REVISION` fit?
2. Does routing adapt to FR-5?
3. Who removes the moderator role?

So far I have changed nothing. Are you answering for the db and backend people, as before? If so, let me know which points to apply.
```

User answer, original in Polish:

```text
wprowadź te wszystkie poprawki
```

User answer, English translation by the agent:

```text
apply all these fixes
```
