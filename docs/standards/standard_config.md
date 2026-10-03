# Standard konfiguracji i sekretów

Stan dokumentu: 2026-10-03

Status: gotowy - pełna treść.

## Po co ten dokument

Konfiguracja rozlana po repozytorium jest problemem, który ujawnia się dopiero przy rotacji sekretu albo audycie: na pytanie "skąd to jest czytane i kto tego jeszcze używa" trzeba wtedy odpowiedzieć przeszukaniem całego kodu, zamiast otwarciem jednego pliku. Drugi koszt jest cichszy: gdy każde miejsce czyta zmienną środowiskową po swojemu, część z nich robi to z wartością domyślną, część bez, a błąd konfiguracji zamiast wywalić się przy starcie, ujawnia się losowo, w produkcji, daleko od przyczyny.

Ten standard ustala, gdzie wartość konfiguracyjna ma mieszkać i kto ma prawo ją przeczytać.

## Zakres i granice

Ten standard odpowiada za: podział konfiguracji na warstwy, regułę przypisania wartości do warstwy, walidację wartości pochodzących ze środowiska, miejsce przechowywania sekretów i zawartość pliku konfiguracyjnego.

Czego tu nie ma:

- wykrywanie sekretów zaszytych w kodzie i skan podatności zależności - to `standard_security.md`;
- format, poziomy i treść wpisu logu, mimo że poziom logowania jest wartością konfiguracyjną - to `standard_logging.md`;
- jedno miejsce prawdy dla mechanizmów współdzielonych jako reguła architektoniczna - to `standard_architecture.md`;
- co konkretnie serwis potrzebuje mieć skonfigurowane w warstwach drugiej i trzeciej - to specyfikacja produktu wskazana w `CLAUDE.md`. Nazwy i znaczenie pozycji warstwy pierwszej są natomiast tutaj, w sekcji o pozycjach środowiska, bo żaden z trzech szablonów nie zawiera komentarzy i nie może ich nieść.

## Reguła odstępstwa

Standard opisuje stan docelowy i obowiązuje w pełni od pierwszego commita. Projekt założony z szablonu nie ma kodu zastanego, więc nie ma czego chronić okresem przejściowym - kod niezgodny ze standardem blokuje review niezależnie od tego, kto go pisał i kiedy.

Gdy repozytorium będzie mieć kod zastany, rozluźnienie tej reguły do wersji miękkiej ma być jawną decyzją zapisaną w `docs/standards/README.md` wraz z datą i powodem. Nie jest stanem, który wchodzi w życie sam.

## Trzy warstwy konfiguracji i cztery miejsca przechowywania

Warstwa pierwsza: zmienne środowiskowe. Wszystko, co jest sekretem, oraz każdy nie-sekret zależny od maszyny albo od środowiska. Nazwy i wartości mieszkają w trzech wersjonowanych szablonach, `.env.example`, `.env.local.example` i `.env.priv.example`, a znaczenie każdej pozycji jest opisane niżej w tym dokumencie - plik szablonu nie może go nieść, bo nie zawiera komentarzy.

Kontrakt środowiska wymaga, żeby każdy klucz szablonu stał także w odpowiadającym mu pliku lokalnym. Projekt pilnuje tej reguły testem architektury, który zakłada razem z pierwszym kodem tej warstwy; szablon go nie zawiera. Dalej w tym dokumencie ten test nazywa się testem kontraktu środowiska.

Podział na trzy szablony idzie po dwóch pytaniach zadawanych po kolei. Pierwsze: czy wartość jest sekretem. Sekret idzie do `.env.example`, chyba że jest poświadczeniem, pod którym każdy w zespole występuje we własnym imieniu w cudzym systemie - wtedy do `.env.priv.example`. Drugie pytanie dotyczy wyłącznie nie-sekretów: czy wartość różni się między maszynami albo środowiskami. Jeśli tak, idzie do `.env.local.example`; jeśli nie, nie jest pozycją środowiska wcale i stoi wpisana wprost w warstwie drugiej.

