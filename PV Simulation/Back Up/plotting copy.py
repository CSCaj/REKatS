import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from sub_functions import save_results

def plot_results(root, erzeugte_energien, stromerzeugungen, dieselmenge, eingesparte_energie, berechnungszeiten, tabs_entries):
    ergebnis_win = tk.Toplevel(root)
    ergebnis_win.title("Ergebnis der Stromerzeugung")

    text = f"Berechnungszeit: {berechnungszeiten[0]:.2f} Sekunden\n\n"  # Nehmen wir die Berechnungszeit des ersten Arrays

    # Eingabeparameter anzeigen
    text += "Eingabeparameter:\n\n"
    for tab_entries in tabs_entries:
        for key, entry in tab_entries.items():
            text += f"{key.capitalize()}: {entry.get()}\n"
        text += "\n"
    
    # Summierte Erzeugung berechnen
    summierte_erzeugung = sum(erzeugte_energien)

    # Erzeugte Energie anzeigen
    text += f"Erzeugte Energie:\n"
    flaechen_bezeichnungen = ['Dach Ost', 'Dach West', 'Seite Ost', 'Seite West']
    for idx, erzeugte_energie in enumerate(erzeugte_energien):
        text += f"{flaechen_bezeichnungen[idx]}: {erzeugte_energie:.2f} kWh\n"
    text += f"\nSummierte Erzeugung: {summierte_erzeugung:.2f} kWh\n"

    text += f"\nEingesparter Diesel: {summierte_erzeugung:.2f} l\n"

    text += f"Eingesparte Dieselenergie: {eingesparte_energie:.2f} kWh\n"

    label = tk.Label(ergebnis_win, text=text, justify='left')
    label.pack(padx=10, pady=10)

    # Plot für alle ausgewählten Flächen und summierte Erzeugung
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot für jede Fläche
    for idx, stromerzeugung in enumerate(stromerzeugungen):
        ax.plot(stromerzeugung.index, stromerzeugung, label=['Dach Ost', 'Dach West', 'Seite Ost', 'Seite West'][idx])

    # Summierte Erzeugung
    summierte_erzeugung = sum(stromerzeugungen)
    ax.plot(summierte_erzeugung.index, summierte_erzeugung, linestyle='--', color='black', label='Summierte Erzeugung')

    ax.set_xlabel('Zeit')
    ax.set_ylabel('Leistung (W)')
    ax.set_title('Stromerzeugung')
    ax.legend()
    ax.grid(True)

    # Canvas für Tkinter erstellen und einfügen
    canvas = FigureCanvasTkAgg(fig, master=ergebnis_win)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Speicher-Button hinzufügen
    save_button = tk.Button(ergebnis_win, text="Speichern", command=lambda: save_results(text, stromerzeugungen, summierte_erzeugung, fig))
    save_button.pack(pady=10)
