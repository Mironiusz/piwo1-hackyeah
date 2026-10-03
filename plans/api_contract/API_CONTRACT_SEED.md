# Seed: Contract of the programming interface between the frontend and the backend of the MVP, as an initiative for the backend person

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one conversation, during phase B of `plan-prd` for `plans/mvp/`, right after the agent set up one initiative per delegated technical decision. It consists of two messages from the user, followed by the agent questions they led to and the user's answers. Everything is quoted verbatim in Polish, the options offered with a question being part of the question, and each item is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

User message 1, original in Polish:

```text
i powiedz, które inicjatywy dla jakiej osoby - frotnend, db, import, zewnętrzne api, backend
```

User message 1, English translation by the agent:

```text
and say which initiatives are for which person - frontend, db, import, external api, backend

(Translator's note: "frotnend" in the original is translated as "frontend".)
```

User message 2, original in Polish:

```text
i dodaj też jeszcze jedną na backend
```

User message 2, English translation by the agent:

```text
and also add one more for the backend
```

Agent question 1, original in Polish:

```text
Czego ma dotyczyć dodatkowa inicjatywa dla osoby od backendu?

Opcje:
- Kontrakt API front-back: Endpointy, kształt żądań i odpowiedzi, kody błędów między frontem a backendem (i ewentualnie drugim klientem HarmonyOS). Kategoria blokująca: stabilność kontraktu API.
- Model domeny i schemat bazy: Fakty, głosy, statusy, geostrefy, flagi, ukrycie przez moderatora, odpięcie przy usunięciu konta. Kategorie blokujące: schemat bazy, forma zmiany schematu.
- Architektura backendu i worker: Warstwy api/service/data/worker, zadania okresowe (odświeżanie OSM, kasowanie identyfikatorów głosów po 30 dniach), konfiguracja i logowanie wg profilu Pythona.
- Identyfikator głosu bez konta: Z czego dokładnie liczony jest nieodwracalny identyfikator (IP + cechy przeglądarki), czy z sekretem, jak jest kasowany po 30 dniach. Kategoria blokująca: dane osobowe.
```

Agent question 1, English translation by the agent:

```text
What should the additional initiative for the backend person be about?

Options:
- Front-back API contract: Endpoints, the shape of requests and responses, error codes between the frontend and the backend (and possibly a second, HarmonyOS client). Blocking category: stability of the API contract.
- Domain model and database schema: Facts, votes, statuses, geozones, flags, hiding by a moderator, detaching on account deletion. Blocking categories: database schema, form of a schema change.
- Backend architecture and worker: The api/service/data/worker layers, periodic tasks (refreshing OSM, deleting the vote identifiers after 30 days), configuration and logging according to the Python profile.
- Identifier of a vote without an account: What exactly the irreversible identifier is computed from (IP + browser characteristics), whether with a secret, how it is deleted after 30 days. Blocking category: personal data.
```

User answer 1, original in Polish:

```text
Kontrakt API front-back
```

User answer 1, English translation by the agent:

```text
Front-back API contract
```

Agent question 2, original in Polish:

```text
Nazwa nowej inicjatywy: plans/api_contract -> prefiks API_CONTRACT (właściciel: backend, konsultuje frontend). SEED będzie dosłownym zapisem tej części rozmowy, SHAPE to szkielet jak w pozostałych, regulator C:40. Pasuje?

Opcje:
- Pasuje, twórz: Zakładam plans/api_contract z API_CONTRACT_SEED.md i API_CONTRACT_SHAPE.md.
- Inna nazwa: Podasz własną nazwę katalogu i prefiksu.
```

Agent question 2, English translation by the agent:

```text
Name of the new initiative: plans/api_contract -> prefix API_CONTRACT (owner: backend, frontend consulted). The SEED will be a verbatim record of this part of the conversation, the SHAPE a skeleton like in the others, regulator C:40. Does it fit?

Options:
- Fits, create: I set up plans/api_contract with API_CONTRACT_SEED.md and API_CONTRACT_SHAPE.md.
- Another name: You give your own name of the directory and the prefix.
```

User answer 2, original in Polish:

```text
Pasuje, twórz
```

User answer 2, English translation by the agent:

```text
Fits, create
```
