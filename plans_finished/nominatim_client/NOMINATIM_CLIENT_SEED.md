# Seed: Testing the public Nominatim instance and writing the interface to it

Source: conversation with the user
Date: 2026-10-03

## Verbatim content

The request was made in Polish, in one conversation, in two messages of the user and one answer to a question the agent asked about the name of the initiative. The second message refers to the Nominatim discussed in the first message and in the agent's answer to it, which is not quoted here; that answer concluded that Nominatim is needed only for the address search of `docs/product/specification.md` M2 and M5, as decided in `plans_finished/geocoding/`. Each message is quoted verbatim in Polish, the agent question together with the options offered with it, and each is followed by an English translation by the agent. The translation is not part of the verbatim record; in case of doubt the Polish original applies.

User message 1, original in Polish:

```text
przejrzyjmy, czy do czegokolwiek może nam być potrzebny nominatim, jeśli wybraliśmy:

* OpenStreetMap (z Geofabrik)
* Przystanki autobusowe i tramwajowe:: https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0

oraz valhallę
```

User message 1, English translation by the agent:

```text
let's review whether we might need nominatim for anything at all, if we chose:

* OpenStreetMap (from Geofabrik)
* Bus and tram stops:: https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0

and valhalla
```

User message 2, original in Polish:

```text
załóż inicjatywę na przetestowanie tego nominatima i napisanie na niego interfejsu
```

User message 2, English translation by the agent:

```text
set up an initiative for testing this nominatim and writing an interface for it
```

Agent question, original in Polish:

```text
Jak nazwać inicjatywę? `plans_finished/geocoding/` zdecydowało, CO budujemy, ale samo budowanie wyłączyło ze swojego zakresu.

Opcje:
- nominatim_client (Recommended): Nowa inicjatywa plans/nominatim_client/ z prefiksem NOMINATIM_CLIENT. Zakres: przetestowanie Nominatima i napisanie integracji według decyzji z geocoding. Archiwum zostaje nietknięte.
- address_search: Nowa inicjatywa plans/address_search/ z prefiksem ADDRESS_SEARCH. Szerszy zakres nazwy: cała funkcja wyszukiwania adresu, a nie tylko klient Nominatima.
- Wznowienie geocoding: plans_finished/geocoding/ wraca do plans/ z wpisem o wznowieniu w review, a wywiad kontynuuje istniejący shape. Zmienia to jego zakres, bo tam budowanie było poza zakresem.
```

Agent question, English translation by the agent:

```text
What should the initiative be called? `plans_finished/geocoding/` decided WHAT we build, but left the building itself out of its scope.

Options:
- nominatim_client (Recommended): A new initiative plans/nominatim_client/ with the prefix NOMINATIM_CLIENT. Scope: testing Nominatim and writing the integration according to the decisions of geocoding. The archive stays untouched.
- address_search: A new initiative plans/address_search/ with the prefix ADDRESS_SEARCH. A broader scope of the name: the whole address search feature, not only the Nominatim client.
- Resumption of geocoding: plans_finished/geocoding/ returns to plans/ with a resumption entry in the review, and the interview continues the existing shape. This changes its scope, because building was out of scope there.
```

User answer, original in Polish:

```text
nominatim_client (Recommended)
```

User answer, English translation by the agent:

```text
nominatim_client (Recommended)
```
