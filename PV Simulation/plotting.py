import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk
from sub_functions import save_results
from functions_wind import plot_wind_results
import constants as c 
import constants_wind as cw

def plot_results(root, erzeugte_energien, stromerzeugungen, df_wind, wind_energy_output_single, wind_energy_output_total, Anzahl, dieselmenge, eingesparte_energie, berechnungszeiten, tabs_entries, selected_areas, df_results, fullscreen=False):
    ergebnis_win = tk.Toplevel(root)
    ergebnis_win.title("Ergebnis der Stromerzeugung")
    if fullscreen:
        ergebnis_win.attributes('-fullscreen', True)
    else:
        ergebnis_win.geometry('1024x768')

    notebook = ttk.Notebook(ergebnis_win)
    notebook.pack(expand=1, fill='both')
    
    create_results_tab(notebook, erzeugte_energien, stromerzeugungen, dieselmenge, eingesparte_energie, berechnungszeiten, tabs_entries, selected_areas)
    create_wind_simulation_tab(notebook, df_wind, wind_energy_output_single, wind_energy_output_total, Anzahl)
    create_test_tab(notebook, df_results)
    create_misc_tab(notebook)


def create_scrollable_tab(notebook, title):
    frame = ttk.Frame(notebook)
    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Frame zum Canvas hinzufügen
    canvas_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=canvas_frame, anchor="nw")
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    notebook.add(frame, text=title)
    return canvas_frame

def append_text_widget(text_widget, title, data_dict):
    text_widget.insert(tk.END, f"{title}:\n")
    for key, value in data_dict.items():
        text_widget.insert(tk.END, f"{key}: {value}\n")
    text_widget.insert(tk.END, "\n")

def plot_stromerzeugung(ax, stromerzeugungen, selected_areas):
    summierte_stromerzeugung = None
    for idx, stromerzeugung in enumerate(stromerzeugungen):
        label = selected_areas[idx] if idx < len(selected_areas) else f"Unbekannte Fläche {idx}"
        ax.plot(stromerzeugung.index, stromerzeugung, label=label)
        
        if summierte_stromerzeugung is None:
            summierte_stromerzeugung = stromerzeugung.copy()
        else:
            summierte_stromerzeugung += stromerzeugung

    if summierte_stromerzeugung is not None:
        ax.plot(summierte_stromerzeugung.index, summierte_stromerzeugung, linestyle='--', color='black', label='Summierte Erzeugung')
    ax.set_xlabel('Zeit')
    ax.set_ylabel('Leistung (W)')
    ax.set_title('Stromerzeugung')
    ax.legend()
    

def create_results_tab(notebook, erzeugte_energien, stromerzeugungen, dieselmenge, eingesparte_energie, berechnungszeiten, tabs_entries, selected_areas):
    ergebnis_frame = create_scrollable_tab(notebook, "Ergebnisse und Plot")
    
    text_widget = tk.Text(ergebnis_frame, wrap='word', height=15)
    text_widget.pack(padx=10, pady=10, fill='both', expand=True)
    
    text = f"Berechnungszeit: {berechnungszeiten[0]:.2f} Sekunden\n\nEingabeparameter:\n\n"
    for tab_entries in tabs_entries:
        data_dict = {key.capitalize(): entry.get() for key, entry in tab_entries.items()}
        append_text_widget(text_widget, "Eingabeparameter", data_dict)
    
    summierte_erzeugung = sum(erzeugte_energien)
    erzeugte_energie_text = "\n".join(
        f"{selected_areas[idx]}: {energie:.2f} kWh" if idx < len(selected_areas)
        else f"Unbekannte Fläche {idx}: {energie:.2f} kWh"
        for idx, energie in enumerate(erzeugte_energien)
    )
    text += f"Erzeugte Energie:\n{erzeugte_energie_text}\nSummierte Erzeugung: {summierte_erzeugung:.2f} kWh\n"
    text += f"Eingesparter Diesel: {dieselmenge:.2f} l\nEingesparte Dieselenergie: {eingesparte_energie:.2f} kWh\n"

    text_widget.insert(tk.END, text)
    text_widget.config(state=tk.DISABLED)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_stromerzeugung(ax, stromerzeugungen, selected_areas)
    
    canvas_plot = FigureCanvasTkAgg(fig, master=ergebnis_frame)
    canvas_plot.draw()
    canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    
    toolbar = NavigationToolbar2Tk(canvas_plot, ergebnis_frame)
    toolbar.update()
    canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    
    save_button = tk.Button(ergebnis_frame, text="Speichern", command=lambda: save_results(text, stromerzeugungen, fig))
    save_button.pack(pady=10)

