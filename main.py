import time
import sys
import os
import random
import json

# --- KOLORY ANSI (Klimat starego terminala RPG) ---
C_RESET = "\033[0m"
C_ZŁOTO = "\033[1;33m"
C_ZIELONY = "\033[0;32m"
C_CZERWONY = "\033[1;31m"
C_CYAN = "\033[0;36m"
C_FIOLET = "\033[1;35m"
C_MAGENTA = "\033[0;35m"
C_BIAŁY = "\033[1;37m"
C_SZARY = "\033[0;37m"

# Globalne zmienne stanu gry
name = ""
hp = 100         
mana = 100
energia = 1000000  
gold = 5
atak = 10          
posX = 0
posY = 0
ekwipunek = []
krok_tury = 0  # Naprawione: startujemy od 0 kroków wykonanych

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
        print(f"{C_CZERWONY}[Błąd zapisu logów: {e}]{C_RESET}")

def inicjalizuj_gre():
    """Resetuje stan gry oraz czyści plik logów na początku nowej rozgrywki."""
    global name, hp, mana, energia, gold, atak, posX, posY, ekwipunek, krok_tury
    hp = 100         
    mana = 100
    energia = 1000000  
    gold = 5
    atak = 10          
    ekwipunek = []
    krok_tury = 0
    
    # Czyszczenie/Inicjalizacja pliku logi.json
    with open("logi.json", "w", encoding="utf-8") as f:
        json.dump([], f)

    if os.name == 'nt': os.system('cls')
    else: os.system('clear')

    print(f"{C_ZŁOTO}==================================================")
    print(f"       KRAINA CHAOSU: EKSPEDYCJA BOGACTWA         ")
    print(f"=================================================={C_RESET}")
    name = input(f"{C_BIAŁY}Zwą mnie: {C_RESET}")
    
    posX = gdzie_spawn('X')
    posY = gdzie_spawn('Y')

    pisz(f"\n{C_ZIELONY}Budzisz się na pozycji [{posX}, {posY}].{C_RESET}")
    pisz(f"{C_SZARY}Wszystkie sekrety krainy i współrzędne opisane są w pliku readme.md.{C_RESET}")
    pisz(f"{C_CYAN}Powszechnie znana jest tylko lokalizacja Kowala: X=23, Y=-5.{C_RESET}")
    
    zapisz_do_logu("Inicjalizacja nowej rozgrywki. Gracz zmaterializowany w dziczy.")

def pokaz_statystyki_koncowe(status_zakonczenia):
    """Wyświetla pełny zrzut wszystkich zmiennych systemowych i obsługuje restart."""
    print(f"\n{C_CZERWONY}==================================================")
    print(f" STATUS KOŃCOWY GRY: {status_zakonczenia}")
    print(f"=================================================={C_RESET}")
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
    print(f"{C_CZERWONY}=================================================={C_RESET}")
    
    zapisz_do_logu(f"Koniec gry. Status: {status_zakonczenia}")
    
    while True:
        odp = input(f"\n{C_BIAŁY}Czy chcesz zagrać ponownie? (tak/nie): {C_RESET}").lower()
        if odp == "tak":
            main()
            break
        elif odp == "nie":
            pisz(f"{C_ZŁOTO}Dziękujemy za grę! Twój ślad został zapisany w logi.json.{C_RESET}")
            sys.exit()

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
        print(f"\n{C_ZŁOTO}!!! ZWYCIĘSTWO !!!{C_RESET}")
        pisz("Zebrałeś wymagane 1000 sztuk złota i wykupiłeś wolność!")
        pokaz_statystyki_koncowe("WYGRANA (BOGACTWO)")

def walka_z_bossem_chaos(x, y):
    print(f"\n{C_CZERWONY}--------------------------------------------------")
    pisz(f"Wkraczasz na nieznane rubieże [{x}, {y}] poza barierę wymiarową...")
    pisz("Z mroku wyłania się Przedwieczny Chaos. Nie masz najmniejszych szans.")
    pisz(f"Jednym spojrzeniem obraca Twoje ciało w gwiezdny pył.{C_RESET}")
    pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ CHAOS)")