Rozdzielenie sekretów od reszty ma jeden konkretny zysk: na pytanie, co w tym repozytorium jest sekretem, odpowiada się otwarciem jednego pliku, w którym każda pozycja nim jest, zamiast rozstrzygania tego pozycja po pozycji. Wydzielenie poświadczeń osobistych ma dwa: wspólny szablon przestaje wymuszać wypełnienie wartości, której nikt nie może podać za kogoś innego, a poświadczenie osobiste stoi w pliku, którego nie otwiera się przy stawianiu środowiska.

Podział na trzy pliki jest faktem wyłącznie lokalnym. Środowisko docelowe dostaje jeden zestaw zmiennych i podziału na pliki nie zna, więc każda reguła oparta na tym, w którym pliku wartość stoi, opisuje maszynę developera, nie środowisko docelowe.

Warstwa druga: konfiguracja globalna, czyli `config/config.py`. Jedyne miejsce w repozytorium, które czyta zmienne środowiskowe i pliki środowiska, i zarazem jedyne, z którego reszta repozytorium bierze konfigurację. Wystawia gotowe, otypowane wartości jako stałe modułu, więc moduł wołający nie wie i nie ma wiedzieć, czy dana wartość przyszła ze środowiska, czy stoi wpisana wprost. Walidację kontraktu wykonuje `config/settings.py`. Ani on, ani pozostałe moduły warstwy drugiej, na przykład odczyt formatu pliku środowiska, nie sięgają po środowisko same - wszystkie dostają wartości podane z fasady.

Kolejność źródeł w fasadzie jest jedna i pierwszeństwo ma to, co trafi wcześniej: zmienne procesu, potem plik wartości lokalnych, potem plik sekretów. Uruchamiacz narzędzi działających poza pełnym środowiskiem aplikacji stosuje tę samą kolejność, więc wartość podana przed poleceniem wygrywa z plikiem w obu drogach. Pliku poświadczeń osobistych fasada nie czyta wcale.

Warstwa trzecia: konfiguracja lokalna. Stałe należące do jednego fragmentu kodu i nieróżniące się między środowiskami: limity, progi, nazwy, wartości domyślne reguł domenowych. Mieszkają przy tym kodzie, którego dotyczą, nie w warstwie drugiej.

## Pozycje środowiska

Każda pozycja trzech szablonów ma w tej sekcji wpis dopisywany razem z pozycją w szablonie. Wpis podaje nazwę pozycji, jej znaczenie, to, czy pozycja jest wymagana albo ma wartość domyślną, oraz zachowanie procesu przy jej braku. Szablon nie zawiera jeszcze żadnej pozycji.

Wartość podawana doraźnie przy wywołaniu, taka jak zgoda na nałożenie rewizji na bazę środowiska docelowego, nie ma pozycji w żadnym szablonie i mieć nie może. Nieobecność w szablonie jest tu regułą, nie przeoczeniem, i wynika wprost z kontraktu środowiska: każdy klucz szablonu ma stać także w pliku lokalnym, więc pozycja w szablonie kazałaby wpisać zgodę raz na zawsze - a zgoda wpisana do pliku przestaje być zgodą i bramka staje się fikcją. Z tego samego powodu dopisanie takiego klucza do własnego pliku środowiska jest obejściem reguły, nie wygodą: test kontraktu środowiska tego nie złapie, bo pilnuje kluczy szablonu, nie kluczy nadmiarowych.

## Reguła przypisania wartości do warstwy

O miejscu wartości rozstrzyga kolejno sekretność, a potem przewidywana zmienność:

- wartość jest sekretem - warstwa pierwsza, plik sekretów, a przy poświadczeniu osobistym plik prywatny;
- wartość nie jest sekretem, ale zależy od maszyny albo od środowiska - warstwa pierwsza, plik wartości lokalnych;
- wartość nie jest sekretem i zakładamy, że się nie zmieni, a używa jej więcej niż jedno miejsce - warstwa druga, wpisana wprost;
- wartość jest stała dla wszystkich środowisk i używana w jednym miejscu - warstwa trzecia.

Kryterium przewidywanej zmienności jest oceną, nie faktem, i pomyłka w jedną stronę oznacza, że zmiana wartości wymaga wdrożenia zamiast edycji pozycji. Dlatego wartość, którą ktoś kiedyś będzie chciał zmienić bez wdrożenia, zostaje pozycją środowiska nawet wtedy, gdy dziś jest jednakowa wszędzie.

