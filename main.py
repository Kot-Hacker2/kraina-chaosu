import time
import sys
import os
import random
import json

# Globalne zmienne stanu gry
name = ""
nazwa_wyprawy = "" # Dodano zmienną
hp = 100          
mana = 100
energia = 1000000  
gold = 5
atak = 10          
posX = 0
posY = 0
ekwipunek = []
krok_tury = 0  

oferta_kowala = {
    "miecze": [
        {"nazwa": "Drewniany Miecz", "cena": 4, "bonus": 5},
        {"nazwa": "Zelazny Miecz", "cena": 12, "bonus": 15},
        {"nazwa": "Smoczy Miecz", "cena": 30, "bonus": 40}
    ],
    "zbroje": [
        {"nazwa": "Skorzana Zbroja", "cena": 4, "bonus": 10},
        {"nazwa": "Kolczuga", "cena": 12, "bonus": 30},
        {"nazwa": "Plytowy Pancerz", "cena": 30, "bonus": 75}
    ]
}

struktury = [(23, -5), (-5, 25), (-40, -40), (50, 50)]

def zapisz_do_logu(wydarzenie):
    """Zapisuje zdarzenie oraz pełny stan zmiennych do pliku logi.json (append)."""
    wpis = {
        "timestamp_krok": krok_tury,
        "wydarzenie": wydarzenie,
        "stan_gracza": {
            "name": name,
            "nazwa_wyprawy": nazwa_wyprawy,
            "hp": hp,
            "mana": mana,
            "energia": energia,
            "gold": gold,
            "atak": atak,
            "posX": posX,
            "posY": posY,
            "ekwipunek": ekwipunek
        }
    }
    try:
        dane_logu = []
        if os.path.exists("logi.json") and os.path.getsize("logi.json") > 0:
            with open("logi.json", "r", encoding="utf-8") as f:
                dane_logu = json.load(f)
        dane_logu.append(wpis)
        with open("logi.json", "w", encoding="utf-8") as f:
            json.dump(dane_logu, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Błąd zapisu logów: {e}]")

def inicjalizuj_gre():
    """Resetuje stan gry oraz czyści plik logów na początku nowej rozgrywki."""
    global name, nazwa_wyprawy, hp, mana, energia, gold, atak, posX, posY, ekwipunek, krok_tury
    hp = 100         
    energia = 1000000  
    gold = 5
    atak = 10          
    ekwipunek = []
    krok_tury = 0
    
    with open("logi.json", "w", encoding="utf-8") as f:
        json.dump([], f)

    if os.name == 'nt': os.system('cls')
    else: os.system('clear')

    print("==================================================")
    print("      KRAINA CHAOSU: EKSPEDYCJA BOGACTWA         ")
    print("==================================================")
    name = input("Zwą mnie: ")
    nazwa_wyprawy = input("Nazwij tę wyprawę: ") # Wprowadzanie nazwy
    
    try:
        mana = int(input("Moja początkowa mana: "))
    except ValueError:
        mana = 100

    print("\nWYBIERZ POZIOM TRUDNOŚCI:")
    print("1. Łatwy (HP x 2)")
    print("2. Normalny (HP x 1)")
    print("3. Trudny (HP x 0.5)")
    wybor = input("Twój wybór (1-3): ")
    
    if wybor == "1": hp = hp*2
    elif wybor == "3": hp = hp*0.5

    posX = gdzie_spawn('X')
    posY = gdzie_spawn('Y')

    print(f"\n--- RAPORT POCZĄTKOWY: {nazwa_wyprawy} ---")
    pisz(f"Budzisz się na pozycji [{posX}, {posY}].")
    pisz("Wszystkie sekrety krainy i współrzędne opisane są w pliku readme.md.")
    pisz("Powszechnie znana jest tylko lokalizacja Kowala: X=23, Y=-5.")
    pisz("twoim celem jest zebranie 1000 sztuk złota")
    pisz("plansza ma wymiary 201x201 (rozciąga się od -100 po 100)")
    
    zapisz_do_logu(f"Inicjalizacja wyprawy '{nazwa_wyprawy}'. Gracz zmaterializowany w dziczy.")