def sprawdz_bossow_regionalnych(x, y):
    global hp, gold, atak
    if x == -50 and y == 60:
        print(f"\n{C_CZERWONY}--------------------------------------------------")
        pisz("[BOSS] Wkraczasz do kamiennego zagajnika. Atakuje Cię Gorgona Meduza!{C_RESET}")
        zapisz_do_logu("Spotkanie z bossem: Gorgona Meduza")
        if input(f"{C_BIAŁY}Czy podejmiesz walkę? (tak/nie): {C_RESET}").lower() == "tak":
            b_hp, b_atak = 350, 40
            while b_hp > 0 and hp > 0:
                b_hp -= atak
                if b_hp > 0: hp -= b_atak
            if hp <= 0:
                pisz(f"{C_CZERWONY}Meduza zamieniła Cię w kamień...{C_RESET}")
                pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ MEDUZĘ)")
            else:
                gold += 400
                pisz(f"{C_ZŁOTO}Pokonałeś Meduzę! Zdobywasz jej skarby (400 sztuk złota).{C_RESET}")
                zapisz_do_logu("Pokonano bosa: Gorgona Meduza")
                sprawdz_zakonczenie_gry()
    elif x == 70 and y == -70:
        print(f"\n{C_CZERWONY}--------------------------------------------------")
        pisz("[BOSS] Ziemia pęka, powstaje Władca Podziemi Nergal!{C_RESET}")
        zapisz_do_logu("Spotkanie z bossem: Władca Podziemi Nergal")
        if input(f"{C_BIAŁY}Czy podejmiesz walkę? (tak/nie): {C_RESET}").lower() == "tak":
            b_hp, b_atak = 500, 30
            while b_hp > 0 and hp > 0:
                b_hp -= atak
                if b_hp > 0: hp -= b_atak
            if hp <= 0:
                pisz(f"{C_CZERWONY}Nergal wciągnął Cię do otchłani...{C_RESET}")
                pokaz_statystyki_koncowe("PRZEGRANA (ZABITY PRZEZ NERGALA)")
            else:
                gold += 500
                pisz(f"{C_ZŁOTO}Zgładziłeś Nergala! Ograbiasz jego kryptę (500 sztuk złota).{C_RESET}")
                zapisz_do_logu("Pokonano bosa: Władca Podziemi Nergal")
                sprawdz_zakonczenie_gry()

def wpadniecie_do_studni():
    print(f"\n{C_CZERWONY}--------------------------------------------------")
    pisz("Wkroczyłeś w strefę centralną. Wpadasz prosto do bezdennej Studni!")
    pisz(f"Woda zalewa Twoje płuca, idziesz na dno...{C_RESET}")
    pokaz_statystyki_koncowe("PRZEGRANA (UTONIĘCIE W STUDNI)")

def wywolaj_zdarzenie_losowe():
    global hp, mana, gold, atak
    print(f"\n{C_MAGENTA}--------------------------------------------------")
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
            pisz(f"{C_CZERWONY}Zginąłeś marnie w walce z potworem podczas wędrówki.{C_RESET}")
            pokaz_statystyki_koncowe("PRZEGRANA (ZABITY W DZICZY)")
        else:
            loot = potwor["gold"] + random.randint(5, 20)
            gold += loot
            print(f"{C_ZŁOTO}Zwycięstwo! Pokonałeś potwora i znajdujesz {loot} sztuk złota!{C_RESET}")
            zapisz_do_logu(f"Zwycięstwo nad {potwor['nazwa']}. Łup: {loot}g")
            sprawdz_zakonczenie_gry()
            
    elif wydarzenie == "skrzynia":
        znalezione = random.randint(40, 90)
        gold += znalezione
        print(f"{C_ZŁOTO}[ODKRYCIE] Przy ścieżce znalazłeś porzuconą skrzynię, a w niej {znalezione} złota!{C_RESET}")
        zapisz_do_logu(f"Znaleziono skrzynię ze złotem: {znalezione}g")
        sprawdz_zakonczenie_gry()
    print(f"{C_MAGENTA}--------------------------------------------------{C_RESET}")

