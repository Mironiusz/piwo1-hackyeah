---
name: implementation-dod-review
description: review zmian w implementacji względem Definition of Done repozytorium. użyj, gdy user prosi o sprawdzenie gotowości, review architektury, ocenę jakości jednostki kodu, weryfikację dokumentacji, audyt zmienionych plików albo przygotowanie zmiany do mergu.
---

# Proces review

Oceń implementację względem Definition of Done repozytorium.

Przed czytaniem kodu otwórz `docs/standards/README.md` - mapę wszystkich standardów, z osobną sekcją na każdy standard, mówiącą, za co odpowiada i jaki ma status (gotowy, częściowy, szkielet). Mapa zastępuje jakąkolwiek stałą listę standardów wypisaną tutaj, więc ten skill nie starzeje się w miarę dokładania kolejnych plików do katalogu.

Sprawdź też `docs/standards/decision_registry.md`. Brak reguły w danym obszarze może być zapisanym odroczeniem, nie luką - zgłaszanie jako braku czegoś, co jest świadomie odłożone wraz z powodem, jest szumem.

Potem obejrzyj zmienione pliki. Jeśli kontekst gita jest dostępny, zakresem review jest aktualny diff. Jeśli nie jest, zakresem są pliki albo kod wskazane przez użytkownika.

Sprawdź zmianę względem każdego standardu z mapy w `docs/standards/standard_review.md`, sekcja "Mapa standard - narzędzie weryfikujące" - nie tylko względem tych, które po przeczytaniu diffu wydają się właściwe. Dla standardu ze zmapowaną komendą odpal ją naprawdę, przez `Bash` albo `PowerShell`, zamiast oceniać zgodność na oko. Reguła odstępstwa jest zaostrzona, dopóki `docs/standards/README.md` nie zapisze jawnej decyzji o jej rozluźnieniu: projekt bez kodu zastanego nie ma czego chronić okresem przejściowym, więc niezgodność ze standardem blokuje review niezależnie od tego, kto pisał dany fragment i kiedy.

Przebieg waży więcej niż review. Znana porażka przebiegu w zakresie zmiany (testy, łańcuch na środowisku, testy e2e) trzyma werdykt na niegotowe, nawet gdy litera kryterium akceptacji jest spełniona. Przed werdyktem sprawdź, czy żaden przebieg późniejszy niż ocena kryterium nie przeczy zakresowi, który oceniasz, i oceniaj kod gałęzi docelowej, nie to, która inicjatywa miała daną rzecz domknąć.

Nie wymyślaj brakującego kontekstu. Jeśli brakuje wymaganego pliku, standardu, granicy odpowiedzialności, testu albo dokumentu - zgłoś to wprost.

Czego nie zgłaszać:

- spekulacyjnych przepisań, których zmiana nie potrzebuje,
- preferencji stylistycznych bez konkretnego ryzyka - z zastrzeżeniem, że reguła zapisana w standardzie nie jest preferencją stylistyczną: naruszenie `standard_formatting.md`, na przykład pogrubienie w prozie albo znak z listy zakazanych, zgłaszasz normalnie,
- problemów istniejących przed zmianą i leżących poza jej zakresem, chyba że blokują zrozumienie samej zmiany,
- braku reguły w obszarze objętym wpisem w rejestrze decyzji odroczonych.

Zgłoś ustalenia w tej kolejności:

1. Blokery - rzeczy, z powodu których zmiana nie jest skończona.
2. Ryzyka - rzeczy, które mogą być akceptowalne, ale wymagają świadomej decyzji.
3. Ulepszenia - opcjonalne porządki i sugestie jakościowe.
4. Weryfikacja - lista wszystkich standardów z mapy w `standard_review.md`, każdy z jednym z trzech stanów: nie dotyczy (z krótkim powodem), sprawdzono automatycznie (komenda z mapy odpalona, wynik albo jego streszczenie w raporcie), sprawdzono ręcznie (standard nie ma zmapowanej komendy). Pominięcie standardu bez jednego z tych trzech stanów jest niekompletną Weryfikacją.
5. Werdykt - jeden z trzech: gotowe, gotowe po drobnych poprawkach, niegotowe - wraz z zakresem, który obejmuje: cała inicjatywa, jedno zadanie z kilku, sam plan albo wskazane pliki.

Zakres werdyktu rozstrzyga o dalszym losie katalogu inicjatywy, więc nazwij go wprost: końcowe `ready` dla całej inicjatywy kwalifikuje ją do archiwum `plans_finished/`, `ready` dla jednego zadania, planu albo części kodu nie (`docs/standards/standard_agentic_workflow.md` rozdz. 4.6). Zgłoś tę kwalifikację w raporcie, ale niczego nie przenoś - review pozostaje w trybie odczytu, a przeniesienie należy do `plan-implement` albo do agenta, któremu user polecił porządki wprost. Review wywołane na inicjatywie już jawnie zakończonej mówi o tym w raporcie, zamiast oceniać ją od nowa.

Wybieraj konkretną informację zwrotną na poziomie pliku, nie ogólne porady.