def pokaz_statystyki_koncowe(status_zakonczenia):
    """Wyświetla pełny zrzut wszystkich zmiennych systemowych i obsługuje restart."""
    print("\n==================================================")
    print(f" STATUS KOŃCOWY GRY: {status_zakonczenia}")
    print(f" WYPRAWA: {nazwa_wyprawy}") # Wyświetlanie nazwy
    print("==================================================")
    print(f" [Zmienna: name]       Nazwa gracza: {name}")
    print(f" [Zmienna: hp]         Punkty życia: {hp}")
    print(f" [Zmienna: mana]       Punkty many: {mana}")
    print(f" [Zmienna: energia]    Pozostała energia: {energia}")
    print(f" [Zmienna: gold]       Stan konta (Złoto): {gold}/1000")
    print(f" [Zmienna: atak]       Wartość ataku: {atak}")
    print(f" [Zmienna: posX]       Ostatnia pozycja X: {posX}")
    print(f" [Zmienna: posY]       Ostatnia pozycja Y: {posY}")
    print(f" [Zmienna: ekwipunek]  Zawartość ekwipunku: {ekwipunek}")
    print(f" [Zmienna: krok_tury]  Rozegrane tury/kroki: {krok_tury}")
    print("==================================================")
    
    zapisz_do_logu(f"Koniec gry. Status: {status_zakonczenia}")
    
    while True:
        odp = input("\nCzy chcesz zagrać ponownie? (tak/nie): ").lower()
        if odp == "tak":
            main()
            break
        elif odp == "nie":
            pisz("Dziękujemy za grę! Twój ślad został zapisany w logi.json.")
            sys.exit()

# ... (reszta funkcji pozostaje bez zmian)

def czy_to_mur_z_dziura(x, y):
    if (x == -13 or x == 13) and (-13 <= y <= 13):
        return y != 0
    if (y == -13 or y == 13) and (-13 <= x <= 13):
        return x != 0
    return False

def znajdz_sciezke(start_x, start_y, cel_x, cel_y):
    if (start_x, start_y) == (cel_x, cel_y):
        return []
    
    ograniczony_cel_x = max(-101, min(101, cel_x))
    ograniczony_cel_y = max(-101, min(101, cel_y))

    kolejka = [[(start_x, start_y)]]
    odwiedzone = {(start_x, start_y)}

    while kolejka:
        sciezka = kolejka.pop(0)
        x, y = sciezka[-1]

        if (x, y) == (ograniczony_cel_x, ograniczony_cel_y):
            return sciezka[1:] 

        if x > 100 or x < -100 or y > 100 or y < -100:
            return [(cel_x, cel_y)]

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            
            if -101 <= nx <= 101 and -101 <= ny <= 101:
                if (nx, ny) not in odwiedzone:
                    if czy_to_mur_z_dziura(nx, ny) and (nx, ny) != (ograniczony_cel_x, ograniczony_cel_y):
                        continue
                    if (nx, ny) in struktury and (nx, ny) != (cel_x, cel_y):
                        continue
                    odwiedzone.add((nx, ny))
                    nowa_sciezka = list(sciezka)
                    nowa_sciezka.append((nx, ny))
                    kolejka.append(nowa_sciezka)
    return None 

def sprawdz_zakonczenie_gry():
    global gold
    if gold >= 1000:
        print("\n!!! ZWYCIĘSTWO !!!")
        pisz("Zebrałeś wymagane 1000 sztuk złota i wykupiłeś wolność!")
        pokaz_statystyki_koncowe("WYGRANA (BOGACTWO)")

def walka_z_bossem_chaos(x, y):
    print("\n--------------------------------------------------")
    pisz(f"Wkraczasz na nieznane rubieże [{x}, {y}] poza barierę wymiarową...")
    pisz("Z mroku wyłania się Przedwieczny Chaos. Nie masz najmniejszych szans.")
    pisz("Jednym spojrzeniem obraca Twoje ciało w gwiezdny pył.")
    pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ CHAOS)")