def podrozuj(cel_x, cel_y):
    """SYSTEM PODRÓŻY Z LICZNIKIEM CZASU RZECZYWISTEGO (Bez kropek, 1 krok = 2 sekundy)."""
    global posX, posY, energia, krok_tury
    
    trasa = znajdz_sciezke(posX, posY, cel_x, cel_y)
    if trasa is None:
        pisz(f"{C_CZERWONY}Droga jest zablokowana przez wewnętrzne mury!{C_RESET}")
        return False

    dlugosc_trasy = len(trasa)
    if dlugosc_trasy == 0:
        pisz(f"{C_SZARY}Już stoisz na wskazanych współrzędnych.{C_RESET}")
        return True
        
    calkowity_czas = dlugosc_trasy * 2
    pisz(f"\n{C_CYAN}Wyruszasz w pieszą wędrówkę do [{cel_x}, {cel_y}].")
    pisz(f"Dystans: {dlugosc_trasy} pól. Szacowany czas podróży: {calkowity_czas} sekund...{C_RESET}")
    
    # Losowanie szansy na zdarzenie (15 na 70)
    wystapi_zdarzenie = random.randint(1, 70) <= 15
    krok_zdarzenia = -1

    if wystapi_zdarzenie:
        bezpieczne_indeksy = [i for i, pole in enumerate(trasa) if pole not in struktury]
        if bezpieczne_indeksy:
            krok_zdarzenia = random.choice(bezpieczne_indeksy)

    # Przemierzanie trasy
    for indeks, nastepne_pole in enumerate(trasa):
        # 1 KROK = 2 SEKUNDY (Odliczanie czasu rzeczywistego dla tego pola)
        pozostalo_sekund = (dlugosc_trasy - indeks) * 2
        sys.stdout.write(f"\r{C_SZARY}[Podróż trwa] Pozycja: {nastepne_pole} | Pozostały czas: {pozostalo_sekund}s...{C_RESET}")
        sys.stdout.flush()
        
        time.sleep(2.0)
        
        # Oficjalne nadpisanie pozycji i zasobów PO upływie czasu tego kroku
        posX, posY = nastepne_pole
        energia -= 1
        krok_tury += 1  # Dokładne podbicie licznika o realnie wykonany krok
        
        # Sprawdzanie pułapek mechanicznych
        if posX > 100 or posX < -100 or posY > 100 or posY < -100:
            print()
            walka_z_bossem_chaos(posX, posY)
        if -2 <= posX <= 2 and -2 <= posY <= 2:
            print()
            wpadniecie_do_studni()
            
        sprawdz_bossow_regionalnych(posX, posY)
        
        # Aktywacja zdarzenia losowego
        if indeks == krok_zdarzenia:
            print() # Nowa linia, aby zdarzenie nie nadpisało licznika czasu
            wywolaj_zdarzenie_losowe()
        
    print(f"\n{C_ZIELONY}► Cel osiągnięty! Bezpiecznie dotarłeś do punktu końcowego.{C_RESET}")
    zapisz_do_logu(f"Zakończono podróż do [{posX}, {posY}]. Dystans: {dlugosc_trasy} kroków.")
    return True

def sklep_kowala():
    global gold, hp, atak
    zapisz_do_logu("Wejście do kuźni kowala")
    while True:
        print(f"\n{C_ZŁOTO}=================== SKLEP KOWALA (23, -5) ===================")
        print(f"Złoto: {gold} | Twój Atak: {atak} | Twoje HP: {hp}{C_RESET}")
        wybor = input(f"{C_BIAŁY}1. Kup Miecz / 2. Kup Zbroję / 3. Wyjdź przed kuźnię: {C_RESET}")
        if wybor == "1":
            for i, m in enumerate(oferta_kowala["miecze"], 1):
                print(f"  {i}. {m['nazwa']} (+{m['bonus']} Atak) - {m['cena']}g")
            try:
                kup = int(input(f"{C_BIAŁY}Wybór: {C_RESET}"))
                if 1 <= kup <= 3:
                    m = oferta_kowala["miecze"][kup-1]
                    if gold >= m["cena"]: 
                        gold -= m["cena"]; atak += m["bonus"]; ekwipunek.append(m["nazwa"])
                        zapisz_do_logu(f"Zakupiono broń: {m['nazwa']}")
                    else: print(f"{C_CZERWONY}Brak złota!{C_RESET}")
            except ValueError: pass
        elif wybor == "2":
            for i, z in enumerate(oferta_kowala["zbroje"], 1):
                print(f"  {i}. {z['nazwa']} (+{z['bonus']} HP) - {z['cena']}g")
            try:
                kup = int(input(f"{C_BIAŁY}Wybór: {C_RESET}"))
                if 1 <= kup <= 3:
                    z = oferta_kowala["zbroje"][kup-1]
                    if gold >= z["cena"]: 
                        gold -= z["cena"]; hp += z["bonus"]; ekwipunek.append(z["nazwa"])
                        zapisz_do_logu(f"Zakupiono pancerz: {z['nazwa']}")
                    else: print(f"{C_CZERWONY}Brak złota!{C_RESET}")
            except ValueError: pass
        elif wybor == "3": 
            zapisz_do_logu("Opuszczenie kuźni kowala")
            break

