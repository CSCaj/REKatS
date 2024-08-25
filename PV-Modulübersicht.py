import tkinter as tk
from tkinter import ttk
import pvlib
import numpy as np

# Daten aus der Sandia-Moduldatenbank laden
sandia_modules = pvlib.pvsystem.retrieve_sam('SandiaMod')

# GUI erstellen
class ModuleDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sandia Moduldatenbank")
        
        self.create_widgets()
        
        # Daten für die Anzeige
        self.displayed_modules = list(sandia_modules.keys())  # Alle Module zu Beginn anzeigen
        
        # Einfügen der Daten in die Treeview
        self.update_displayed_modules()
        
        # Doppelklick-Event für Treeview-Einträge
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # Event für das Resize des Hauptfensters
        self.root.bind("<Configure>", self.on_resize)

    def create_widgets(self):
        # Suchfeld
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_displayed_modules)
        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var)
        self.search_entry.pack(padx=10, pady=10, fill=tk.X)

        # Treeview für die Anzeige der Module
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("Vintage", "Area", "Material", "Cells_in_Series",
                                "Parallel_Strings", "Isco", "Voco", "Impo", "Vmpo")
        
        # Festlegen der Spaltenüberschriften
        self.tree.heading("#0", text="Modul")
        self.tree.column("#0", width=150)
        
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Packen der Treeview
        self.tree.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Schließen-Button
        self.close_button = ttk.Button(self.root, text="Schließen", command=self.root.quit)
        self.close_button.pack(pady=10)

    def update_displayed_modules(self, *args):
        # Funktion zum Aktualisieren der angezeigten Module basierend auf der Sucheingabe
        search_text = self.search_var.get().lower()  # Suchtext ohne Groß-/Kleinschreibung

        # Filtern der Module
        self.displayed_modules = [module for module in sandia_modules
                                  if search_text in module.lower()]

        # Löschen aller bestehenden Einträge in der Treeview
        self.tree.delete(*self.tree.get_children())

        # Einfügen der gefilterten Module in die Treeview
        for module in self.displayed_modules:
            data = sandia_modules[module]
            self.tree.insert("", "end", text=module, values=(
                data['Vintage'], data['Area'], data['Material'],
                data['Cells_in_Series'], data['Parallel_Strings'],
                data['Isco'], data['Voco'], data['Impo'], data['Vmpo']
            ))

    def on_double_click(self, event):
        # Funktion, die aufgerufen wird, wenn ein Eintrag in der Treeview doppelt geklickt wird
        item = self.tree.selection()[0]  # Auswahl des Eintrags
        module_name = self.tree.item(item, "text")  # Name des Moduls aus dem Textattribut des Eintrags

        # Neues Fenster für die Detailansicht des Moduls
        module_details_window = tk.Toplevel(self.root)
        module_details_window.title(f"Details für Modul: {module_name}")

        # Treeview für die Detailansicht
        self.detail_tree = ttk.Treeview(module_details_window)
        self.detail_tree["columns"] = ("Wert")
        self.detail_tree.heading("#0", text="Parameter")
        self.detail_tree.column("#0", width=150)
        self.detail_tree.heading("Wert", text="Wert")
        self.detail_tree.column("Wert", width=200)

        # Daten für das ausgewählte Modul
        module_data = sandia_modules[module_name]

        # Einfügen der Daten in den Treeview
        for key, value in module_data.items():
            self.detail_tree.insert("", "end", text=key, values=(str(value)))

        # Packen und Konfigurieren des Treeviews für die Detailansicht
        self.detail_tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def on_resize(self, event):
        # Funktion, die aufgerufen wird, wenn das Hauptfenster neu dimensioniert wird
        # Treeview im Hauptfenster anpassen
        self.tree.pack_configure(fill=tk.BOTH, expand=True)
        
        # Treeview in Detailfenstern anpassen, falls geöffnet
        if hasattr(self, 'detail_tree'):
            self.detail_tree.pack_configure(fill=tk.BOTH, expand=True)

# Hauptprogramm
if __name__ == "__main__":
    root = tk.Tk()
    app = ModuleDatabaseApp(root)
    root.mainloop()