def create_wind_simulation_tab(notebook, df_wind, wind_energy_output_single, wind_energy_output_total, Anzahl):
    wind_frame = create_scrollable_tab(notebook, "Windsimulation")
    plot_wind_results(wind_frame, df_wind, cw.CUT_IN_SPEED, cw.RATED_SPEED, cw.CUT_OUT_SPEED, wind_energy_output_single, wind_energy_output_total, Anzahl)

def create_test_tab(notebook, df_results):
    test_frame = create_scrollable_tab(notebook, "Test")
    plot_from_dataframe(test_frame, df_results, ['Gesamtlast','Batterie Ladung', 'Erzeugung EE', 'Netto Last'], figsize=(10, 8))
    create_output_label(test_frame, "Dies ist ein Ausgabe-Label \nmit etwas Text")

def create_misc_tab(notebook):
    sonstiges_frame = create_scrollable_tab(notebook, "Sonstiges")
    sonstiges_text = (
        f"SG20 Parameter:\nDach MPS: {c.DACH_SG20_MPS}\nDach Strings: {c.DACH_SG20_STRINGS}\n"
        f"Seiten MPS: {c.SEITEN_SG20_MPS}\nSeiten Strings: {c.SEITEN_SG20_STRINGS}\n"
        f"Länge: {c.SG20_LAENGE} m\nBreite: {c.SG20_BREITE} m\nGewicht: {c.SG20_GEWICHT} kg\n"
        f"Feldbetten: {c.SG20_FELDBETTEN}\n\n"
        f"SG30 Parameter:\nDach MPS: {c.DACH_SG30_MPS}\nDach Strings: {c.DACH_SG30_STRINGS}\n"
        f"Seiten MPS: {c.SEITEN_SG30_MPS}\nSeiten Strings: {c.SEITEN_SG30_STRINGS}\n"
        f"Länge: {c.SG30_LAENGE} m\nBreite: {c.SG30_BREITE} m\nGewicht: {c.SG30_GEWICHT} kg\n"
        f"Feldbetten: {c.SG30_FELDBETTEN}\nGarnituren: {c.SG30_GARNITUREN}\nPlätze: {c.SG30_PLAETZE}\n\n"
        f"SG40 Parameter:\nDach MPS: {c.DACH_SG40_MPS}\nDach Strings: {c.DACH_SG40_STRINGS}\n"
        f"Seiten MPS: {c.SEITEN_SG40_MPS}\nSeiten Strings: {c.SEITEN_SG40_STRINGS}\n"
        f"Länge: {c.SG40_LAENGE} m\nBreite: {c.SG40_BREITE} m\nGewicht: {c.SG40_GEWICHT} kg\n"
        f"Feldbetten: {c.SG40_FELDBETTEN}\n\n"
        f"SG50 Parameter:\nDach MPS: {c.DACH_SG50_MPS}\nDach Strings: {c.DACH_SG50_STRINGS}\n"
        f"Seiten MPS: {c.SEITEN_SG50_MPS}\nSeiten Strings: {c.SEITEN_SG50_STRINGS}\n"
        f"Länge: {c.SG50_LAENGE} m\nBreite: {c.SG50_BREITE} m\nGewicht: {c.SG50_GEWICHT} kg\n"
        f"Feldbetten: {c.SG50_FELDBETTEN}\n"
    )
    sonstiges_text_widget = tk.Text(sonstiges_frame, wrap='word', height=15)
    sonstiges_text_widget.pack(padx=10, pady=10, fill='both', expand=True)
    sonstiges_text_widget.insert(tk.END, sonstiges_text)
    sonstiges_text_widget.config(state=tk.DISABLED)



