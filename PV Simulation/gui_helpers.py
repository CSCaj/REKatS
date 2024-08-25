import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from tkinter import ttk
import constants as c  # Importieren Sie die constants.py Datei


# Globale Variablen zur Speicherung der Werte
anzahl_vars = {}
belegung_vars = {}
zelttypen = ["SG20", "SG30", "SG40", "SG50"]
belegungen = ['Dach Ost', 'Dach West', 'Seite Ost', 'Seite West']

def create_tabs(root, entries, default_values, anzahl_vars, belegung_vars):
    tab_control = ttk.Notebook(root)
    # Stilinstanz erstellen
    style = ttk.Style()
    # Stil für Reiter anpassen
    style.configure('TNotebook.Tab', font=('Arial', 12, 
                                        #    'bold'
                                           ), 
                                           padding=3)
    
    # Tab für allgemeine Einstellungen
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Allgemein')
    create_input_frame(tab1, ['Breitengrad', 'Laengengrad', 'Hoehe', 'Anstellwinkel', 'azimuth', 'startzeit', 'endzeit', 'schrittweite'], entries, default_values, 20)

    # Tab für Modulparameter
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Modulparameter')
    create_input_frame(tab2, ['pdc0', 'gamma_pdc', 'a_ref', 'Il_ref', 'I0_ref', 'Rs_ref', 'Rsh_ref', 'Adjust', 'Technology'], entries, default_values, 20)

    # Tab für Wechselrichterparameter
    tab3 = ttk.Frame(tab_control)
    tab_control.add(tab3, text='Wechselrichterparameter')
    create_input_frame(tab3, ['pdc0_inv', 'eta_inv_nom', 'eta_inv_ref'], entries, default_values)


    # Tab für Zeltbelegung
    tab4 = create_zeltbelegung_tab(tab_control, anzahl_vars, belegung_vars)

    # Tab für klein Winenergieanlage
    tab5 = ttk.Frame(tab_control)
    tab_control.add(tab5, text='klein Winenergieanlage') 
    create_input_frame(tab5, ['Anzahl WEA', 'P_n', 'Narbenhoehe', 'v_min', 'v_n', 'v_max'], entries, default_values)
    # create_input_frame(tab5, ['v_min', 'v_n', 'v_max'], entries, default_values)

    # Tab für Batteriespeicher
    tab6 = ttk.Frame(tab_control)
    tab_control.add(tab6, text='Batteriespeicher')
    create_input_frame(tab6, ['Batteriekapazitaet', 'Ladeeffizienz', 'Entladeeffizienz', 'Max Ladeleistung', 'Max Entladeleistung', 'Anfangsenergie', 'Min Ladezustand', 'Max Ladezustand'], entries, default_values)
    
    # Tab für Elektrolyse
    tab7 = ttk.Frame(tab_control)
    tab_control.add(tab7, text='Elektrolyse')
    create_input_frame(tab7, ['Anzahl EL', 'Elektrische Leistung', 'Wasserverbrauch'], entries, default_values)

    # Tab für Brennstoffzelle
    tab8 = ttk.Frame(tab_control)
    tab_control.add(tab8, text='Brennstoffzelle')
    
    # Tab für Wasserstoffspeicher
    tab9 = ttk.Frame(tab_control)
    tab_control.add(tab9, text='Wasserstoffspeicher')

    # Tab für Batteriespeicher
    tab10 = ttk.Frame(tab_control)
    tab_control.add(tab10, text='etc.')

    tab_control.pack(expand=1, fill='both')
    return tab_control



def create_zeltbelegung_tab(tab_control, anzahl_vars, belegung_vars, font_size=12):
    tab4 = ttk.Frame(tab_control)
    tab_control.add(tab4, text='Zeltbelegung')
    font = ("Arial", font_size)
    style = ttk.Style()
    style.configure('TLabel', font=("Arial", font_size))
    style.configure('TCheckbutton', font=("Arial", font_size))

    for zelt in zelttypen:
        frame = ttk.LabelFrame(tab4, text=zelt)
        frame.pack(fill='x', padx=10, pady=10)
        
        anzahl = tk.IntVar(value=getattr(c, f"{zelt}_ANZAHL", 0))
        anzahl_vars[zelt] = anzahl  # Speichern der IntVar für späteren Zugriff
        anzahl_label = ttk.Label(frame, text="Anzahl:", font=font)
        anzahl_label.pack(side='left')
        anzahl_entry = ttk.Entry(frame, textvariable=anzahl, width=5, font=font)
        anzahl_entry.pack(side='left', padx=10, pady=5)
        
        belegung_vars[zelt] = {}
        standard_belegungen = getattr(c, f"{zelt}_BELEGUNGEN", {})
        for belegung in belegungen:
            var = tk.BooleanVar(value=standard_belegungen.get(belegung, False))  # Standardwert für Checkboxen
            belegung_vars[zelt][belegung] = var  # Speichern der BooleanVar für späteren Zugriff
            chk = ttk.Checkbutton(frame, text=belegung, variable=var, style='TCheckbutton')
            chk.pack(side='left', padx=10, pady=5)
    
    return tab4

def create_input_frame(frame, keys, entries, default_values,entry_width=10, font_size=12):
    frame = tk.Frame(frame, padx=10, pady=10)
    frame.pack(padx=10, pady=10)
    font = ("Arial", font_size)

    entry_dict = {}
    row = 0
    for key in keys:
        label = tk.Label(frame, text=f"{key.capitalize()}:", font=font)
        label.grid(row=row, column=0, sticky=tk.E)
        entry = tk.Entry(frame, justify='right', width=entry_width, font=font)
        entry.grid(row=row, column=1)
        entry.insert(0, default_values[key]['value'])
        entry_dict[key] = entry
        
        unit_label = tk.Label(frame, text=default_values[key].get('unit', ''), font=font)
        unit_label.grid(row=row, column=2, sticky=tk.W)
        
        row += 1

    entries.append(entry_dict)

# def create_input_frame(frame, keys, entries, default_values):
#     frame = tk.Frame(frame, padx=10, pady=10)
#     frame.pack(padx=10, pady=10)

#     entry_dict = {}
#     row = 0
#     for key in keys:
#         label = tk.Label(frame, text=f"{key.capitalize()}:")
#         label.grid(row=row, column=0, sticky=tk.W)
#         entry = tk.Entry(frame)
#         entry.grid(row=row, column=1)
#         entry.insert(0, default_values[key])
#         entry_dict[key] = entry
#         row += 1

#     entries.append(entry_dict)

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