def sprawdz_bossow_regionalnych(x, y):
    global hp, gold, atak
    if x == -50 and y == 60:
        print("\n--------------------------------------------------")
        pisz("[BOSS] Wkraczasz do kamiennego zagajnika. Atakuje Cię Gorgona Meduza!")
        zapisz_do_logu("Spotkanie z bossem: Gorgona Meduza")
        if input("Czy podejmiesz walkę? (tak/nie): ").lower() == "tak":
            b_hp, b_atak = 350, 40
            while b_hp > 0 and hp > 0:
                b_hp -= atak
                if b_hp > 0: hp -= b_atak
            if hp <= 0:
                pisz("Meduza zamieniła Cię w kamień...")
                pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ MEDUZĘ)")
            else:
                gold += 400
                pisz("Pokonałeś Meduzę! Zdobywasz jej skarby (400 sztuk złota).")
                zapisz_do_logu("Pokonano bosa: Gorgona Meduza")
                sprawdz_zakonczenie_gry()
    elif x == 70 and y == -70:
        print("\n--------------------------------------------------")
        pisz("[BOSS] Ziemia pęka, powstaje Władca Podziemi Nergal!")
        zapisz_do_logu("Spotkanie z bossem: Władca Podziemi Nergal")
        if input("Czy podejmiesz walkę? (tak/nie): ").lower() == "tak":
            b_hp, b_atak = 500, 30
            while b_hp > 0 and hp > 0:
                b_hp -= atak
                if b_hp > 0: hp -= b_atak
            if hp <= 0:
                pisz("Nergal wciągnął Cię do otchłani...")
                pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ NERGALA)")
            else:
                gold += 500
                pisz("Zgładziłeś Nergala! Ograbiasz jego kryptę (500 sztuk złota).")
                zapisz_do_logu("Pokonano bosa: Władca Podziemi Nergal")
                sprawdz_zakonczenie_gry()

def wpadniecie_do_studni():
    print("\n--------------------------------------------------")
    pisz("Wkroczyłeś w strefę centralną. Wpadasz prosto do bezdennej Studni!")
    pisz("Woda zalewa Twoje płuca, idziesz na dno...")
    pokaz_statystyki_koncowe("PRZEGRANA (UTONIĘCIE W STUDNI)")

def wywolaj_zdarzenie_losowe():
    global hp, mana, gold, atak
    print("\n--------------------------------------------------")
    wydarzenie = random.choice(["przeciwnik", "przeciwnik", "skrzynia"])
    
    if wydarzenie == "przeciwnik":
        potwor = random.choice([
            {"nazwa": "Głodny Wilk", "hp": 20, "atak": 5, "gold": 25},
            {"nazwa": "Złośliwy Goblin", "hp": 45, "atak": 12, "gold": 60},
            {"nazwa": "Skażony Ork", "hp": 90, "atak": 22, "gold": 150}
        ])
        print(f"[ZDARZENIE AMBUSH] Nagle zza drzew wyskakuje {potwor['nazwa']}!")
        zapisz_do_logu(f"Atak potwora: {potwor['nazwa']}")
        
        p_hp = potwor["hp"]
        while p_hp > 0 and hp > 0:
            p_hp -= atak
            if p_hp > 0: hp -= potwor["atak"]
            
        if hp <= 0:
            pisz("Zginąłeś marnie w walce z potworem podczas wędrówki.")
            pokaz_statystyki_koncowe("PRZEGRANA (ZABITY W DZICZY)")
        else:
            loot = potwor["gold"] + random.randint(5, 20)
            gold += loot
            print(f"Zwycięstwo! Pokonałeś potwora i znajdujesz {loot} sztuk złota!")
            zapisz_do_logu(f"Zwycięstwo nad {potwor['nazwa']}. Łup: {loot}g")
            sprawdz_zakonczenie_gry()
            
    elif wydarzenie == "skrzynia":
        znalezione = random.randint(40, 90)
        gold += znalezione
        print(f"[ODKRYCIE] Przy ścieżce znalazłeś porzuconą skrzynię, a w niej {znalezione} złota!")
        zapisz_do_logu(f"Znaleziono skrzynię ze złotem: {znalezione}g")
        sprawdz_zakonczenie_gry()
    print("--------------------------------------------------")