# def plot_results(root, erzeugte_energien, stromerzeugungen, 
#                  df_wind, wind_energy_output_single, wind_energy_output_total, Anzahl, 
#                  dieselmenge, eingesparte_energie, berechnungszeiten, 
#                  tabs_entries, selected_areas, df_results, fullscreen=False):
#     # Neues Fenster erstellen
#     ergebnis_win = tk.Toplevel(root)
#     ergebnis_win.title("Ergebnis der Stromerzeugung")

#     # Fenstergröße einstellen
#     if fullscreen:
#         ergebnis_win.attributes('-fullscreen', True)
#     else:
#         ergebnis_win.geometry('1024x768')

#     # Notebook (Tabs) hinzufügen
#     notebook = ttk.Notebook(ergebnis_win)
#     notebook.pack(expand=1, fill='both')  # Nur horizontal expandieren, damit es oben fixiert bleibt
    
#     # Erstes Tab - Ergebnisse und Plot
#     ergebnis_frame = create_scrollable_tab(notebook, "Ergebnisse und Plot")

#     # Scrollbares Text-Widget für lange Texte
#     text_widget = tk.Text(ergebnis_frame, wrap='word', height=15)
#     text_widget.pack(padx=10, pady=10, fill='both', expand=True)

#     text = f"Berechnungszeit: {berechnungszeiten[0]:.2f} Sekunden\n\n"  # Nehmen wir die Berechnungszeit des ersten Arrays

#     # Eingabeparameter anzeigen
#     text += "Eingabeparameter:\n\n"
#     for tab_entries in tabs_entries:
#         for key, entry in tab_entries.items():
#             text += f"{key.capitalize()}: {entry.get()}\n"
#         text += "\n"

#     # Summierte Erzeugung berechnen
#     summierte_erzeugung = sum(erzeugte_energien)

#     # Erzeugte Energie anzeigen
#     text += "Erzeugte Energie:\n"
#     for idx, erzeugte_energie in enumerate(erzeugte_energien):
#         if idx < len(selected_areas):
#             text += f"{selected_areas[idx]}: {erzeugte_energie:.2f} kWh\n"
#         else:
#             text += f"Unbekannte Fläche {idx}: {erzeugte_energie:.2f} kWh\n"
#     text += f"\nSummierte Erzeugung: {summierte_erzeugung:.2f} kWh\n"

#     text += f"\nEingesparter Diesel: {dieselmenge:.2f} l\n"
#     text += f"Eingesparte Dieselenergie: {eingesparte_energie:.2f} kWh\n"

#     text_widget.insert(tk.END, text)
#     text_widget.config(state=tk.DISABLED)

#     # Plot für alle ausgewählten Flächen und summierte Erzeugung
#     fig, ax = plt.subplots(figsize=(8, 5))

#     # Plot für jede Fläche
#     summierte_stromerzeugung = None
#     for idx, stromerzeugung in enumerate(stromerzeugungen):
#         if idx < len(selected_areas):
#             ax.plot(stromerzeugung.index, stromerzeugung, label=selected_areas[idx])
#             if summierte_stromerzeugung is None:
#                 summierte_stromerzeugung = stromerzeugung.copy()
#             else:
#                 summierte_stromerzeugung += stromerzeugung
#         else:
#             ax.plot(stromerzeugung.index, stromerzeugung, label=f"Unbekannte Fläche {idx}")
#             if summierte_stromerzeugung is None:
#                 summierte_stromerzeugung = stromerzeugung.copy()
#             else:
#                 summierte_stromerzeugung += stromerzeugung

#     # Summierte Erzeugung plotten
#     if summierte_stromerzeugung is not None:
#         ax.plot(summierte_stromerzeugung.index, summierte_stromerzeugung, linestyle='--', color='black', label='Summierte Erzeugung')

