import argparse
import json
import os
import random
import sys

mozliwe_pory_dnia = {'r': 'rano', 'w': 'wieczór'}
mozliwe_dni_tygodnia = {'pn': 'poniedziałek', 'wt': 'wtorek', 'sr': 'środa',
                        'cw': 'czwartek', 'pt': 'piątek', 'sb': 'sobota', 'nd': 'niedziela'}


def generate_random_data():
    model = random.choice(['A', 'B', 'C'])

    output_value = random.randint(0, 1000)

    computation_time = random.randint(0, 1000)

    # JSON
    if args.j:
        return {
            "Model": model,
            "Output value": output_value,
            "Time of computation": f"{computation_time}s"
        }

    # CSV
    else:
        return model, output_value, computation_time


def parser_init():
    parser = argparse.ArgumentParser(description="Skrypt do tworzenia i czytania plików.\n"
                                     "Domyślnie tworzymy pliki csv na podanej ścieżce.\n",
                                     epilog="Brak podania argumentów przy wywołaniu skryptu\n"
                                     "oznacza zakończenie działania programu bez wyniku\n")

    parser.add_argument(
      "--miesiace",
      nargs="*",  # dowolna ilość argumentów, zatem 0 lub więcej
      type=str,
      default=[],  # pusta lista przy braku specyfikacji miesięcy
      help="Lista miesięcy w formacie: miesiąc1 miesiąc2 ..."
    )

    parser.add_argument(
      "--zakres_dni_tygodnia",
      nargs="*",
      type=str,
      default=[],
      help="Lista zakresów dni tygodnia w formacie: zakres1 zakres2 ...\n"
           "Zakresy przedstawiamy jako dzień1-dzień2 np. pn-pt\n"
           "Ilość zakresów musi odpowiadać ilości podanych miesięcy"
    )

    parser.add_argument(
      "--pora_dnia",
      nargs="*",  # dowolna ilość argumentów, zatem 0 lub więcej
      type=str,
      default=['r'],  # wartość domyślna - rano
      help="Należy podać ciąg składający się z r - rano, w - wieczorem \n"
           "osobno dla każdego z przypadków il.miesięcy * il.dni.\n"
           "Brak specyfikacji oznacza przyjęcie wartości domyślnej - rano"
    )

    parser.add_argument(
        "-o",
        action='store_true',
        help="Aktywowanie flagi służącej do odczytywania plików"
    )

    parser.add_argument(
        "-j",
        action='store_true',
        help="Aktywowanie flagi służącej do odczytywania/tworzenia plików json\n"
    )

    return parser


def months_check(arguments):
    # Gdy miesiące nie zostały podane kończymy program
    if not arguments.miesiace:
        sys.exit(0)

    # Sprawdzenie czy podano poprawne nazwy miesięcy
    mozliwe_miesiace = {'styczeń', 'luty', 'marzec', 'kwiecień', 'maj',
                        'czerwiec', 'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień'}

    if not set(arguments.miesiace).issubset(mozliwe_miesiace):
        print("Błąd: Podano niepoprawną nazwę miesiąca.\n"
              "Nazwę podajemy z małej litery i z polskimi znakami: \n"
              "np. styczeń\n")
        sys.exit(1)

    # Sprawdzenie czy każdy miesiąc podano tylko raz
    if len(arguments.miesiace) != len(set(arguments.miesiace)):
        print("Błąd: Podano niepoprawną nazwę miesiąca.\n"
              "Nazwę danego miesiąca można podać tylko raz.\n")
        sys.exit(1)


def days_range_check(arguments):
    # Sprawdzenie czy ilość zakresów dni tygodnia odpowaida ilości miesięcy
    if len(arguments.miesiace) != len(arguments.zakres_dni_tygodnia):
        print("Błąd: Ilość zakresów dni tygodnia nie odpowiada ilości podanych miesięcy.\n "
              "Należy podać tyle zakresów ile zostało podanych miesięcy.\n")
        sys.exit(1)

    # Sprawdzenie czy podano poprawny zakres dni tygodnia
    for el in arguments.zakres_dni_tygodnia:
        wynik = el.split("-")
        for d in wynik:
            if d not in mozliwe_dni_tygodnia:
                print("Błąd: Podano niepoprawny format zakresu tygodnia\n"
                      "Dostępne dni to: pn, wt, sr, cw, pt, sb, nd\n"
                      "Dni w zakresie rozdzielamy znakiem -\n"
                      "np. pn-pt")
                sys.exit(1)

    # Zamiana zakresu na listy dni tygodnia
    # Definiujemy dostępne dni tygodnia
    mozliwe_dni = list(mozliwe_dni_tygodnia.keys())

    for dzien in arguments.zakres_dni_tygodnia:
        # Sprawdzamy, czy dany element jest zakresem
        if '-' in dzien:
            start, end = dzien.split('-')
            start_index = mozliwe_dni.index(start)
            end_index = mozliwe_dni.index(end)

            # Sprawdzamy kierunek zakresu i tworzymy odpowiednią listę dni
            if start_index <= end_index:
                # Zakres w normalnym kierunku
                zakres = mozliwe_dni[start_index:end_index + 1]
            else:
                # Zakres odwrotny
                zakres = mozliwe_dni[start_index:] + mozliwe_dni[:end_index + 1]

            # Dodajemy listę zakresu do wyniku
            arguments.zakres_dni_tygodnia[arguments.zakres_dni_tygodnia.index(dzien)] = zakres

        else:
            arguments.zakres_dni_tygodnia[arguments.zakres_dni_tygodnia.index(dzien)] = [dzien]