def podrozuj(cel_x, cel_y):
    """SYSTEM PODRÓŻY Z LICZNIKIEM CZASU RZECZYWISTEGO (Bez kropek, 1 krok = 2 sekundy)."""
    global posX, posY, energia, krok_tury
    
    trasa = znajdz_sciezke(posX, posY, cel_x, cel_y)
    if trasa is None:
        pisz("Droga jest zablokowana przez wewnętrzne mury!")
        return False

    dlugosc_trasy = len(trasa)
    if dlugosc_trasy == 0:
        pisz("Już stoisz na wskazanych współrzędnych.")
        return True
        
    calkowity_czas = dlugosc_trasy * 0.2
    pisz(f"\nWyruszasz w pieszą wędrówkę do [{cel_x}, {cel_y}].")
    pisz(f"Dystans: {dlugosc_trasy} pól. Szacowany czas podróży: {calkowity_czas} sekund...")
    
    wystapi_zdarzenie = random.randint(1, 70) <= 15
    krok_zdarzenia = -1

    if wystapi_zdarzenie:
        bezpieczne_indeksy = [i for i, pole in enumerate(trasa) if pole not in struktury]
        if bezpieczne_indeksy:
            krok_zdarzenia = random.choice(bezpieczne_indeksy)

    for indeks, nastepne_pole in enumerate(trasa):
        pozostalo_sekund = (dlugosc_trasy - indeks) * 0.2
        print(f"\r[Podróż trwa] Pozycja: {nastepne_pole} | Pozostały czas: {pozostalo_sekund:.1f}s...")
        sys.stdout.flush()
        
        time.sleep(0.2)
        
        posX, posY = nastepne_pole
        energia -= 1
        krok_tury += 1 
        
        if posX > 100 or posX < -100 or posY > 100 or posY < -100:
            print()
            walka_z_bossem_chaos(posX, posY)
        if -2 <= posX <= 2 and -2 <= posY <= 2:
            print()
            wpadniecie_do_studni()
            
        sprawdz_bossow_regionalnych(posX, posY)
        
        if indeks == krok_zdarzenia:
            print() 
            wywolaj_zdarzenie_losowe()
        
    print(f"\n► Cel osiągnięty! Bezpiecznie dotarłeś do punktu końcowego.")
    zapisz_do_logu(f"Zakończono podróż do [{posX}, {posY}]. Dystans: {dlugosc_trasy} kroków.")
    return True

def sklep_kowala():
    global gold, hp, atak
    zapisz_do_logu("Wejście do kuźni kowala")
    while True:
        print(f"\n=================== SKLEP KOWALA (23, -5) ===================")
        print(f"Złoto: {gold} | Twój Atak: {atak} | Twoje HP: {hp}")
        wybor = input("1. Kup Miecz / 2. Kup Zbroję / 3. Wyjdź przed kuźnię: ")
        if wybor == "1":
            for i, m in enumerate(oferta_kowala["miecze"], 1):
                print(f"  {i}. {m['nazwa']} (+{m['bonus']} Atak) - {m['cena']}g")
            try:
                kup = int(input("Wybór: "))
                if 1 <= kup <= 3:
                    m = oferta_kowala["miecze"][kup-1]
                    if gold >= m["cena"]: 
                        gold -= m["cena"]; atak += m["bonus"]; ekwipunek.append(m["nazwa"])
                        zapisz_do_logu(f"Zakupiono broń: {m['nazwa']}")
                    else: print("Brak złota!")
            except ValueError: pass
        elif wybor == "2":
            for i, z in enumerate(oferta_kowala["zbroje"], 1):
                print(f"  {i}. {z['nazwa']} (+{z['bonus']} HP) - {z['cena']}g")
            try:
                kup = int(input("Wybór: "))
                if 1 <= kup <= 3:
                    z = oferta_kowala["zbroje"][kup-1]
                    if gold >= z["cena"]: 
                        gold -= z["cena"]; hp += z["bonus"]; ekwipunek.append(z["nazwa"])
                        zapisz_do_logu(f"Zakupiono pancerz: {z['nazwa']}")
                    else: print("Brak złota!")
            except ValueError: pass
        elif wybor == "3": 
            zapisz_do_logu("Opuszczenie kuźni kowala")
            break

