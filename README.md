# 🌌 KRAINA CHAOSU: EKSPEDYCJA BOGACTWA
## Oficjalna Dokumentacja Techniczna Świata Gry (v2.6)

Witaj w Przeklętej Krainie – surowym, tekstowym uniwersum RPG zamkniętym w barierze wymiarowej od -100 do 100 na osiach X i Y. Twoim celem jest zebranie 1000 sztuk złota, aby wykupić wolność.

**UWAGA (Bezpieczeństwo):** Przed przystąpieniem do uruchomienia upewnij się, że pobrałeś z repozytorium i zapisałeś w jednym folderze na swoim komputerze oba wymagane pliki: `main.py` oraz `README.md`

### 🚀0. INSTRUKCJA URUCHOMIENIA
A.
1. Upewnij się, że masz zainstalowanego Pythona w wersji 3.11 lub nowszej.
2. Otwórz terminal / wiersz poleceń w folderze z projektem.
3. Uruchom grę wpisując polecenie:
   python main.py
B
1. Upewnij się, że masz zainstalowanego Pythona w wersji 3.11 lub nowszej.
2. otwórz folder z plikami
3. kliknij dwukrotnie na plik main.py
---

## 📜 1. STATYSTYKI I ZASOBY GRACZA
* **HP**: Startujesz ze 100 pkt. Spadek do 0 oznacza śmierć.
* **Energia Życiowa**: Startujesz z 1 000 000 pkt. Każdy wykonany krok kosztuje **1 pkt energii**.
* **Złoto**: Zbierasz je, aby osiągnąć status `WYGRANA`.
* **Atak**: Bazowo 10 pkt. Zwiększany przez miecze.
* **Krok_tury**: Licznik realnie wykonanych ruchów na mapie.

---

## 🧭 2. SYSTEM PODRÓŻY I MECHANIKA ŚWIATA
* **Czas**: Każdy krok zajmuje 2 sekundy czasu rzeczywistego.
* **Zużycie Energii**: 1 krok = 1 pkt energii.
* **Zdarzenia Losowe**: Szansa 15/70 na turę. Aktywują się tylko na polach "dziczy" (poza strukturami).
* **Spawn**: Wybierasz pozycję od -12 do 12. Unikaj strefy Studni (-2 do 2), w przeciwnym razie system zrzuci Cię na pozycję [12, 12].

---

## 🧱 3. ARCHITEKTURA MAPY: MUR Z DZIURĄ
Świat posiada niewidzialną barierę:
* **Mur**: Rozciąga się na liniach X=±13 oraz Y=±13.
* **Przejście**: Jedyną drogą przez mur są punkty, w których X=0 lub Y=0. Próba przejścia przez inne pola zostanie zablokowana przez algorytm ścieżki.

---

## 🏛️ 4. STRUKTURY I BOSSOWIE
* **Kuźnia [23, -5]**: Handel mieczami i zbrojami.
* **Świątynia [-40, -40]**: Leczenie do 100 HP za 20 złota.
* **Karczma [-5, 25]**: Możliwość kapitulacji poprzez "upicie się".
* **Magiczny Portal [50, 50]**: Teleportacja losowa. Jeśli system wylosuje strefę Studni, bezpiecznik przeniesie Cię na [15, 15].
* **Głęboka Studnia [0, 0]**: Strefa 5x5 (od -2 do 2). Wkroczenie = natychmiastowa śmierć.
* **Bossowie**: Gorgona Meduza [-50, 60] (350 HP, 40 Atak) oraz Nergal [70, -70] (500 HP, 30 Atak).

---

## ⚔️ 5. BESTIARIUSZ
| Nazwa | HP | Atak | Łup Bazowy | Bonus |
| :--- | :--- | :--- | :--- | :--- |
| Głodny Wilk | 20 | 5 | 25g | +5-20g |
| Złośliwy Goblin | 45 | 12 | 60g | +5-20g |
| Skażony Ork | 90 | 22 | 150g | +5-20g |

---

## 💰 6. CENNIK KOWALA
**Broń (Atak)**: 
* Drewniany (+5): 4g 
* Żelazny (+15): 12g 
* Smoczy (+40): 30g

**Zbroje (HP)**: 
* Skórzana (+10): 4g 
* Kolczuga (+30): 12g 
* Płytowy (+75): 30g

---

## 💡 7. STRATEGIA
1. **Początek**: Kup Drewniany Miecz u Kowala zaraz po spawnie.
2. **Nawigacja**: Zawsze szukaj "dziur" w murze na liniach zerowych.
3. **Ekonomia**: Nie walcz z bossami, dopóki nie zdobędziesz Smoczego Miecza i Płytowej Zbroi.
4. **Logi**: Każda akcja jest zapisywana w pliku `logi.json` dla celów analitycznych.

---

### 💾 SYSTEM LOGOWANIA (MECHANIKA DODATKOWA)
Gra posiada zaimplementowany automatyczny system rejestracji zdarzeń. 
Podczas rozgrywki w folderze głównym programu automatycznie wygeneruje się plik `logi.json`. 

Zawiera on pełną historię wyprawy (krok po kroku) wraz ze szczegółowym zrzutem stanu wszystkich zasobów gracza (HP, złoto, pozycja, ekwipunek) po każdym wykonanym ruchu. Plik ten jest czyszczony i tworzony na nowo przy każdym uruchomieniu nowej gry.
