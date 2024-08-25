import constants_bat as cb
from tkinter import messagebox
from sub_functions import extract_bat_data

def calculation_bat(entries, df_results): 
    df_results = df_results 
    return df_results









# def load_control(entries, df_results):
#     params = extract_bat_data(entries)
#     battery_energy = params['Anfangsenergie']
#     charge_efficiency = params['Ladeeffizienz']
#     discharge_efficiency = params['Entladeeffizienz']
#     max_charge_rate = params['Max Ladeleistung']
#     max_discharge_rate = params['Max Entladeleistung']
#     min_battery_level = params['Min Ladezustand']
#     max_battery_level = params['Max Ladezustand']
#     # backup_generator_power = params.get('Backup Generator Leistung', 0)  # Falls ein Backup-Generator spezifiziert ist
    
#     # Erstellen einer neuen Spalte für den Ladezustand des Akkus
#     # df_results['Battery Energy'] = 0.0
#     # df_results['Generator Usage'] = 0.0
    
#     # Berechnungen für jede Zeile im DataFrame
#     for index, row in df_results.iterrows():
#         gesamtlast = row['Gesamtlast']
#         pv_erzeugung = row['PV Erzeugung']
#         wind_erzeugung = row['Wind Erzeugung']
        
#         # Erneuerbare Energieerzeugung
#         erneuerbare_energie = pv_erzeugung + wind_erzeugung
        
#         # Verfügbare Energie nach Deckung der Gesamtlast
#         verfügbare_energie = erneuerbare_energie - gesamtlast
        
#         # Falls verfügbare Energie positiv ist, entscheiden, ob sie zum Laden der Batterie verwendet wird
#         if verfügbare_energie > 0:
#             # Berechne die maximale Ladeleistung basierend auf der verfügbaren Energie und dem Ladeeffizienz
#             ladeleistung = min(max_charge_rate, verfügbare_energie * charge_efficiency)
            
#             # Falls die Batterie nicht voll ist, lade sie auf
#             if battery_energy < max_battery_level:
#                 battery_energy += ladeleistung
#                 if battery_energy > max_battery_level:
#                     battery_energy = max_battery_level
        
#         # Wenn die verfügbare Energie negativ ist, Batterie entladen oder Generator verwenden
#         if verfügbare_energie < 0:
#             benötigte_energie = -verfügbare_energie
#             discharge_amount = min(max_discharge_rate, battery_energy * discharge_efficiency)
#             if discharge_amount >= benötigte_energie:
#                 battery_energy -= benötigte_energie / discharge_efficiency
#             else:
#                 # Backup-Generator aktivieren
#                 generator_usage = benötigte_energie - discharge_amount
#                 # Hier könnte zusätzlicher Code für die Generatorsteuerung hinzugefügt werden
        
#         # Sicherstellen, dass der Batterie-Ladezustand im erlaubten Bereich bleibt
#         if battery_energy < min_battery_level:
#             battery_energy = min_battery_level
#         elif battery_energy > max_battery_level:
#             battery_energy = max_battery_level

#         # Speichern des Batteriestands in der neuen Spalte
#         df_results.at[index, 'Batterie Energie'] = battery_energy
    
#     return df_results



def load_control(entries, df_results):
    try:
        # Initialisieren der Batteriedaten
        params = extract_bat_data(entries)
        battery_energy = params['Anfangsenergie']

        # print(f"Initialisierte Batteriedaten: {params}")

        # Neue Spalten für das Managementsystem
        df_results['Batterie Ladung'] = 0.0
        df_results['Backup Generator'] = 0.0
        df_results['Batterie Energie'] = battery_energy
        df_results['Netto Last'] = df_results['Gesamtlast'] - (df_results['PV Erzeugung'] + df_results['Wind Erzeugung'])

        # Simulation des Batteriemanagements für jeden Zeitschritt
        for idx, row in df_results.iterrows():
            df_results.loc[idx], battery_energy = battery_management_system(entries, row, battery_energy)
        
        # print(df_results)
        return df_results

    except Exception as e:
        print(f"Fehler bei der Durchführung der Berechnung: {e}")
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten beim Ladecontroller: {e}")

# Funktion zur Simulation des Batteriemanagements
def battery_management_system(entries, row, battery_energy):
    net_load = row['Gesamtlast'] - (row['PV Erzeugung'] + row['Wind Erzeugung'])

    # Dynamische Parameter extrahieren
    params = extract_bat_data(entries)
    
    # print(f"Extrahierte Batteriedaten: {params}")
    
    charge_efficiency = params['Ladeeffizienz']
    discharge_efficiency = params['Entladeeffizienz'] 
    max_charge_rate = params['Max Ladeleistung']
    max_discharge_rate = params['Max Entladeleistung']
    min_battery_level = params['Min Ladezustand'] * params['Batteriekapazitaet']
    max_battery_level = params['Max Ladezustand'] * params['Batteriekapazitaet']

    # print(f"Net Load: {net_load}")
    # print(f"Initial Battery Energy: {battery_energy}")

    if net_load > 0:  # Mehr Last als Erzeugung, Batterie entladen
        discharge_power = min(net_load, max_discharge_rate)
        discharge_energy = discharge_power * discharge_efficiency
        
        if battery_energy - discharge_energy < min_battery_level:
            discharge_energy = battery_energy - min_battery_level
        
        battery_energy -= discharge_energy
        row['Batterie Ladung'] = -discharge_energy / discharge_efficiency
        if battery_energy < min_battery_level:
            row['Backup Generator'] = net_load - (discharge_energy / discharge_efficiency)
    else:  # Mehr Erzeugung als Last, Batterie laden
        charge_power = min(-net_load, max_charge_rate)
        charge_energy = charge_power * charge_efficiency
        
        if battery_energy + charge_energy > max_battery_level:
            charge_energy = max_battery_level - battery_energy
        
        battery_energy += charge_energy
        row['Batterie Ladung'] = charge_energy / charge_efficiency

    # Sicherstellen, dass die Batterieenergie innerhalb der Grenzen bleibt
    battery_energy = min(max(battery_energy, min_battery_level), max_battery_level)
    row['Batterie Energie'] = battery_energy

    return row, battery_energy


