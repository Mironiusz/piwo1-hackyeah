/**
 * Polish words of the deck: the material of the Kraków bez barier submission on HackTribe, which the challenge
 * requires in Polish. This is the only file of the code unit with Polish text. The notes of each slide are the spoken
 * text of the Kraków pitch.
 *
 * The structure must match `src/content/en.js` key for key; `npm run lint` checks it (`scripts/content-check.mjs`).
 */
export default {
  page: {
    title: 'EnableMe - Kraków bez barier',
    icons: { arrow: 'do' },
  },
  slides: {
    title: {
      summary: 'tytuł: EnableMe',
      kicker: 'HackYeah 2026 - Kraków bez barier',
      heading: 'EnableMe',
      subtitle: 'Sprawdź trasę, zanim wyjdziesz z domu',
      notes: '<p>Dzień dobry, jesteśmy zespołem EnableMe. Pokażemy aplikację, która pozwala sprawdzić pieszą trasę w Krakowie, zanim się nią pójdzie.</p>',
    },
    problem: {
      summary: 'problem: o barierze dowiadujesz się na miejscu',
      heading: 'O barierze dowiadujesz się na miejscu',
      who: 'Osoby na wózku, rodzice z wózkiem dziecięcym, osoby, którym trudno chodzić',
      barriers: ['schody', 'wysoki krawężnik', 'zła nawierzchnia', 'stromy podjazd', 'wąskie przejście'],
      gap: 'Mapa mówi: dostępne albo niedostępne. Nie mówi, skąd to wie ani z kiedy jest ta informacja.',
      notes: `<p>Osoba na wózku, rodzic z wózkiem dziecięcym albo ktoś, komu trudno chodzić, o schodach czy wysokim krawężniku zwykle dowiaduje się dopiero na miejscu.</p>
<p>[click] Jeśli w ogóle ma jakąś mapę, to dostaje jedną etykietę: dostępne albo niedostępne. Nie wie, skąd ta informacja pochodzi, z kiedy jest i czy ktoś ją sprawdził.</p>`,
    },
    solution: {
      summary: 'rozwiązanie: potrzeby, trasa, fakty',
      heading: 'Potrzeby, trasa, fakty',
      steps: [
        { head: 'Potrzeby', text: 'Czego unikasz i czego potrzebujesz. Bez pytania o niepełnosprawność.' },
        { head: 'Trasa', text: 'Piesza trasa w Krakowie, która omija bariery z Twoich potrzeb.' },
        { head: 'Fakty', text: 'Każda bariera i udogodnienie ze źródłem, datą i statusem.' },
      ],
      footer: 'Aplikacja pokazuje fakty. Ocenę zostawia Tobie.',
      notes: `<p>EnableMe działa w trzech krokach.</p>
<p>[click] Najpierw potrzeby: zaznaczasz, czego unikasz i czego potrzebujesz, albo wybierasz gotowy zestaw. Nie pytamy o niepełnosprawność, bo do dopasowania trasy wystarczą preferencje.</p>
<p>[click] Potem trasa piesza w Krakowie, która omija bariery z Twoich potrzeb.</p>
<p>[click] I fakty: każda bariera i każde udogodnienie ma źródło, datę i status. Nie dajemy gwiazdek ani werdyktu. Ocenę zostawiamy Tobie.</p>`,
    },
    states: {
      summary: 'cztery stany odcinka trasy',
      heading: 'Każdy odcinek mówi, co o nim wiemy',
      legend: [
        { key: 'barrier', label: 'bariera z Twoich potrzeb' },
        { key: 'clear', label: 'bez barier, dane pełne' },
        { key: 'partial', label: 'dane niepełne' },
        { key: 'nodata', label: 'brak danych' },
      ],
      grayscale: 'ta sama trasa w skali szarości',
      rule: 'Brak informacji nigdy nie jest pokazywany jako dostępność.',
      channels: 'Stan niesie kolor, ikona i wzór linii. Pod mapą ta sama trasa jest listą tekstową.',
      notes: `<p>Trasa nie jest po prostu zielona albo czerwona. Każdy odcinek ma jeden z czterech stanów: bariera z Twoich potrzeb, brak barier przy pełnych danych, dane niepełne albo brak danych.</p>
<p>[click] Najważniejsza zasada: brak informacji nigdy nie udaje dostępności. Odcinek, o którym nic nie wiemy, jest szary i przerywany, a nie zielony.</p>
<p>[click] Stan niesie kolor, ikona i wzór linii, więc stany rozróżnisz nawet w skali szarości. Pod mapą ta sama trasa jest listą tekstową: to tekstowa alternatywa mapy dla czytnika ekranu.</p>`,
    },
    facts: {
      summary: 'fakty, głosy i sprzeczne dane',
      heading: 'Społeczność utrzymuje dane',
      card: {
        type: 'Wysoki krawężnik',
        sourceLabel: 'źródło',
        source: 'zgłoszenie użytkownika',
        dateLabel: 'data',
        date: '2026-10-04',
        statusLabel: 'status',
        status: 'niezweryfikowany',
        conflict: 'Dane mapy (OpenStreetMap): obniżony krawężnik',
        rule: 'Dopóki zgłoszenie nie ma 2 potwierdzeń, liczą się dane mapy.',
      },
      votes: ['Nadal jest', 'Już nie ma'],
      statuses: ['niezweryfikowany', 'potwierdzony', 'sporny', 'nieaktualny'],
      rules: ['jeden głos na fakt dziennie', 'liczy się 5 ostatnich osób', 'głos bez konta waży pół', 'flagi i moderacja'],
      notes: `<p>Dane żyją dzięki ludziom. Każdy może zgłosić barierę, udogodnienie albo niedostępny obszar, z kontem albo bez.</p>
<p>[click] Każdy fakt, także ten z OpenStreetMap, można potwierdzić: nadal jest, albo zgłosić: już nie ma. Z ostatnich głosów pięciu osób powstaje status: niezweryfikowany, potwierdzony, sporny albo nieaktualny.</p>
<p>[click] Tu przypadek sprzecznych danych: użytkownik zgłosił wysoki krawężnik, a OpenStreetMap mówi o obniżonym. Pokazujemy obie informacje i ich status, zamiast wybierać za użytkownika. Dopóki zgłoszenie nie zbierze dwóch potwierdzeń, liczą się dane mapy. Przed nadużyciami chronią limity głosów, flagi i moderator.</p>`,
    },
    demo: {
      summary: 'pokaz na żywo',
      heading: 'Na żywo',
      steps: [
        { head: 'Potrzeby', text: 'Poruszam się na wózku' },
        { head: 'Trasa', text: 'Tauron Arena - Ogród Doświadczeń' },
        { head: 'Brak trasy bez barier', text: 'Park Lotników Polskich' },
        { head: 'Sprzeczne dane', text: 'zgłoszenie kontra dane mapy' },
      ],
      footnote: 'Aplikacja HarmonyOS na emulatorze. Zgłoszenia w pokazie to dane przykładowe z okolic Tauron Areny, oznaczone w aplikacji.',
      notes: `<p>Teraz na żywo, na emulatorze HarmonyOS.</p>
<p>Ustawiamy potrzeby: poruszam się na wózku. Wyznaczamy trasę spod Tauron Areny do Ogrodu Doświadczeń: krawężnik potwierdzony, schody niezweryfikowane z trasą alternatywną, odcinki bez danych w części Czego nie wiemy.</p>
<p>Do Parku Lotników Polskich nie ma trasy bez barier: aplikacja mówi to wprost i pokazuje trasę z najmniejszą liczbą barier.</p>
<p>Na koniec wysoki krawężnik zgłoszony przez użytkownika, sprzeczny z OpenStreetMap: źródło, data, status i głos.</p>
<p>Gdy emulator zawiedzie: nagranie wideo od tej samej sceny.</p>`,
    },
    data: {
      summary: 'źródła danych, świeżość i niedostępność',
      heading: 'Skąd są dane i co, gdy ich brak',
      head: ['źródło', 'co daje', 'świeżość', 'gdy niedostępne'],
      rows: [
        ['OpenStreetMap (ODbL)', 'bariery, udogodnienia, sieć piesza, mapa', 'kopia z datą stanu OSM', 'ostatnia pełna kopia z jej datą'],
        ['Zgłoszenia ludzi', 'punkty i obszary', 'data ostatniego potwierdzenia', '-'],
        ['Wyszukiwarka adresów (Nominatim)', 'adres na punkt', 'na żądanie, z naszego serwera', 'jasny komunikat, bez zgadywania'],
        ['Dane miejskie (otwarte dane, MSIP)', 'następny krok', 'po sprawdzeniu warunków', 'jeszcze nieużywane'],
      ],
      footer: 'Każdy fakt ma status z głosów, także fakt z OpenStreetMap.',
      notes: `<p>Nie potrzebujemy bazy prowadzonej ręcznie przez miasto ani dostępu do systemów urzędu. Podstawą jest OpenStreetMap: wycinek Krakowa, pobierany w całości albo wcale. Aplikacja zawsze pokazuje datę kopii, a gdy źródła nie ma, pracuje na ostatniej pełnej kopii.</p>
<p>Na to nakładamy zgłoszenia ludzi, z datą ostatniego potwierdzenia. Adres wyszukujemy z naszego serwera, bez danych osoby. Otwarte dane miasta i MSIP dołączymy po sprawdzeniu warunków każdego zbioru.</p>`,
    },
    architecture: {
      summary: 'architektura: dane osobno, prezentacja osobno',
      heading: 'Dane osobno, prezentacja osobno',
      ingest: { head: 'Pozyskanie danych', items: ['wycinek OpenStreetMap', 'importer tagów', 'PostGIS: fakty i głosy', 'Valhalla: graf tras'] },
      api: { head: 'API', items: ['Python, FastAPI', '16 operacji', 'jeden kontrakt'] },
      clients: { head: 'Klienci', items: ['web: React, MapLibre', 'HarmonyOS: ArkTS'] },
      extendHead: 'Jak rozszerzyć',
      extend: ['nowe źródło: importer do modelu faktu', 'nowa kategoria: reguła tagu', 'nowe miasto: wycinek i graf'],
      privacyHead: 'Prywatność',
      privacy: ['potrzeby tylko na urządzeniu', 'zapytanie o trasę nie opuszcza projektu', 'konto bez e-maila'],
      notes: `<p>Architektura oddziela pozyskanie danych od prezentacji. Importer czyta wycinek OpenStreetMap, zamienia tagi na bariery i udogodnienia i zapisuje je w PostGIS, a silnik Valhalla liczy trasy na naszym grafie.</p>
<p>[click] Wszystko wystawia jedno API z szesnastoma operacjami. Korzystają z niego dwa niezależne klienty: aplikacja webowa i aplikacja HarmonyOS.</p>
<p>[click] Nowe źródło to nowy importer do tego samego modelu faktu, nowa kategoria to reguła tagu, nowe miasto to nowy wycinek i graf. Prywatność jest wbudowana: potrzeby zostają na urządzeniu, zapytanie o trasę nie wychodzi poza projekt, konto nie wymaga e-maila.</p>`,
    },
    business: {
      summary: 'model biznesowy i utrzymanie',
      heading: 'Model biznesowy i utrzymanie',
      free: { head: 'Bezpłatnie', items: ['mieszkańcy i turyści', 'bez reklam', 'bez sprzedaży danych o ludziach'] },
      paid: {
        head: 'Płacą',
        items: [
          'miasto i zarządcy dróg: wdrożenie i zgłoszenia barier w jednym miejscu',
          'obiekty i organizatorzy wydarzeń: trasa bez barier do wejścia',
          'partnerzy programu nagród za potwierdzenia',
        ],
      },
      run: { head: 'Utrzymanie poza infrastrukturą miasta', items: ['operator hostuje jeden serwer z kontenerami', 'odświeżanie danych i aktualizacje', 'moderacja zgłoszeń'] },
      footer: 'Sprzedajemy usługę, nie dane: dane z OpenStreetMap zostają otwarte.',
      notes: `<p>Dla mieszkańców i turystów aplikacja jest bezpłatna.</p>
<p>[click] Płacą ci, którzy zyskują na dostępności. Miasto i zarządcy dróg dostają wdrożenie i potwierdzone przez mieszkańców zgłoszenia barier w jednym miejscu. Hotele, muzea i organizatorzy wydarzeń kupują trasę bez barier do swojego wejścia. Partnerzy mogą finansować nagrody za potwierdzenia, na przykład bilet komunikacji miejskiej.</p>
<p>[click] Usługę prowadzi operator poza infrastrukturą miasta: jeden serwer z kontenerami, odświeżanie danych, aktualizacje i moderacja. Sprzedajemy usługę, nie dane: to, co pochodzi z OpenStreetMap, zostaje otwarte.</p>`,
    },
    status: {
      summary: 'co działa i co dalej',
      heading: 'Co działa i co dalej',
      works: {
        head: 'Działa dziś',
        items: [
          'potrzeby i gotowe zestawy',
          'trasa z czterema stanami odcinków i listą',
          'trasa alternatywna i brak trasy bez barier',
          'fakty ze źródłem, datą, statusem i głosami',
          'zgłoszenia, konta, moderacja, PL i EN',
        ],
      },
      next: { head: 'Dalej', items: ['serwer z danymi całego Krakowa', 'zdjęcia w zgłoszeniach', 'otwarte dane miasta', 'zgłoszenia z powrotem do OpenStreetMap', 'kolejne miasta'] },
      limits: 'Znane ograniczenia prototypu: dane przykładowe z okolic Tauron Areny, hostowane demo po HTTP.',
      closing: 'EnableMe - fakty zamiast etykiet.',
      notes: `<p>Dziś na HarmonyOS działa cały główny scenariusz, na oznaczonych danych przykładowych.</p>
<p>[click] Dalej: serwer z danymi całego Krakowa, zdjęcia w zgłoszeniach, otwarte dane miasta, odsyłanie zgłoszeń do OpenStreetMap i kolejne miasta.</p>
<p>[click] EnableMe: fakty zamiast etykiet i uczciwie pokazana niepewność. Dziękujemy.</p>`,
    },
  },
};