Pozycją środowiska zostaje też wartość jednakowa wszędzie, którą czyta konsument spoza Pythona, na przykład interpolacja pliku compose albo skrypt powłoki: tylko kod w Pythonie umie zaimportować stałą z warstwy drugiej. Pozycja, której nie czyta żaden proces serwisu, nie ma odpowiednika ani w modelu ustawień, ani w fasadzie.

Nie każdy nie-sekret wolno wnieść do repozytorium i to jest reguła niezależna od powyższych. Żaden adres, host, login ani sekret środowiska docelowego nie wchodzi do repozytorium w jakiejkolwiek formie - ani do kodu, ani do dokumentacji, ani do szablonu środowiska. Ten sam zakaz obejmuje identyfikatory użytkowników obcego systemu. Nie-sekret objęty zakazem trafia do pliku wartości lokalnych niezależnie od tego, że się nie zmienia, a w warstwie drugiej stoi wyłącznie nazwa pozycji, nigdy jej treść. W szablonie na miejscu wartości stoi znacznik do uzupełnienia, a na środowisku docelowym wartość wpisuje człowiek w konfiguracji tego środowiska.

Konsekwencja tych reguł jest jednoznaczna i zamierzona: odczyt zmiennej środowiskowej poza warstwą drugą jest naruszeniem standardu, niezależnie od tego, jak lokalna jest ta wartość i jak wygodnie było ją przeczytać na miejscu. Rozproszony odczyt środowiska to dokładnie ten stan, w którym nie da się odpowiedzieć na pytanie, co serwis potrzebuje mieć ustawione, bez przeszukania całego kodu.

Jedyny dopuszczalny wyjątek: kod uruchamiany poza pełnym środowiskiem aplikacji. Należą do niego jednorazowe narzędzia uruchamiane z linii poleceń, `alembic/env.py` oraz te konftesty i testy, które czytają pozycje nieznane fasadzie, na przykład adres konta migracyjnego. Taki wyjątek jest opisany w docstringu w miejscu odczytu, wraz z powodem - nie jest cichy.

Adres połączenia kontem właściciela schematu, używany wyłącznie przy nakładaniu rewizji, czyta `alembic/env.py` wprost ze środowiska, a warstwa druga go nie zna i znać nie ma: konto zmieniające schemat nie ma prawa stać w warstwie, którą importuje każdy proces serwisu. Brak tego adresu zatrzymuje Alembika z nazwą właściwego klucza, bez fallbacku.

## Walidacja wartości ze środowiska

Wartość pochodząca ze środowiska jest walidowana przy starcie procesu, nie przy pierwszym użyciu. Brak wymaganej zmiennej albo wartość niepoprawnego typu zatrzymuje start z komunikatem mówiącym, której zmiennej brakuje i w którym pliku ta zmienna ma stać - nie przechodzi dalej z wartością domyślną i nie wywala się później, w losowym miejscu. Przypisanie pozycji do pliku stoi w `config/settings.py` jako jawna mapa i jest utrzymywane razem z szablonami: dopisanie pozycji do szablonu bez wpisu w tej mapie daje komunikat nazywający zmienną, ale milczący o pliku.

Komunikat naruszenia podaje nazwę zmiennej i nazwę złamanej reguły, nigdy wartość ani jej fragment.

Walidacja sprawdza kształt wartości, nie stan zasobu, na który wartość wskazuje. Istnienia katalogu albo pliku pod ścieżką z konfiguracji nie sprawdza - brak takiego zasobu ujawnia się na sondzie gotowości albo przy pierwszym użyciu.

Adres, pod który proces wysyła sekret albo token, oraz adres, z którego pobiera klucze publiczne do sprawdzania podpisu tokenów, musi używać HTTPS, bez wyjątku dla adresów lokalnych, bo pierwszym idzie poświadczenie, a podmieniony zbiór kluczy podpisałby dowolny token. Naruszenie zatrzymuje start.

Wartość domyślna jest dopuszczalna wyłącznie tam, gdzie istnieje sensowna wartość bezpieczna, a jej użycie nie ukrywa błędu konfiguracji. Connection string nie ma wartości domyślnej. Poziom logowania ma - i jest nią `INFO`, nigdy `DEBUG`: domyślny poziom `DEBUG` w połączeniu z regułą o danych osobowych ze `standard_logging.md` zamienia każde niedopatrzenie w kodzie w ekspozycję danych.

