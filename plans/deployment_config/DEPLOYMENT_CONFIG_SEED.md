# Seed: Deployment configuration of the MVP demo, split out of the task DEPLOYMENT

Source: conversation with the user
Date: 2026-10-04

## Verbatim content

The request was made in Polish, in one conversation, at the start of phase B of `plan-prd` for the task `DEPLOYMENT` of `plans/deployment/`. The user interrupted the agent while it was gathering facts for the implementation plan. The agent asked one clarifying question, and the user answered with one of the options offered. All three parts are quoted verbatim in Polish, each followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies. The only change to the original is in the agent question: its typographic quotation marks are written as plain quotation marks, because `docs/standards/standard_formatting.md` forbids the closing one in the repository.

User message, original in Polish:

```text
Wróć, teraz tylko dokumentacja, a utworzenie właściwych to będzie w osobnym task
```

User message, English translation by the agent:

```text
Go back, now only documentation, and creating the actual ones will be in a separate task
```

Agent question, original in Polish, with the options offered:

```text
Co zostaje w tym tasku jako "tylko dokumentacja"?

Opcje:
- FR-7 + projekt wdrożenia: Zostaje FR-7 (CLAUDE.md, AGENTS.md, D-8, D-10, rejestr decyzji, AI_WORKFLOW.md) oraz spisany projekt wdrożenia: jakie serwisy, wolumeny, porty, restart, czyszczenie bazy, loader i checklista. Osobny task robi z tego pliki Compose i instrukcję dla ludzi, gdy będzie kod.
- Tylko FR-7: Zostaje wyłącznie przepięcie dokumentów na Twój serwer. FR-1 do FR-6, łącznie z projektem i instrukcją, przechodzą w całości do osobnego taska.
- FR-7 + instrukcja: Zostaje FR-7 i pisana instrukcja wdrożenia (FR-1 bez plików, plus FR-5 i FR-6 jako kroki w instrukcji). Pliki Compose robi osobny task, a instrukcja zostanie dopasowana do nich później.
```

Agent question, English translation by the agent:

```text
What stays in this task as "only documentation"?

Options:
- FR-7 + deployment design: FR-7 stays (CLAUDE.md, AGENTS.md, D-8, D-10, the decision registry, AI_WORKFLOW.md), together with the written design of the deployment: which services, volumes, ports, restart, emptying the database, the loader and the checklist. A separate task turns it into the Compose files and the instructions for people once the code exists.
- Only FR-7: Only rewriting the documents to your server stays. FR-1 to FR-6, the design and the instructions included, move as a whole to the separate task.
- FR-7 + instructions: FR-7 stays, together with the written deployment instructions (FR-1 without the files, plus FR-5 and FR-6 as steps of the instructions). The separate task makes the Compose files, and the instructions are adjusted to them later.
```

User answer, original in Polish:

```text
FR-7 + instrukcja
```

User answer, English translation by the agent:

```text
FR-7 + instructions
```