#     ax.set_xlabel('Zeit')
#     ax.set_ylabel('Leistung (W)')
#     ax.set_title('Stromerzeugung')
#     ax.legend()
#     ax.grid(True)

#     # Canvas für Tkinter erstellen und einfügen
#     canvas_plot = FigureCanvasTkAgg(fig, master=ergebnis_frame)
#     canvas_plot.draw()
#     canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=1)

#     # Toolbar für interaktive Funktionen hinzufügen
#     toolbar = NavigationToolbar2Tk(canvas_plot, ergebnis_frame)
#     toolbar.update()
#     canvas_plot.get_tk_widget().pack(fill=tk.BOTH, expand=1)

#     # Speicher-Button hinzufügen
#     save_button = tk.Button(ergebnis_frame, text="Speichern", command=lambda: save_results(text, stromerzeugungen, summierte_stromerzeugung, fig))
#     save_button.pack(pady=10)

#     #################################################
#     # 2. Tab - Windsimulation
#     wind_frame = create_scrollable_tab(notebook, "Windsimulation")
    
#     # Hier wird die Funktion aufgerufen, um die Diagramme zu erstellen
#     plot_wind_results(wind_frame, df_wind, cw.CUT_IN_SPEED, cw.RATED_SPEED, cw.CUT_OUT_SPEED, wind_energy_output_single, wind_energy_output_total, Anzahl)

#     #################################################
#     # 3. Tab - Sonstiges
#     test_frame = create_scrollable_tab(notebook, "Test")
#     plot_from_dataframe(test_frame, df_results, ['Batterie Ladung'], figsize=(10, 8))
#     create_output_label(test_frame, "Dies ist ein Ausgabe-Label \nmit etwas Text")

#     #################################################
#     # 4. Tab - Sonstiges
#     sonstiges_frame = create_scrollable_tab(notebook, "Sonstiges")

#     sonstiges_text = (
#         f"SG20 Parameter:\n"
#         f"Dach MPS: {c.DACH_SG20_MPS}\n"
#         f"Dach Strings: {c.DACH_SG20_STRINGS}\n"
#         f"Seiten MPS: {c.SEITEN_SG20_MPS}\n"
#         f"Seiten Strings: {c.SEITEN_SG20_STRINGS}\n"
#         f"Länge: {c.SG20_LAENGE} m\n"
#         f"Breite: {c.SG20_BREITE} m\n"
#         f"Gewicht: {c.SG20_GEWICHT} kg\n"
#         f"Feldbetten: {c.SG20_FELDBETTEN}\n\n"
#         f"SG30 Parameter:\n"
#         f"Dach MPS: {c.DACH_SG30_MPS}\n"
#         f"Dach Strings: {c.DACH_SG30_STRINGS}\n"
#         f"Seiten MPS: {c.SEITEN_SG30_MPS}\n"
#         f"Seiten Strings: {c.SEITEN_SG30_STRINGS}\n"
#         f"Länge: {c.SG30_LAENGE} m\n"
#         f"Breite: {c.SG30_BREITE} m\n"
#         f"Gewicht: {c.SG30_GEWICHT} kg\n"
#         f"Feldbetten: {c.SG30_FELDBETTEN}\n"
#         f"Garnituren: {c.SG30_GARNITUREN}\n"
#         f"Plätze: {c.SG30_PLAETZE}\n\n"
#         f"SG40 Parameter:\n"
#         f"Dach MPS: {c.DACH_SG40_MPS}\n"
#         f"Dach Strings: {c.DACH_SG40_STRINGS}\n"
#         f"Seiten MPS: {c.SEITEN_SG40_MPS}\n"
#         f"Seiten Strings: {c.SEITEN_SG40_STRINGS}\n"
#         f"Länge: {c.SG40_LAENGE} m\n"
#         f"Breite: {c.SG40_BREITE} m\n"
#         f"Gewicht: {c.SG40_GEWICHT} kg\n"
#         f"Feldbetten: {c.SG40_FELDBETTEN}\n\n"
#         f"SG50 Parameter:\n"
#         f"Dach MPS: {c.DACH_SG50_MPS}\n"
#         f"Dach Strings: {c.DACH_SG50_STRINGS}\n"
#         f"Seiten MPS: {c.SEITEN_SG50_MPS}\n"
#         f"Seiten Strings: {c.SEITEN_SG50_STRINGS}\n"
#         f"Länge: {c.SG50_LAENGE} m\n"
#         f"Breite: {c.SG50_BREITE} m\n"
#         f"Gewicht: {c.SG50_GEWICHT} kg\n"
#         f"Feldbetten: {c.SG50_FELDBETTEN}\n"
#     )

