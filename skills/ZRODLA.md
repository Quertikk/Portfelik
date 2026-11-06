# Źródła skilli

Foldery w `skills/` zawierają pliki `SKILL.md` skilli, z których autor korzysta przy budowie projektu. Skill to zestaw instrukcji dla asystenta AI (Claude Code). Skille nie są częścią aplikacji.

| Skill | Do czego służy w projekcie | Źródło | Licencja |
|---|---|---|---|
| `ponytail` | Pisanie i przegląd kodu: najmniejsza zmiana, która w pełni rozwiązuje zadanie | https://github.com/DietrichGebert/ponytail (wersja 5.0.0) | MIT, plik `ponytail/LICENSE` |
| `sztuczny-miodek` | Korekta polskich tekstów i bramka jakości przed uznaniem dokumentu za gotowy | https://github.com/researchanddeploy/sztuczny-miodek (wersja 1.1.0) | MIT, plik `sztuczny-miodek/LICENSE` |
| `academic-pptx` | Prezentacje na spotkania tygodniowe i prezentacja końcowa | Skill synchronizowany z konta claude.ai (zestaw `anthropic-skills`) | MIT według pliku `academic-pptx/LICENSE`; w nagłówku `SKILL.md` stoi zapis „Proprietary", więc sprawdź przed dalszym udostępnianiem |
| `ui-ux-pro-max` | Projekt interfejsu: szablony i style | Skill synchronizowany z konta claude.ai (zestaw `anthropic-skills`) | Lokalna kopia nie zawiera informacji o licencji |

W folderach leży tylko plik `SKILL.md` (oraz `LICENSE`, jeśli był dostępny). Skille `sztuczny-miodek` i `academic-pptx` korzystają też z plików pomocniczych, których tu nie ma, na przykład linter `ai_linter.py` albo katalog `references/`. Pełne wersje są w repozytoriach źródłowych.

Pozostałe skille w tym folderze (`scrum-master`, `agile-coach`, `polish-correct`, `humanizer-pl`, `humanizer`) dodano wcześniej. Ich źródeł tu nie opisano.