Strefa biznesowa (`standard_time.md`) nie ma wartości domyślnej i mieć jej nie może: strefa maszyny wygląda na sensowny domyślnik, a jest wartością, która na innym serwerze cicho zmienia zapisane przesunięcie. Przełącznik wystawiający cokolwiek ponad kontrakt produktu, na przykład interaktywną przeglądarkę dokumentu interfejsu, ma wartość domyślną wyłączoną: wdrożenie, które o przełączniku nie wie, nie wystawia niczego ponad specyfikację.

Przy pozycji wymaganej wartość pusta bywa legalną decyzją, na przykład pusta lista źródeł, z których przeglądarka może wołać serwis, znaczy, że żadna przeglądarka nie ma dostępu. Brak klucza i wartość pusta są wtedy dwiema różnymi rzeczami: pierwsze jest niewypełnioną konfiguracją i zatrzymuje start, drugie świadomą decyzją.

Wyjątkiem od walidacji przy starcie jest pozycja, której nie czyta proces obsługujący żądania, tylko wyłącznie proces roboczy albo jedno zadanie okresowe. Taka pozycja może być opcjonalna i bez wartości domyślnej: jej brak nie zatrzymuje startu interfejsu programistycznego, a ujawnia się przy pierwszej próbie użycia jako nazwany wyjątek i kończy przebieg jako nieudany. Brak nie jest przy tym cichy: przebieg zapisuje w swoich szczegółach, że konfiguracji brakuje, zamiast udawać wykonanie. Wartość pusta znaczy przy takiej pozycji brak konfiguracji, jawnie i celowo, bo kontrakt środowiska wymaga obecności każdego klucza szablonu w pliku lokalnym, a maszyna, na której nikt tej funkcji nie konfiguruje, zostawia pozycję pustą.

Serwis stoi na Pydantiku, więc kontrakt środowiska jest walidowanym modelem, nie zestawem luźnych sprawdzeń rozsypanych po kodzie. Model daje walidację typów, jawny komunikat o brakującej wartości i jedno miejsce, w którym widać cały kontrakt. Wartości wstrzykuje mu fasada jedną mapą - model nie czyta środowiska sam, więc test podaje mu własną mapę zamiast podmieniać zmienne procesu.

## Sekrety

Sekret nie trafia do repozytorium w żadnej formie - ani jako wartość domyślna w kodzie, ani jako przykład w dokumentacji, ani w pliku szablonu. `.env.example` zawiera wyłącznie jawne miejsca do wypełnienia, także dla wartości, które sekretem nie są: adresu serwera, nazwy bazy i nazwy konta. Powód dla tych trzech: razem z hasłem tworzą kompletny zestaw dostępu, a osobno są mapą infrastruktury, która nie ma powodu leżeć w publicznym repozytorium.

Sekret wydany przez system zewnętrzny przychodzi kanałem wskazanym przez jego wystawcę, nigdy przez repozytorium, zgłoszenie ani czat.

Poświadczenie osobiste, które otwiera zapis do systemu poza tym repozytorium, ma granicę użycia ostrzejszą niż pozostałe pozycje. Nie wolno go czytać ani warstwie drugiej, ani żadnej z trzech warstw serwisu, nie wolno podawać go argumentem wiersza poleceń i nie wolno wypisywać jego wartości w żadnej postaci - ani w raporcie narzędzia, ani w treści wyjątku, ani w logu. Czyta go wyłącznie narzędzie, które go potrzebuje, i redaguje w jednym miejscu, zanim cokolwiek trafi na wyjście. Nazwa takiej pozycji stoi w szablonie prywatnym po to, żeby była jedna dla całego zespołu.

Wszystkie trzy pliki lokalne są w `.gitignore`, a dostęp do plików sekretów, czyli do `.env` i `.env.priv`, jest zablokowany po stronie narzędzi agentowych dwiema barierami, z których żadna nie zastępuje drugiej.

