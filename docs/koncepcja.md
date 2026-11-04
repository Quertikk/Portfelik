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

AI wykonuje w aplikacji realną pracę, której użytkownik inaczej musiałby dokonać ręcznie:

1. **Rozpoznawanie paragonu:** zdjęcie paragonu jest wysyłane do modelu AI, który zwraca kwotę, datę, nazwę sklepu i proponowaną kategorię. Użytkownik tylko sprawdza i zatwierdza.
2. **Podsumowanie miesiąca (opcjonalnie):** krótki opis słowny, gdzie wydano więcej niż zwykle i co można ograniczyć.

## 6. Ograniczenia

- **Brak integracji z bankami.** Pobieranie transakcji z banku wymaga licencji i umów z bankami (dyrektywa PSD2), co wykracza poza projekt. Wydatki są dodawane ręcznie albo ze zdjęcia paragonu.
- **Pieniądze są wirtualne.** Skarbonka i „kary” są zapisami w aplikacji, nie przelewami.
- **Uproszczone logowanie w pierwszej wersji.** W sprincie 0 użytkownika wybiera się z listy; pełne logowanie z hasłem jest zaplanowane w sprincie 1.

## 7. Technologie

- Python 3 + Flask: prosty serwer, łatwy do uruchomienia i opisania w dokumentacji.
- SQLite: baza w jednym pliku, nie wymaga instalacji serwera bazy danych.
- HTML + CSS: interfejs działający w przeglądarce na komputerze i telefonie.
- API modelu AI (Gemini lub Claude) do rozpoznawania paragonów.