def karczma():
    global gold
    print("\n=================== PRZEKLETA KARCZMA ===================")
    if input("Upić się do nieprzytomności za 1 złota? (tak/nie): ").lower() == "tak" and gold >= 1:
        gold -= 1
        zapisz_do_logu("Gracz upił się w karczmie - kapitulacja.")
        pisz("\nZasypiasz pod ciężkim, dębowym stołem. Świat i potwory przestają Cię obchodzić...")
        pokaz_statystyki_koncowe("UPICIE CZYLI NIE PRZEGRANA")

def swiatynia():
    global gold, hp
    print("\n=================== ANGIELSKA ŚWIĄTYNIA ===================")
    if input("Uleczyć rany i odzyskać siły za 20 złota? (tak/nie): ").lower() == "tak" and gold >= 20:
        gold -= 20
        hp = 100
        pisz("Boska energia przepływa przez Twoje ciało. Zostałeś w pełni uleczony!")
        zapisz_do_logu("Pełne leczenie w Świątyni za 20g.")

def magiczny_portal():
    global posX, posY
    print("\n=================== ANOMALIA: PORTAL MAGICZNY ===================")
    pisz("Portal wciąga Cię kosmiczną siłą i gwałtownie zniekształca czasoprzestrzeń...")
    time.sleep(1.0)
    posX, posY = random.randint(-90, 90), random.randint(-90, 90)
    if -2 <= posX <= 2 and -2 <= posY <= 2: posX, posY = 15, 15
    pisz(f"Wyrzuciło Cię w nieznanym zakątku świata: [{posX}, {posY}]!")
    zapisz_do_logu(f"Użycie portalu. Losowa teleportacja na pozycję [{posX}, {posY}].")

def gdzie_spawn(oS):
    try:
        wartość = int(input(f"W osi {oS} zacznę (od -12 do 12, bez -2 do 2) gdy wartość błędna pojawisz się na 12 w danej osi: "))
        if -2 <= wartość <= 2 or not (-12 <= wartość <= 12): return 12
        return wartość
    except ValueError: return 12

def pisz(tekst, opoznienie=0.005):
    for litera in tekst:
        print(litera, end="", flush=True)
        time.sleep(opoznienie)
    print()

def main():
    global posX, posY
    inicjalizuj_gre()
    
    while True:
        if posX == 23 and posY == -5: sklep_kowala()
        elif posX == -5 and posY == 25: karczma()
        elif posX == -40 and posY == -40: swiatynia()
        elif posX == 50 and posY == 50: magiczny_portal()

        print(f"\n=================== [TURA / KROKI W GRZE: {krok_tury}] ===================")
        print(" OBECNY STAN ZASOBÓW:")
        print(f" -> Pozycja: [{posX}, {posY}]")
        print(f" -> Punkty Życia (HP): {hp}")
        print(f" -> Punkty Many: {mana}")
        print(f" -> Energia życiowa: {energia}")
        print(f" -> Posiadane Złoto: {gold} / 1000")
        print(f" -> Siła Ataku: {atak}")
        print(f" -> Ekwipunek: {ekwipunek}")
        print("=========================================================")

        pisz("Gdzie nakazujesz podróżować? (Siatka mapy: -100 do 100)")
        try:
            cel_x = int(input("Cel X: "))
            cel_y = int(input("Cel Y: "))
            podrozuj(cel_x, cel_y)
        except ValueError: 
            print("Błąd! Podaj poprawne współrzędne liczbowe.")

if __name__ == "__main__":
    main()
