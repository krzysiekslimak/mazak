*[English](README.md) | Polski*

# Mazak

Lekki edytor do adnotowania zrzutów ekranu (mockupy, dokumentacja, feedback) — strzałki, dymki, tekst, ramki, naklejki, rozmycie/pikselizacja i przycinanie, każdy z panelem konfiguracji koloru, grubości, kształtu i cienia. Napisany w Pythonie / PySide6 (Qt6), natywna aplikacja na Linuksa.

![Zrzut ekranu Mazaka](docs/screenshot.png)

Mazak **nie robi zrzutów ekranu** — do tego służy natywne narzędzie Twojego systemu (np. `Shift+Print Screen` na GNOME). Mazak otwiera już zrobiony obraz (z pliku albo prosto ze schowka) i pozwala go oznaczyć.

## Funkcje

- **Strzałka** — kolor, grubość, 3 style (klasyczna / cienka / gruba), cień
- **Dymek** — kolor, 3 kształty (zaokrąglony / owalny / chmurka), obramowanie on/off, cień, tekst wewnątrz (czcionka, rozmiar, pogrubienie, kolor tekstu, cień tekstu)
- **Tekst** — kolor, czcionka, rozmiar, pogrubienie, cień
- **Ramka** — kolor, grubość, ostre/zaokrąglone rogi, cień
- **Naklejki** — 6 gotowych symboli (wykrzyknik, znak zapytania, ptaszek, krzyżyk, gwiazdka, ostrzeżenie), kolor, rozmiar, cień
- **Rozmycie/pikselizacja** — przeciągnij po wrażliwych danych (hasła, maile), żeby je zasłonić, z regulowaną intensywnością
- **Przycinanie** — zaznacz obszar przeciągnięciem, potem zastosuj lub anuluj; istniejące elementy są odpowiednio przesuwane lub usuwane
- Kliknięcie już postawionego elementu narzędziem **Zaznacz** ponownie pokazuje jego panel — można edytować na żywo bez rysowania od nowa
- **Wklejanie ze schowka** (Ctrl+V) i **kopiowanie wyniku do schowka** (Ctrl+C) — oba działają tylko gdy płótno ma fokus, więc nie kolidują z polami tekstowymi w panelach
- Wielopoziomowy **undo/redo** (Ctrl+Z / Ctrl+Shift+Z) obejmujący dodawanie, usuwanie i edycję elementów
- Powiększanie/pomniejszanie/dopasowanie (toolbar, Ctrl+scroll albo Ctrl+/Ctrl-), z gładkim (niepikselowanym) skalowaniem obrazu
- Eksport spłaszczony do PNG, zapamiętywanie ostatnio używanego folderu (otwieranie i eksport osobno)

## Instalacja

### Pakiet .deb (Ubuntu/Debian, zalecane)

Pobierz najnowszy plik `.deb` z zakładki [Releases](../../releases) i zainstaluj:

```bash
sudo apt install ./mazak_*.deb
```

Pakiet zawiera własny, samodzielny zestaw PySide6 — nie wymaga niczego dodatkowego z internetu podczas instalacji. Po instalacji znajdziesz „Mazak” w menu aplikacji.

### Ze źródeł

Wymagany Python 3.10+.

```bash
git clone https://github.com/krzysiekslimak/mazak.git
cd mazak
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./run.sh
```

## Rozwój / uruchamianie testowe

Projekt nie ma zewnętrznego frameworka testowego — logikę weryfikuje się poprzez uruchomienie aplikacji i ręczne (lub `QTest`-owe) przejście przez dany przepływ. Struktura kodu:

```
mazak/
├── main_window.py   # okno główne, toolbar, panele właściwości
├── canvas.py         # QGraphicsView/Scene, obsługa rysowania, schowek, przycinanie
├── items.py           # klasy elementów (ArrowItem, SpeechBubbleItem, TextAnnotationItem, FrameItem, StickerItem, BlurRegionItem)
├── panels.py          # kontekstowe panele ustawień dla każdego narzędzia
├── undo.py             # stos undo/redo oparty o komendy
├── icons.py              # generowane programowo ikony (bez plików graficznych)
├── style.py               # arkusz stylów Qt (QSS)
└── tools.py                # enumy narzędzi i wariantów (Tool, ArrowStyle, BubbleShape, StickerKind)
```

## Licencja

[MIT](LICENSE)
