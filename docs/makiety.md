# Makiety ekranów sprintu 1

Makiety opisują ekrany, które już działają w aplikacji (widok desktopowy, na telefonie sekcje układają się jedna pod drugą). Czekają na akceptację Właściciela produktu (Daria). Jeśli coś ma wyglądać inaczej, zmiany wpisujemy tutaj, a potem w kodzie.

## 1. Zatwierdzanie wydatków (F8)

Karta „Do zatwierdzenia” stoi nad formularzem dodawania wydatku we wspólnym portfelu. Widzi ją każdy członek portfela, ale przyciski dostaje tylko ten, kto nie jest autorem.

```
+--------------------------------------------------------------+
| DO ZATWIERDZENIA (1)                                         |
| Wydatki powyżej 200,00 zł wchodzą do sum dopiero po          |
| zatwierdzeniu przez innego członka portfela.                 |
|--------------------------------------------------------------|
| 349,00 zł · Zakupy · Daria, 01.11            [Zatwierdź] [Odrzuć]
| Nowa pralka (połowa ceny)                                    |
| 💬 komentarz autora, jeśli go dodał                          |
+--------------------------------------------------------------+
```

Autor tego samego wydatku zamiast przycisków widzi napis „Czeka na decyzję innej osoby”.

Na liście wydatków kwota ma podpis pod spodem: „oczekuje” albo „odrzucony”. Takie wydatki nie liczą się do sum miesiąca, do podziału kosztów ani do limitów.

Próg (domyślnie 200 zł) ustawia właściciel portfela w sekcji „Ustawienia portfela”.

## 2. Limity kategorii i tryb Oszczędny (F10)

Pasek kategorii w karcie „Według kategorii” pokazuje „wydano / limit”. Kolor i podpis zależą od stanu limitu.

```
Poniżej 80%     Jedzenie                 120,00 zł / 600,00 zł
                [#####-----------------------------------]   zielony

Od 80% włącznie Transport                110,00 zł / 120,00 zł
                [#################################-----]   pomarańczowy
                92% limitu

Powyżej 100%    Restauracje i kawiarnie   32,50 zł / 30,00 zł
                [########################################]   czerwony
                Limit przekroczony o 2,50 zł
```

Kategoria bez limitu wygląda jak dotąd, bez drugiej kwoty.

Baner trybu Oszczędnego pojawia się nad kartami w bieżącym miesiącu:

```
+--------------------------------------------------------------+
| Tryb Oszczędny. W kategoriach z limitem wydano już ponad 80% |
| sumy limitów, a miesiąc jeszcze trwa. Odłóż większe zakupy   |
| na następny miesiąc.                                         |
+--------------------------------------------------------------+
```

Limity ustawia się w zwijanej sekcji „Ustawienia portfela” (po jednym polu na kategorię, puste pole usuwa limit). Przy portfelu wspólnym zmienia je tylko właściciel.
