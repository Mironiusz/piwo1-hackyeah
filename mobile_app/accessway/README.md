# AccessWay - Kraków bez barier (aplikacja HarmonyOS)

Aplikacja na wyzwanie "Kraków bez barier" (HackYeah 2026). Na razie działa w całości na urządzeniu: sieć piesza, trasy, ocena odcinków, zgłoszenia, głosy i konta liczą się lokalnie, a warstwa danych jest gotowa na podłączenie API zespołu.

## Uruchomienie na emulatorze (z katalogu `hujawei`)

Instalacja emulatora i narzędzi od zera (Linux i Windows): `docs/EMULATOR_SETUP.md`.

```bash
make emulator-fast        # albo make emulator, jeśli emulator jeszcze nie działa
make osm                  # opcjonalnie: prawdziwe dane OSM centrum Krakowa (wymaga internetu)
make run                  # build + podpis + instalacja + uruchomienie
make logs                 # logi aplikacji przez 60 s
make uninstall           # odinstalowanie (czyści zapisane zgłoszenia i ustawienia)
make test                 # testy logiki domenowej na Node
```

Bez `make osm` aplikacja używa schematycznej próbki okolic Tauron Areny (`tools/accessway_sample.py`), oznaczonej w aplikacji jako dane przykładowe.

## Co jest w aplikacji

Ekrany odwzorowują makiety zespołu "Widoki MVP: makiety" (artboardy System i V-2 do V-14):

- V-2 Potrzeby: trzy gotowe zestawy, listy "Unikam" i "Potrzebuję", przyciski Pomiń i Gotowe; potrzeby zostają tylko na urządzeniu.
- V-3 Mapa faktów: wyszukiwanie celu, przełącznik "Z moich potrzeb / Wszystkie", fakty w widocznym miejscu ze statusem, źródłem i datą.
- V-4 i V-8 Planowanie trasy i wyszukiwanie adresu: start i cel z wyszukiwarki (dopiero po Enter albo przycisku), z mapy albo z lokalizacji; błąd usługi tras bez trasy zgadywanej.
- V-5 Wynik trasy: schemat trasy, kafelki, mapa w czterech stanach odcinków, grupy "Z Twoich potrzeb", "Dodatkowe bariery", "Udogodnienia na trasie", "Czego nie wiemy", trasa alternatywna dla niezweryfikowanej bariery; warianty bez oceny i bez trasy wolnej od barier.
- V-6 Szczegóły faktu: głos "Nadal jest" albo "Już nie ma" raz na dobę, sprzeczność ze stanem w OpenStreetMap, zgłoszenie do moderacji.
- V-7 Zgłaszanie bariery, udogodnienia albo obszaru krok po kroku, ze sprawdzeniem faktów tego samego rodzaju w promieniu 15 m.
- V-10 do V-14: menu, konto z pseudonimem i hasłem, informacja o prywatności, o danych, moderacja.

Nazwa produktu nie jest jeszcze wybrana, więc nagłówek pokazuje "[Nazwa produktu]" jak makiety (stała `PRODUCT_NAME` w `data/AppModel.ets`).

## Dane i podłączenie API

Ekrany korzystają wyłącznie z interfejsu `Repository` (`entry/src/main/ets/data/Repository.ets`). Są dwie implementacje:

- `LocalRepository`: wszystko na urządzeniu, z danych dołączonych do aplikacji (domyślnie);
- `ApiRepository`: API zespołu według `docs/product/api_contract.md` w repozytorium piwo1-hackyeah.

Wybór zależy od jednego pliku: `entry/src/main/resources/rawfile/config/api.json`.

```json
{ "base_url": "http://203.0.113.10", "timeout_ms": 15000 }
```

- `base_url` pusty: praca bez serwera.
- `base_url` z adresem: adres serwera bez `/api` i bez ukośnika na końcu; ścieżki operacji dokleja aplikacja.
- Serwer na komputerze, na którym działa emulator: `http://10.0.2.2:<port>` (adres hosta widziany z QEMU).
- Po zmianie pliku: `make run` (plik jest wbudowany w pakiet).

Co gdzie jest:

| Plik | Rola |
|---|---|
| `data/ApiConfig.ets` | odczyt `config/api.json` |
| `data/ApiClient.ets` | HTTP, nagłówek `Authorization: Bearer`, odnowiony token z `Session-Token`, kody błędów na komunikaty |
| `data/ApiTypes.ets` | kształty JSON z kontraktu, jeden do jednego |
| `data/ApiMapping.ets` | tłumaczenie kontraktu na typy aplikacji (testy w `entry/src/test/ApiMapping.test.ets`) |
| `data/ApiRepository.ets` | operacje kontraktu, każda opisana nazwą i ścieżką |

Operacje kontraktu i ich miejsce w aplikacji: `plan_route` (wynik trasy), `search_address` (wyszukiwanie), `read_osm_copy` (data danych), `list_facts_in_area` (mapa faktów, pobierana na nowo po przesunięciu mapy), `read_fact`, `cast_vote`, `flag_fact` (szczegóły faktu), `find_nearby_facts`, `create_fact` (zgłaszanie), `create_account`, `log_in`, `read_own_account`, `delete_own_account` (konto), `list_flagged_facts`, `hide_fact`, `restore_fact` (moderacja).

Różnice między kontraktem a makietami, rozwiązane w aplikacji:

