# Diagramy UML

Diagramy w składni Mermaid, GitHub rysuje je w podglądzie pliku. Architektura i model danych są w [specyfikacji](specyfikacja.md#4-architektura).

## Przypadki użycia

```mermaid
flowchart LR
    U([Użytkownik])
    C([Członek wspólnego portfela])
    W([Właściciel portfela])
    M([Model AI])

    U --> UC1(Zarejestrować się i zalogować)
    U --> UC2(Dodać, edytować, usunąć wydatek)
    U --> UC3(Dodać wydatek ze zdjęcia paragonu)
    U --> UC4(Przeglądać podsumowanie i wykres ze średnią)
    U --> UC5(Prowadzić subskrypcje)
    U --> UC6(Pobrać wydatki miesiąca jako CSV)
    C --> UC7(Zatwierdzić lub odrzucić cudzy wydatek)
    C --> UC8(Zobaczyć rozliczenie)
    C --> UC9(Dołączyć przez link zaproszenia)
    W --> UC10(Ustawić próg zatwierdzania i limity)
    W --> UC11(Utworzyć link zaproszenia)
    UC3 -.-> M
    C -. jest też .-> U
    W -. jest też .-> C
```

## Sekwencja: dodanie wydatku ze zdjęcia paragonu (F11)

```mermaid
sequenceDiagram
    actor U as Użytkownik
    participant A as app.py (receipt)
    participant R as receipts.py
    participant M as Model AI (Gemini)
    participant B as SQLite

    U->>A: POST /portfel/id/paragon (JPG lub PNG, do 5 MB)
    A->>A: get_wallet (członkostwo), rozpoznanie typu po zawartości
    alt zły typ lub plik za duży
        A-->>U: komunikat, ręczne wprowadzanie
    else poprawny obraz
        A->>R: read_receipt(bajty, mime)
        R->>M: obraz + polecenie (klucz z GEMINI_API_KEY)
        M-->>R: JSON: kwota, data, sklep, kategoria
        R-->>A: słownik z polami tekstowymi
        A->>A: walidacja: parse_amount, date.fromisoformat, kategoria z bazy
        A-->>U: przekierowanie na portfel z wypełnionym formularzem
    end
    Note over A,B: Zdjęcie jest tylko w pamięci, do bazy nic nie trafia
    U->>A: POST /portfel/id/dodaj (po poprawkach)
    A->>B: INSERT expenses (status wg progu zatwierdzania)
    A-->>U: portfel z nowym wydatkiem
```

## Stany wydatku

```mermaid
stateDiagram-v2
    [*] --> approved: dodanie, portfel osobisty lub kwota do progu
    [*] --> pending: dodanie, portfel wspólny i kwota powyżej progu
    pending --> approved: zatwierdza inny członek
    pending --> rejected: odrzuca inny członek
    approved --> pending: autor podnosi kwotę powyżej progu
    approved --> approved: edycja opisu, kategorii, daty lub kwoty do progu
    rejected --> rejected: edycja (status zostaje)
    approved --> [*]: usunięcie przez autora
    pending --> [*]: usunięcie przez autora
    rejected --> [*]: usunięcie przez autora
```

Do sum miesiąca, kategorii, osób, limitów i rozliczenia wchodzą tylko wydatki w stanie `approved`.