Pierwsza to lista blokad w `.claude/settings.json`. Obejmuje odczyt oraz zapis narzędziami operującymi na plikach - zapis dlatego, że plik z sekretami należy do człowieka, a jego nadpisanie jest nieodwracalne inaczej niż wygenerowaniem wszystkiego od nowa po drugiej stronie. Lista wymienia każdy plik po nazwie i nie jest wzorcem, więc nowy plik sekretów trzeba do niej dopisać - inaczej powstaje przez samo swoje istnienie, poza zasięgiem reguły.

Druga to hook `block_dangerous_commands.py`, który zatrzymuje polecenia powłoki wypisujące zawartość takiego pliku oraz rekursywne przeszukiwanie korzenia drzewa bez jawnego wykluczenia plików sekretów, bo wzorzec przepuszczony przez całe drzewo trafia w plik sekretów tak samo jak w kod. Hook rozpoznaje polecenie po jego pierwszym słowie, więc nie widzi odczytu wewnątrz interpretera - i jest to świadome ustępstwo, bo program czytający sekret z pliku i podający go dalej jest sposobem zalecanym. Hook działa ponadto wyłącznie po stronie Claude Code, bez odpowiednika po stronie Codeksa.

Żadna z tych dwóch barier nie obejmuje `.env.local` i jest to decyzja, nie przeoczenie. W większości ekosystemów ta nazwa oznacza plik lokalnych sekretów; w tym repozytorium niesie wyłącznie nie-sekrety, więc jej zawartość wolno cytować w rozmowie i w raporcie. Cena jest realna i przyjęta świadomie: sekret wpisany tam z przyzwyczajenia nie zostanie złapany ani przez blokadę odczytu, ani przez kontrolę poleceń powłoki.

Obie bariery chronią przed pomyłką, żadna przed intencją. Token albo hasło ujawnione gdziekolwiek, także w wyjściu polecenia, uznaje się za spalone i unieważnia po stronie systemu, który je wydał.

Reguła ignorowania plików lokalnych stoi na wzorcu `.env.*`, spod którego wersjonowane szablony są wyjęte negacjami `!.env.example` i `!.env.*.example`. Kolejność w `.gitignore` jest tu częścią reguły, bo negacja działa wyłącznie po wzorcu, który dany plik łapie. Jedna litera różnicy między nazwą szablonu a nazwą pliku lokalnego decyduje o tym, czy sekret zostaje na maszynie, więc oba warunki - obecność wzorca i brak negacji dla pliku lokalnego - są pilnowane testem kontraktu środowiska.

Sekret nie trafia też do logu, do treści błędu zwracanej przez interfejs programistyczny ani do komunikatu wyjątku. W modelu ustawień sekret ma typ `SecretStr`, więc nie trafia do repr. Connection string w treści wyjątku jest najczęstszym sposobem, w jaki hasło ląduje w logu.

## Zawartość plików środowiska

Pliki środowiska nie zawierają komentarzy. Zakaz obejmuje wszystkie sześć: wersjonowane szablony `.env.example`, `.env.local.example` i `.env.priv.example` oraz lokalne pliki `.env`, `.env.local` i `.env.priv`, i nie ma od niego wyjątku dla komentarza wyjaśniającego, nagłówka grupującego ani znacznika sekcji.

Powód jest dwuczęściowy. Szablon jest kopiowany i wypełniany, więc komentarz w nim rozjeżdża się z kontraktem przy pierwszej zmianie i od tego momentu opisuje stan, którego już nie ma - a czyta go wtedy ktoś, kto nie ma jak zauważyć, że opis jest nieaktualny. Druga część jest ważniejsza: opis znaczenia zmiennej ma jedno miejsce i jest nim ten standard, sekcja o pozycjach środowiska. Dwa miejsca opisujące to samo to dwa miejsca do zaktualizowania i jedno, o którym ktoś zapomni.

Konsekwencja jest zamierzona: dopisanie zmiennej do szablonu bez opisania jej w tym dokumencie jest niepełną zmianą, tak samo jak dopisanie jej wyłącznie tutaj.

Reguła nie jest pilnowana testem. Test kontraktu środowiska czyta pliki środowiska z pominięciem komentarzy, bo jego zadaniem jest porównywanie kluczy, a nie kontrola formy - rozszerzenie go zmieniłoby jego zamiar. Egzekwowanie zostaje po stronie człowieka i przeglądu.