- Kontrakt nie zwraca własnego głosu, więc aplikacja pamięta głosy z tego urządzenia z ostatniej doby (`api_my_votes.json`).
- Kontrakt nie ma odwrotnego wyszukiwania i nie podaje ulicy faktu, więc z API wiersze faktów nie mają nazwy ulicy, a punkt z mapy nazywa się "Punkt wskazany na mapie".
- `list_facts_in_area` zwraca też fakty nieaktualne; makieta System mówi, że fakt nieaktualny nie jest nigdzie pokazywany, więc aplikacja je pomija.
- Trasa alternatywna pochodzi z pola `alternative` tej samej odpowiedzi; "Pokaż" nie wysyła drugiego żądania.
- Mapa bazowa (ulice, budynki) nadal pochodzi z danych w aplikacji; `make osm` dołącza prawdziwe dane centrum Krakowa.

Serwer działa po zwykłym HTTP, więc `resources/base/profile/network_config.json` zezwala na ruch bez TLS.

W wersji lokalnej rolę moderatora dostaje konto o pseudonimie `moderator`; z API rolę nadaje serwer. Konta, głosy i zgłoszenia wersji lokalnej są zapisane tylko na urządzeniu; `make uninstall` je czyści.

## Mapa z kafelków wektorowych (mock serwera)

Podkład mapy może pochodzić z kafelków wektorowych Krakowa, tak jak w decyzji D-5 `plans_finished/frontend_stack/` w piwo1-hackyeah (archiwum PMTiles z buildu Protomaps). Do czasu serwera projektu kafelki podaje mock:

```bash
make tiles          # pobiera mapę Krakowa do tiles/krakow.pmtiles (około 35 MB, wymaga internetu)
make tiles-sample   # albo mała mapa schematycznej próbki, bez internetu
make mock           # serwer kafelków na porcie 8090
make run            # aplikacja; emulator widzi komputer pod 10.0.2.2
```

Adres serwera kafelków to pole `tiles_url` w `entry/src/main/resources/rawfile/config/api.json` (domyślnie `http://10.0.2.2:8090`). Gdy serwer nie odpowiada albo pole jest puste, mapa rysuje podkład z danych w aplikacji, jak wcześniej.

Mock (`tools/mock_backend/server.py`, sama biblioteka standardowa Pythona) udostępnia:

| Ścieżka | Dla kogo |
|---|---|
| `GET /tiles/info.json` | zakres powiększeń, granice, atrybucja, data buildu |
| `GET /tiles/{z}/{x}/{y}.json` | aplikacja HarmonyOS: kafelek gotowy do rysowania (format `render-v2`): geometria pogrupowana na zieleń, wodę, budynki i trzy rangi ulic, uproszczona do około jednego punktu ekranu, w całkowitych punktach kafelka 0..512 |
| `GET /tiles/krakow.pmtiles` | aplikacja webowa (MapLibre): całe archiwum z obsługą nagłówka `Range` |

Aplikacja wybiera poziom kafelków do skali mapy, pobiera je w tle (najwyżej 4 naraz, pamięć 96 kafelków), a brakujący zastępuje kafelkiem nadrzędnym. Rysuje zieleń, wodę, budynki (od poziomu 14), ulice w trzech szerokościach i ich nazwy, w kolorach z makiet.

Wydajność: kafelek ma na ekranie 512-1024 punktów, więc przy oddaleniu jest ich mniej, a serwer pomija to, czego na danym poziomie nie widać (ścieżki poniżej 14, ulice osiedlowe poniżej 13). Podkład rysuje się raz do bitmapy większej od ekranu o 40% z każdej strony; przesuwanie i szczypanie tylko przesuwa i skaluje tę bitmapę, a od nowa rysuje się ona dopiero po wyjściu poza margines, zmianie skali o ponad 25% (w trakcie szczypania dwukrotnej) albo po nadejściu nowych kafelków (zbieranych w paczki co 90 ms). Na archiwum Krakowa kafelek JSON jest 5-11 razy mniejszy niż w pierwszej wersji (np. poziom 12: 916 KB do 113 KB).

Uwaga: lokalna trasa i fakty przykładowe leżą na schematycznej sieci próbki, która nie pokrywa się z prawdziwymi ulicami. Na prawdziwej mapie Krakowa (`make tiles`) trasa z `LocalRepository` jest więc przesunięta względem ulic; z API trasy przychodzą z prawdziwej sieci i pasują do kafelków. Do pokazu bez API pasuje `make tiles-sample`.

## Scenariusz demonstracji (próbka okolic Tauron Areny)

1. Potrzeby: "Poruszam się na wózku", Gotowe.
2. Mapa: "Dokąd idziesz?", wpisz "ogród", Szukaj, wybierz Ogród Doświadczeń. Start: Adres, "tauron", Szukaj, wybierz Tauron Arena Kraków. Wyznacz trasę.
3. Wynik: potwierdzony wysoki krawężnik na ul. Stanisława Lema i niezweryfikowane schody przy al. Pokoju z trasą alternatywną; "Czego nie wiemy" pokazuje odcinki bez danych.
4. Cel "Park Lotników Polskich": jedyna droga prowadzi przez schody z OpenStreetMap, więc aplikacja mówi, że trasy bez barier nie ma.
5. Potrzeby bez żadnej bariery: trasa bez oceny odcinków.
6. Fakt "Wysoki krawężnik" przy ul. Medweckiego: OpenStreetMap podaje tu obniżony krawężnik.

## Źródła i licencje

- Dane mapy: OpenStreetMap, licencja ODbL, (c) współtwórcy OpenStreetMap, pobierane przez Overpass API.
- Krój pisma: Barlow Semi Condensed (Regular, SemiBold, Bold) i Barlow Condensed Bold, SIL Open Font License (`rawfile/fonts/OFL-Barlow.txt`).
- Ikony: Material Symbols, Apache License 2.0 (`rawfile/icons/LICENSE.txt`), oraz proste ikony konturowe narysowane dla tej aplikacji.
