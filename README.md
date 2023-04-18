# Zadanie

Tento projekt si kladie za ciel implementovať interpret jazyka IPPcode23, ktorý umožní preklad a následné vykonávanie programov napísaných v jazyku IPPcode23.

# Stručný popis riešenia

Riešením projektu je implementácia interpretu v jazyku Python3.10, ktorý zo vstupu definovaného argumentom príkazového riadka načíta XML reprezentáciu programu jazyka IPPcode23. Interpret využíva knižnicu `ElementTree` na načítanie, kontrolu a prístup k jednotlivým prvkom ako sú inštrukcie alebo argumenty.

# Architektúra programu

Základ programu tvorí trieda `Interpret` ktorej metódy predstavujú jednotlivé časti programu. Okrem metód pre spúšťanie jednotlivých častí interpretácie obsahuje aj metódu `main()`, ktorá tvorí hlavné telo programu.
## Implementovaný interpret pozostáva z 3 hlavných častí:

### 1. Spracovanie argumentov príkazového riadka

Pre spracovanie argumentov príkazového riadka bola použitá knižnica `argparse` a samostatná trieda `Argument_parser`. Metódy tejto triedy s použitím fukncií knižnice `argparse` zabezpečuje korektné načítanie a spracovanie argumentov príkazového riadka. Metódy triedy `Argument_parser` rovnako umožňujú predávanie spracovaných dát pre ďalšie použitie v programe.

### 2. Kontrola, parsovanie xml reprezentácie a načítanie inštrukcií

Po úspešnom spracovaní argumentov nasleduje načítanie xml reprezentácie a spracovanie pomocou volania metódy `parse_xml()`. Kontrola prebieha volaním metódy `check_xml()` ktorá zabezpečuje aj statické sémantické kontroly. V prípade úspešného načítania a kontroly je volaná metóda `load_instructions()`. Jednotlivé inštrukcie sú načítané do riedkeho pola na indexy určené ich poradím. Riedke pole je využité z dôvodu podpory načítania nezoradených inštrukcii. 

## 3. Interpretácia načítaných inštrukcií
Základom interpretačnej časti programu je trieda `Execute`. Pri vytváraní inštancie triedy `Execute` jej je predané pole `instruction_list`. Následne pomocou while cyklu prebieha iterácia cez jednotlivé inštrukcie a na základe operačného kódu je volaná príslušná metóda, ktorá vykoná samotnú interpretáciu. Metódy pre interpretáciu jednotlivých inštrukcií zabezpečujú dynamickú sémantickú kontrolu argumentov a vykonanie samotnej funkcionality danej inštrukcie definovanej zadaním.

# UML diagram tried:

