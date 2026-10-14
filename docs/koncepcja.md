# Koncepcja projektu BoxForFriend

## 1. Problem

Bliskie osoby często mieszkają daleko od siebie: para na studiach w różnych miastach, rodzice i dzieci, przyjaciele za granicą. Komunikatory rozwiązują problem przesyłania informacji, ale wiadomość w telefonie szybko ginie wśród dziesiątek powiadomień. Brakuje czegoś, co daje poczucie **obecności drugiej osoby** w codziennym otoczeniu.

## 2. Pomysł

Para identycznych urządzeń z kolorowym ekranem. Każde stoi na biurku lub półce u innej osoby.

1. Osoba A wysyła z telefonu zdjęcie lub krótki tekst.
2. Po kilku sekundach wiadomość pojawia się na ekranie urządzenia osoby B.
3. Urządzenie sygnalizuje nową wiadomość diodą.
4. Osoba B naciska przycisk, a osoba A dostaje potwierdzenie, że wiadomość została zobaczona.

Wiadomość zostaje na ekranie, dopóki nie przyjdzie następna, więc jest widoczna przez cały dzień.

## 3. Podobne rozwiązania na rynku

| Produkt | Co robi | Ograniczenia |
|---|---|---|
| LoveBox | Drewniane pudełko z ekranem, pokazuje tekst i proste rysunki | Brak prawdziwych zdjęć, wysoka cena (ok. 120–170 USD za sztukę) |
| Friendship Lamps | Para lamp: dotknięcie jednej zapala drugą | Przekazuje tylko sygnał, bez treści |

**Nasz wyróżnik:** kolorowy ekran i prawdziwe zdjęcia przy niższym koszcie urządzenia.

## 4. Cele projektu

1. Zbudować dwa działające urządzenia, które wymieniają między sobą zdjęcia i wiadomości tekstowe.
2. Zapewnić prosty sposób wysyłania wiadomości z telefonu, bez instalowania dodatkowej aplikacji.
3. Zapewnić potwierdzenie odczytu wiadomości (przycisk na urządzeniu).
4. Zaprojektować i wydrukować obudowę 3D.
5. Przygotować pełną dokumentację: specyfikację, schematy, diagramy, testy, instrukcje użytkownika i administratora.

## 5. Dostępne zasoby

- 2 × mikrokontroler ESP32-C3 Super Mini (Wi-Fi, USB-C),
- 2 × kolorowy wyświetlacz TFT,
- doświadczenie zespołu z wcześniejszego projektu na tym samym sprzęcie (wyświetlanie danych pobieranych z internetu),
- podwykonawca druku 3D.

## 6. Otwarte problemy (do rozwiązania w sprincie 1–2)

### 6.1 Zasilanie

Zasilanie przewodem USB jest najprostsze, ale niewygodne: urządzenia nie da się swobodnie przestawić. Rozważamy akumulator.

- **Problem:** ekran i Wi-Fi zużywają dużo energii, więc przy stale włączonym ekranie akumulator wystarczy na kilka godzin.
- **Do sprawdzenia:** pojemność akumulatora, a miejsce w obudowie; tryb uśpienia (wygaszony ekran, wybudzanie przy nowej wiadomości lub przycisku); ładowanie przez USB-C.

### 6.2 Sposób przesyłania wiadomości

| Wariant | Zalety | Wady |
|---|---|---|
| A. Bot Telegram, urządzenie łączy się bezpośrednio z Telegramem | Najprostszy, bez serwera, bez kosztów | Klucz bota zapisany w urządzeniu, brak historii, brak kontroli nad danymi |
| B. Własny serwer i strona WWW | Pełna kontrola, baza danych | Mniej wygodne dla użytkownika (osobna strona) |
| C. Bot Telegram + własny serwer pośredniczący | Wygodne dla użytkownika (znany komunikator), baza danych i historia po stronie serwera, potwierdzenie odczytu w Telegramie | Konieczność utrzymania serwera |

### 6.3 Serwer

Gdzie ma działać serwer: komputer zespołu (bez kosztów, ale musi być włączony) czy wynajęty serwer w internecie (niewielki miesięczny koszt, działa stale).

### 6.4 Obudowa

Musi pomieścić: mikrokontroler, ekran, przycisk, diodę, gniazdo USB-C i ewentualnie akumulator z modułem ładowania. Rozmiar i kształt zależą od decyzji w sprawie zasilania (punkt 6.1).

### 6.5 Rozmiar ekranu

Mały ekran jest tańszy i już przetestowany, ale zdjęcia są na nim mniej czytelne. Do oceny na prototypie.

## 7. Wizualizacje koncepcyjne

Wizualizacje wyglądu urządzenia (wygenerowane narzędziem Gemini) zostaną dodane do katalogu `docs/img`.
