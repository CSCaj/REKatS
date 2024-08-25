import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

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
