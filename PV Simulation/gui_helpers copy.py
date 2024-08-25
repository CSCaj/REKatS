import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
import constants as c  # Importieren Sie die constants.py Datei

def create_tabs(root, entries, default_values):
    tab_control = ttk.Notebook(root)
    
    # Tab für allgemeine Einstellungen
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Allgemein')
    create_input_frame(tab1, ['Breitengrad', 'Laengengrad', 'Hoehe', 'Anstellwinkel', 'azimuth', 'startzeit', 'endzeit', 'schrittweite'], entries, default_values)

    # Tab für Modulparameter
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Modulparameter')
    create_input_frame(tab2, ['pdc0', 'gamma_pdc', 'a_ref', 'Il_ref', 'I0_ref', 'Rs_ref', 'Rsh_ref', 'Adjust', 'Technology'], entries, default_values)

    # Tab für Wechselrichterparameter
    tab3 = ttk.Frame(tab_control)
    tab_control.add(tab3, text='Wechselrichterparameter')
    create_input_frame(tab3, ['pdc0_inv', 'eta_inv_nom', 'eta_inv_ref'], entries, default_values)


    # Tab für Zeltbelegung
    tab4 = ttk.Frame(tab_control)
    tab_control.add(tab4, text='Zeltbelegung')
    zelttypen = ["SG20", "SG30", "SG40", "SG50"]
    belegungen = ['Dach Ost', 'Dach West', 'Seite Ost', 'Seite West']
    anzahl_vars = {}
    belegung_vars = {}
    
    # Erstellen Sie für jeden Zelttyp eine Gruppe von Kontrollkästchen und ein Eingabefeld für die Anzahl
    for zelt in zelttypen:
        frame = ttk.LabelFrame(tab4, text=zelt)
        frame.pack(fill='x', padx=10, pady=10)
        
        # Korrektur: Der Standardwert wird hier korrekt gesetzt
        anzahl = tk.IntVar(value=getattr(c, f"{zelt}_ANZAHL", 0))
        anzahl_vars[zelt] = anzahl  # Speichern der IntVar für späteren Zugriff
        anzahl_label = ttk.Label(frame, text="Anzahl:")
        anzahl_label.pack(side='left')
        anzahl_entry = ttk.Entry(frame, textvariable=anzahl, width=5)
        anzahl_entry.pack(side='left', padx=10, pady=5)
        
        belegung_vars[zelt] = {}
        # Standardbelegungen aus constants.py laden
        standard_belegungen = getattr(c, f"{zelt}_BELEGUNGEN", {})
        for belegung in belegungen:
            var = tk.BooleanVar(value=standard_belegungen.get(belegung, False))  # Standardwert für Checkboxen
            belegung_vars[zelt][belegung] = var  # Speichern der BooleanVar für späteren Zugriff
            chk = ttk.Checkbutton(frame, text=belegung, variable=var)
            chk.pack(side='left', padx=10, pady=5)

    tab_control.pack(expand=1, fill='both')
    return tab_control


    # # Tab für Zeltbelegung
    # tab4 = ttk.Frame(tab_control)
    # tab_control.add(tab4, text='Zeltbelegung')
    # create_combobox_frame(tab4, ["SG 20", "SG 30", "SG 40", "SG 50"])
    # checkbox_vars = create_checkbox_frame(tab4, ['Dach Ost', 'Dach West', 'Seite Ost', 'Seite West'])
    # # Set default values for Dach Ost and Dach West
    # checkbox_vars[0].set(True)  # Dach Ost
    # checkbox_vars[1].set(True)  # Dach West

    # # Tab für klein Winenergieanlage
    # tab5 = ttk.Frame(tab_control)
    # tab_control.add(tab5, text='klein Winenergieanlage') 

    # # Tab für Elektrolyse
    # tab6 = ttk.Frame(tab_control)
    # tab_control.add(tab6, text='Elektrolyse')
    
    # tab_control.pack(expand=1, fill='both')


    # return checkbox_vars

def create_input_frame(frame, keys, entries, default_values):
    frame = tk.Frame(frame, padx=10, pady=10)
    frame.pack(padx=10, pady=10)

    entry_dict = {}
    row = 0
    for key in keys:
        label = tk.Label(frame, text=f"{key.capitalize()}:")
        label.grid(row=row, column=0, sticky=tk.W)
        entry = tk.Entry(frame)
        entry.grid(row=row, column=1)
        entry.insert(0, default_values[key])
        entry_dict[key] = entry
        row += 1

    entries.append(entry_dict)

def create_checkbox_frame(parent, options):
    frame = ttk.Frame(parent, padding=30)
    frame.pack(padx=50, pady=10, fill='both', expand=True)
    
    checkbox_vars = []
    for option in options:
        var = tk.BooleanVar()
        checkbox = ttk.Checkbutton(frame, text=option, variable=var)
        checkbox.pack(anchor='w', pady=5)
        checkbox_vars.append(var)

    return checkbox_vars

def create_combobox_frame(parent, values):
    frame = ttk.Frame(parent, padding=10)
    frame.pack(padx=10, pady=10, fill='both', expand=True)

    label = ttk.Label(frame, text="Zelttyp:")
    label.pack(pady=5)

    combo = ttk.Combobox(frame, values=values)
    combo.pack(pady=5)
    combo.bind("<<ComboboxSelected>>", on_select)

def on_select(event):
    selected_value = event.widget.get()
    print(f"Selected: {selected_value}")

def create_calculation_button(root, command):
    button_berechnen = tk.Button(root, text="Berechnen", command=command)
    button_berechnen.pack(pady=10)

def get_entries(entries):
    entry_values = {}
    for entry_dict in entries:
        for key, entry in entry_dict.items():
            entry_values[key] = entry.get()
    return entry_values

def plot_results(root, erzeugte_energie, stromerzeugung, berechnungszeit, tabs_entries):
    ergebnis_win = tk.Toplevel(root)
    ergebnis_win.title("Ergebnis der Stromerzeugung")

    text = f"Berechnungszeit: {berechnungszeit:.2f} Sekunden\n\n"

    # Eingabeparameter anzeigen
    text += "Eingabeparameter:\n\n"
    for tab_entries in tabs_entries:
        for key, entry in tab_entries.items():
            text += f"{key.capitalize()}: {entry.get()}\n"
        text += "\n"

    # Erzeugte Energie anzeigen
    text += f"Erzeugte Energie: {erzeugte_energie:.2f} kWh\n"

    label = tk.Label(ergebnis_win, text=text, justify='left')
    label.pack(padx=10, pady=10)

    # Plot der Stromerzeugung
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(stromerzeugung.index, stromerzeugung, label='Erzeugte Leistung (W)')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Leistung (W)')
    ax.set_title('Stromerzeugung')
    ax.legend()
    ax.grid(True)

    canvas = FigureCanvasTkAgg(fig, master=ergebnis_win)
    canvas.draw()
    canvas.get_tk_widget().pack()