def karczma():
    global gold
    print(f"\n{C_MAGENTA}=================== PRZEKLETA KARCZMA ===================")
    if input(f"{C_BIAŁY}Upić się do nieprzytomności za 1 złota? (tak/nie): {C_RESET}").lower() == "tak" and gold >= 1:
        gold -= 1
        zapisz_do_logu("Gracz upił się w karczmie - kapitulacja.")
        pisz(f"\n{C_SZARY}Zasypiasz pod ciężkim, dębowym stołem. Świat i potwory przestają Cię obchodzić...{C_RESET}")
        pokaz_statystyki_koncowe("UPICIE CZYLI NIE PRZEGRANA")

def swiatynia():
    global gold, hp
    print(f"\n{C_ZIELONY}=================== ANGIELSKA ŚWIĄTYNIA ===================")
    if input(f"{C_BIAŁY}Uleczyć rany i odzyskać siły za 20 złota? (tak/nie): {C_RESET}").lower() == "tak" and gold >= 20:
        gold -= 20
        hp = 100
        pisz(f"{C_ZIELONY}Boska energia przepływa przez Twoje ciało. Zostałeś w pełni uleczony!{C_RESET}")
        zapisz_do_logu("Pełne leczenie w Świątyni za 20g.")

def magiczny_portal():
    global posX, posY
    print(f"\n{C_FIOLET}=================== ANOMALIA: PORTAL MAGICZNY ===================")
    pisz("Portal wciąga Cię kosmiczną siłą i gwałtownie zniekształca czasoprzestrzeń...")
    time.sleep(1.0)
    posX, posY = random.randint(-90, 90), random.randint(-90, 90)
    if -2 <= posX <= 2 and -2 <= posY <= 2: posX, posY = 15, 15
    pisz(f"{C_FIOLET}Wyrzuciło Cię w nieznanym zakątku świata: [{posX}, {posY}]!{C_RESET}")
    zapisz_do_logu(f"Użycie portalu. Losowa teleportacja na pozycję [{posX}, {posY}].")

def gdzie_spawn(oS):
    try:
        wartość = int(input(f"{C_BIAŁY}W osi {oS} zacznę (od -12 do 12, bez -2 do 2): {C_RESET}"))
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

        print(f"\n{C_ZŁOTO}=================== [TURA / KROKI W GRZE: {krok_tury}] ===================")
        print(f"{C_CYAN} OBECNY STAN ZASOBÓW:")
        print(f" -> Pozycja: [{posX}, {posY}]")
        print(f" -> Punkty Życia (HP): {hp}")
        print(f" -> Punkty Many: {mana}")
        print(f" -> Energia życiowa: {energia}")
        print(f" -> Posiadane Złoto: {gold} / 1000")
        print(f" -> Siła Ataku: {atak}")
        print(f" -> Ekwipunek: {ekwipunek}")
        print(f"{C_ZŁOTO}========================================================={C_RESET}")

        pisz(f"{C_BIAŁY}Gdzie nakazujesz podróżować? (Siatka mapy: -100 do 100){C_RESET}")
        try:
            cel_x = int(input(f"{C_SZARY}Cel X: {C_RESET}"))
            cel_y = int(input(f"{C_SZARY}Cel Y: {C_RESET}"))
            podrozuj(cel_x, cel_y)
        except ValueError: 
            print(f"{C_CZERWONY}Błąd! Podaj poprawne współrzędne liczbowe.{C_RESET}")

if __name__ == "__main__":
    main()