#     # Scrollbares Text-Label für lange Inhalte
#     sonstiges_text_widget = tk.Text(sonstiges_frame, wrap='word', height=15)
#     sonstiges_text_widget.pack(padx=10, pady=10, fill='both', expand=True)  # Anpassung hier
#     sonstiges_text_widget.insert(tk.END, sonstiges_text)
#     sonstiges_text_widget.config(state=tk.DISABLED)

#     # Grid layout configuration for resizing
#     test_frame.grid_rowconfigure(0, weight=1)
#     test_frame.grid_columnconfigure(0, weight=1)

def create_output_label(parent_frame, text):
    class OutputLabel(tk.Frame):
        def __init__(self, parent, text):
            super().__init__(parent)
            self.pack(fill=tk.BOTH, expand=1)

            # Label erstellen und in den Frame einfügen
            self.label = tk.Label(self, text=text, anchor="center", font=("Arial", 14))
            self.label.pack(pady=20)

    # OutputLabel in den übergebenen Frame einbetten
    OutputLabel(parent_frame, text).pack(fill=tk.BOTH, expand=1)

def plot_from_dataframe(parent_frame, df, columns_to_plot, figsize=(8, 6)):
    class PlotApp(tk.Frame):
        def __init__(self, parent, df, columns_to_plot, figsize):
            super().__init__(parent)
            self.grid(row=0, column=0, sticky='nsew')

            self.df = df
            self.columns_to_plot = columns_to_plot

            # Matplotlib-Figur und -Achsen erstellen mit spezifischer Größe
            self.fig, self.ax = plt.subplots(figsize=figsize)

            # Dictionary für Linienobjekte
            self.lines = {}

            # Kurven initial plotten
            for column in self.columns_to_plot:
                line, = self.ax.plot(self.df.index, self.df[column], label=column)
                self.lines[column] = line

            # Legende hinzufügen
            self.ax.legend()
            self.ax.grid(True)

            # Frame für das Diagramm erstellen und auf die gewünschte Größe setzen
            self.plot_frame = tk.Frame(self, width=figsize[0]*100, height=figsize[1]*100)
            self.plot_frame.grid(row=0, column=0, sticky='nsew')

            # Matplotlib-Figur in den Frame einbetten
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
            self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            # Kontrollkästchen für Kurven hinzufügen
            self.checkbox_frame = tk.Frame(self)
            self.checkbox_frame.grid(row=1, column=0, sticky='ew')

            self.variables = {}
            for column in self.columns_to_plot:
                var = tk.BooleanVar(value=True)
                checkbox = ttk.Checkbutton(self.checkbox_frame, text=column, variable=var, command=self.update_plot)
                checkbox.pack(side=tk.LEFT)
                self.variables[column] = var

            # Grid layout configuration for resizing
            self.grid_rowconfigure(0, weight=1)
            self.grid_columnconfigure(0, weight=1)

        def update_plot(self):
            # Kurven je nach Kontrollkästchen-Zustand ein-/ausblenden
            for column, line in self.lines.items():
                line.set_visible(self.variables[column].get())
            
            # Plot aktualisieren
            self.canvas.draw()

    # PlotApp in den übergebenen Frame einbetten
    PlotApp(parent_frame, df, columns_to_plot, figsize).grid(row=0, column=0, sticky='nsew')

# Funktion, um ein Tab mit einem scrollbaren Frame zu erstellen
def create_scrollable_tab(notebook, tab_name):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=tab_name)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack-Options für Canvas und Scrollbar anpassen
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scrollable_frame


