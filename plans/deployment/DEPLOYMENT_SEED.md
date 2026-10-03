# Seed: Deployment of the MVP demo to the chosen hosting, split out of the demo environment decision

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one conversation, as an answer to a question the agent asked in phase B of `plan-prd` for the task `DEMO_ENVIRONMENT` of `plans/demo_environment/`. The answer is one of the offered options, so it is quoted together with the agent question it answers. Both are quoted verbatim in Polish, the options offered with the question being part of the question, and each is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

Agent question, original in Polish:

```text
Jak rozciąć zależność między tym planem a architekturą backendu w plans/mvp?

Opcje:
- Drugie zadanie tutaj (Recommended): Ten task zostaje przy decyzji: FR-1, FR-5, FR-6, FR-7. FR-2..FR-4 idą do nowego zadania DEPLOYMENT w plans/demo_environment, startującego, gdy jest szkielet aplikacji. Wracam do PRD tego taska, żeby je przenieść.
- Przenieś do plans/mvp: FR-2..FR-4 trafiają do PRD MVP jako rozszerzenie (jak FR-7), a pakiet wdrożeniowy budujecie razem z aplikacją w planie MVP. Tu zostaje sama decyzja.
- Jeden plan, czekamy: Plan zostaje 'in progress' z otwartymi pytaniami o routing, frontend i Q-10. Q-7 w MVP trzeba by zamknąć wyjątkowo wcześniej, inaczej pętla zostaje.
```

Agent question, English translation by the agent:

```text
How do we cut the dependency between this plan and the backend architecture in plans/mvp?

Options:
- A second task here (Recommended): This task stays with the decision: FR-1, FR-5, FR-6, FR-7. FR-2..FR-4 go to a new task DEPLOYMENT in plans/demo_environment, which starts when the skeleton of the app exists. I go back to the PRD of this task to move them.
- Move to plans/mvp: FR-2..FR-4 go to the MVP PRD as an extension (like FR-7), and you build the deployment package together with the app in the MVP plan. Only the decision stays here.
- One plan, we wait: The plan stays 'in progress' with open questions about routing, the frontend and Q-10. Q-7 in the MVP would have to be closed early as an exception, otherwise the loop stays.
```

User answer, original in Polish:

```text
Drugie zadanie tutaj (Recommended)
```

User answer, English translation by the agent:

```text
A second task here (Recommended)
```