Znacznik do uzupełnienia w szablonie jest wartością, która nie przechodzi walidacji. Skopiowany i niewypełniony szablon ma zatrzymać start z nazwą zmiennej, a nie ustawić działającą konfigurację wskazującą nieistniejący zasób.

## Zawartość pliku konfiguracyjnego

Plik konfiguracyjny zawiera wartości i ich walidację. Nie zawiera logiki domenowej, nie wykonuje zapytań, nie otwiera połączeń i nie ma efektów ubocznych poza odczytem środowiska.

Import fasady konfiguracji jest kosztowny i wymaga kompletnego środowiska, bo wartości powstają w momencie importu. Koszt płaci każdy, kto zaimportuje cokolwiek z `api/`, `service/` albo `data/`, w tym test, który sam żadnej wartości nie zamawia. Jest to cena za to, że reszta repozytorium ma jeden adres konfiguracji zamiast funkcji, którą trzeba zawołać i której wynik trzeba czyścić między testami. Objaw braku wartości jest przy tym natychmiastowy i nazwany, nie cichy.

Moduły warstwy drugiej stojące pod fasadą - walidacja kontraktu, odczyt formatu pliku środowiska i konfiguracja logowania - mają import tani i bezpieczny i taki ma zostać. To one są importowane przez narzędzia działające poza pełnym środowiskiem aplikacji.

Konfiguracja nie jest miejscem na obejście braku wartości. Jeśli wartość jest wymagana, a nie ma jej w środowisku, poprawną reakcją jest zatrzymanie startu, nie podstawienie czegokolwiek.

## Checklista

- Czy jakikolwiek nowy odczyt zmiennej środowiskowej pojawia się poza fasadą konfiguracji - a jeśli tak, czy jest to opisany w docstringu wyjątek dla kodu spoza pełnego środowiska aplikacji?
- Czy nowa pozycja środowiska trafiła do właściwego z trzech plików: sekret do `.env`, poświadczenie osobiste do `.env.priv`, nie-sekret zależny od maszyny albo środowiska do `.env.local` - a nie-sekret niezmienny nie została pozycją środowiska wcale?
- Czy nowa pozycja środowiska ma wpis w mapie przypisania pozycji do pliku w `config/settings.py`, żeby komunikat o jej braku nazywał także plik?
- Czy każda nowa wymagana wartość ze środowiska zatrzymuje start procesu, gdy jej brakuje, zamiast przechodzić z wartością domyślną?
- Czy nowa pozycja opcjonalna jest czytana wyłącznie przez proces roboczy albo zadanie okresowe, a jej brak kończy przebieg nazwanym wyjątkiem zamiast cichego pominięcia?
- Czy komunikat naruszenia walidacji nazywa zmienną i regułę, bez wartości i jej fragmentu?
- Czy nowa wartość domyślna jest bezpieczna i nie ukrywa błędu konfiguracji?
- Czy nowa wartość konfiguracyjna trafiła do warstwy wynikającej z jej pochodzenia, a nie z zasięgu użycia?
- Czy nowa zmienna środowiskowa została dopisana do właściwego szablonu jako znacznik do uzupełnienia, który nie przechodzi walidacji, bez rzeczywistej wartości, i czy jej znaczenie zostało opisane w sekcji o pozycjach środowiska?
- Czy wybór szablonu wynika z jednego kryterium, czyli z tego, czy wartość jest u całego zespołu ta sama - a nie z tego, że pozycja jest sekretem? Szablon prywatny nie jest miejscem na każdy sekret, tylko na ten, w którym każdy występuje pod własnym kontem.
- Czy żaden adres, host, login ani sekret środowiska docelowego nie trafił do kodu, dokumentacji ani szablonu?
- Czy nowy plik sekretów, jeśli powstał, został objęty regułą w `.gitignore` i dopisany do blokady odczytu w `.claude/settings.json`?
- Czy pliki środowiska pozostają wolne od komentarzy?
- Czy sekret nie trafia do logu, treści błędu ani komunikatu wyjątku?
- Czy plik konfiguracyjny pozostaje wolny od logiki i efektów ubocznych poza odczytem środowiska?