def daytime_check(arguments):
    # Sprawdzenie czy ilosc pór dnia jest poprawna
    ilosc_dni = 0
    for i in range(len(arguments.miesiace)):
        ilosc_dni += len(arguments.zakres_dni_tygodnia[i])

    if len(arguments.pora_dnia) > ilosc_dni:
        print("Błąd: Podano niepoprawną ilość pór dnia. \n"
              "Na każdy podany dzień w każdym miesiącu przypada jedna pora dnia\n")
        sys.exit(1)

    # Sprawdzenie czy poprawnie podano wartości dla pory dnia
    if not set(arguments.pora_dnia).issubset(mozliwe_pory_dnia):
        print("Błąd: Możliwe pory dnia to: r, w.\n"
              "Podano nieoprawną porę dnia.\n")
        sys.exit(1)

    # Uzupełnienie listy pora_dnia wartościami domyślnymi
    if len(arguments.pora_dnia) < ilosc_dni:
        while len(arguments.pora_dnia) < ilosc_dni:
            arguments.pora_dnia.append('r')


def args_check(arguments):
    # Sprawdzenie poprawności podanych parametrów
    months_check(arguments)
    days_range_check(arguments)
    daytime_check(arguments)


def write_to_file(sciezka_do_pliku):
    write_file = False

    if os.path.isfile(sciezka_do_pliku):
        print(f"Podany plik {sciezka_do_pliku} istnieje.\n"
              "Jeśli chcesz go nadpisać wpisz: y\n"
              "Jeśli nie, wciśnij dowolny przycisk.\n")
        if not input() == 'y':
            pass
        else:
            write_file = True
    else:
        write_file = True

    if write_file:
        with open(sciezka_do_pliku, 'w') as plik:
            # Piszemy do pliku:
            # JSON
            if args.j:
                data = {
                    "Header": ["Model", "Output value", "Time of computation"],
                    "Data": generate_random_data()
                }
                json.dump(data, plik, indent=4)
            # CSV
            else:
                plik.write("Model; Output value; Time of computation;\n")
                model, output_value, computation_time = generate_random_data()
                plik.write(f"{model}; {output_value}; {computation_time}s;\n")


def read_from_file(sciezka_do_pliku):
    if os.path.isfile(sciezka_do_pliku):
        with open(sciezka_do_pliku, 'r') as plik:
            # Odczytujemy informacje z pliku:
            pass
    else:
        print(f"Podany plik {sciezka_do_pliku} nie istnieje.\n")


def read_write_files():
    # Tworzenie struktury katalogu i odczytanie/tworzenie plików
    # Katalog główny
    sciezka_glowna = os.path.join(os.getcwd(), 'SkryptPython')

    # Tworzenie katalogu głównego i inicjalizacja iteratora dla pory dnia
    j = 0
    # Iteracja przez miesiące
    for i, miesiac in enumerate(args.miesiace):
        # Tworzymy katalog dla miesiąca
        sciezka_miesiaca = os.path.join(sciezka_glowna, miesiac.capitalize())

        # Iteracja przez dni tygodnia i pory dnia
        dni_tygodnia = args.zakres_dni_tygodnia[i]

        for dzien in dni_tygodnia:
            # Tworzymy katalog dla dnia
            sciezka_dnia = os.path.join(sciezka_miesiaca, mozliwe_dni_tygodnia[dzien])

            # Tworzymy katalog dla pory dnia
            pora = mozliwe_pory_dnia[args.pora_dnia[j]]
            j += 1

            sciezka_pory = os.path.join(sciezka_dnia, pora)
            os.makedirs(sciezka_pory, exist_ok=True)
            # Odczytujemy/Tworzymy plik

            # JSON
            if args.j:
                sciezka_do_pliku = os.path.join(sciezka_pory, 'Solutions.json')
            # CSV
            else:
                sciezka_do_pliku = os.path.join(sciezka_pory, 'Solutions.csv')

            # Odczytujemy
            if args.o:
                read_from_file(sciezka_do_pliku)

            # Tworzenie pliku
            else:
                write_to_file(sciezka_do_pliku)


args = parser_init().parse_args()
args_check(args)
read_write_files()