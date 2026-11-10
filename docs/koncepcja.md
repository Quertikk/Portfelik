# Koncepcja projektu Portfelik

## 1. Problem

Osoby, które mieszkają razem (pary, współlokatorzy, rodziny), mają jednocześnie wydatki osobiste i wspólne. Najczęściej wspólne wydatki są zapisywane „w głowie” albo w czacie, przez co trudno odpowiedzieć na pytania:

- ile w tym miesiącu wydaliśmy razem, a ile każdy osobno;
- kto ile zapłacił za wspólne rzeczy;
- czy duży zakup był wcześniej uzgodniony;
- na co uciekają pieniądze i czy mieścimy się w budżecie.

## 2. Cel

Prosta aplikacja webowa, w której każdy użytkownik prowadzi swój **portfel osobisty**, a grupa korzysta ze **wspólnego portfela**. Aplikacja pokazuje podsumowania, pilnuje limitów, wymaga zatwierdzania większych wspólnych wydatków i pomaga oszczędzać.

## 3. Użytkownicy

- Para, która prowadzi wspólny budżet.
- Współlokatorzy, którzy dzielą rachunki i zakupy.
- Pojedyncza osoba, która chce kontrolować własne wydatki.

## 4. Główne funkcje

| Obszar | Funkcja |
|---|---|
| Portfele | Portfel osobisty i wspólny, przełączanie jednym kliknięciem, analityka osobno dla każdego |
| Wydatki | Kwota, kategoria, data, opis, osoba płacąca; komentarz do wydatku |
| Zatwierdzanie | Próg kwoty (np. 200 zł) we wspólnym portfelu; wydatek powyżej progu ma status „oczekuje”, druga osoba zatwierdza lub odrzuca |
| Limity | Limit miesięczny na kategorię; ostrzeżenie i tryb „Oszczędny”, gdy wydano ponad 80% budżetu przed końcem miesiąca |
| AI | Dodanie wydatku na podstawie zdjęcia paragonu: model AI odczytuje kwotę, datę, sklep i proponuje kategorię |
| Analityka | Wydatki według kategorii, porównanie z poprzednim miesiącem i ze średnią z 3 miesięcy |
| Subskrypcje | Lista stałych opłat (Netflix, Spotify, siłownia) z przypomnieniem 2 dni przed płatnością |
| Oszczędzanie | Wirtualna skarbonka z zaokrąglaniem wydatków; propozycja przeniesienia niewydanych środków na koniec miesiąca |
| Grywalizacja | Osiągnięcia i humorystyczne „kary” za przekroczenie limitów |

Kolejność realizacji i szacunki znajdują się w [backlog.md](backlog.md).

## 5. Rola AI

AI przejmuje pracę, którą użytkownik inaczej musiałby wykonać ręcznie:

1. **Rozpoznawanie paragonu:** zdjęcie paragonu jest wysyłane do modelu AI, który zwraca kwotę, datę, nazwę sklepu i proponowaną kategorię. Użytkownik tylko sprawdza i zatwierdza.
2. **Podsumowanie miesiąca (opcjonalnie, nie zrealizowane, poza backlogiem):** krótki opis słowny, gdzie wydano więcej niż zwykle i co można ograniczyć.

## 6. Ograniczenia

- **Brak integracji z bankami.** Pobieranie transakcji z banku wymaga licencji i umów z bankami (dyrektywa PSD2), co wykracza poza projekt. Wydatki są dodawane ręcznie albo ze zdjęcia paragonu.
- **Pieniądze są wirtualne.** Skarbonka i „kary” są zapisami w aplikacji, nie przelewami.
- **Hasła bez odzyskiwania.** Logowanie działa na e-mailu i haśle (skrót w bazie), ale aplikacja nie wysyła wiadomości, więc nie ma resetu hasła.
- **Jeden plik bazy.** SQLite wystarcza dla małej grupy użytkowników; przy większym ruchu trzeba by przejść na PostgreSQL.

## 7. Technologie, narzędzia i biblioteki

Koncepcja tworzenia oprogramowania: małe przyrosty w dwutygodniowych sprintach (Scrum), każda zmiana w Pull Requeście z recenzją drugiej osoby i testem automatycznym, wdrożenie na serwer po zielonych testach.

| Obszar | Wybór | Uzasadnienie |
|---|---|---|
| Język i serwer | Python 3 + Flask | Prosty serwer, łatwy do uruchomienia i opisania |
| Szablony | Jinja2 (w Flasku), HTML + CSS bez frameworka | Interfejs na telefonie i komputerze bez kroku budowania |
| Baza danych | SQLite, migracje własne (lista `MIGRATIONS`, `PRAGMA user_version`) | Jeden plik, bez serwera bazy; kopia przez `sqlite3 .backup` |
| Bezpieczeństwo | Flask-WTF (CSRF), `werkzeug.security` (skróty haseł) | Gotowe, sprawdzone mechanizmy zamiast własnych |
| AI | Gemini (Google), wywołanie przez `urllib` z biblioteki standardowej | Odczyt paragonu ze zdjęcia; dostawca wymienny przez `receipts.PROVIDERS`; bez dodatkowej biblioteki |
| Testy | pytest; `coverage` do pomiaru pokrycia; GitHub Actions | Testy przy każdym Pull Requeście |
| Kontrola wersji i backlog | Git, GitHub (Issues, Projects, Pull Requesty) | Jedna Issue na pozycję F i NF |
| Hosting | PythonAnywhere (HTTPS, trwały dysk, zadanie okresowe kopii) | Darmowe konto wystarcza do oddania projektu |
| Diagramy | Mermaid w plikach Markdown | Diagramy w repozytorium, bez osobnego programu |
| Asystenci AI | Claude (kod i dokumentacja techniczna), Gemini (grafiki, prezentacje) | Za wynik odpowiadają osoby; kod przechodzi recenzję i testy |

## 8. Układy elektroniczne i mechaniczne

Projekt jest wyłącznie oprogramowaniem, więc nie zawiera układów elektronicznych ani mechanicznych. Wymaganie o schematach takich układów (wytyczna 7) nie dotyczy projektu. Zamiast nich dokumentujemy architekturę i procesy diagramami UML w [uml.md](uml.md) oraz diagramem architektury w [specyfikacji](specyfikacja.md#4-architektura).
