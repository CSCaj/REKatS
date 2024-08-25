import constants as c
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import pvlib
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem, Array, FixedMount
import os
from tkinter import messagebox


def diesel_berechnung(erzeugte_energie):
    try:
        dieselmenge = erzeugte_energie /(c.DIESEL_E_DICHTE * c.DIESEL_MOTOR_ETA)  # l
        eingesparte_energie = dieselmenge * c.DIESEL_E_DICHTE # kWh
        # print(f"Eingesparter Diesel: {dieselmenge:.2f} l \nEingesparte Dieselenergie: {eingesparte_energie:.2f} kWh")

        return dieselmenge, eingesparte_energie
    except Exception as e:
        print(f"Fehler bei der Dieselberchnung: {e}")

def save_results(text, stromerzeugungen, summierte_erzeugung, figs):
    # Zusammenführen aller stromerzeugungen in ein DataFrame
    df_stromerzeugungen = pd.concat([stromerzeugung.reset_index(drop=True) for stromerzeugung in stromerzeugungen], axis=1)
    df_stromerzeugungen.columns = [f'Fläche {idx+1}' for idx in range(len(stromerzeugungen))]
    
    # Hinzufügen der summierten Erzeugung als separate Spalte
    df_stromerzeugungen['Summierte Erzeugung'] = summierte_erzeugung.reset_index(drop=True)
    
    # Dateispeicher-Dialog für Excel-Datei
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                             filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
    if file_path:
        # Daten in ein Excel-Dokument schreiben
        with pd.ExcelWriter(file_path) as writer:
            # Text in DataFrame umwandeln
            lines = text.split('\n')
            data = [line.split(': ') for line in lines if ': ' in line]
            df_params = pd.DataFrame(data, columns=['Bezeichnung', 'Wert'])
            
            # DataFrame "params" erstellen
            df_params.to_excel(writer, sheet_name='params', index=False)
            
            # DataFrame "stromerzeugungen" erstellen
            df_stromerzeugungen.to_excel(writer, sheet_name='stromerzeugungen', index=False)
    
    # Dateispeicher-Dialog für Plot als Bild
    img_path = filedialog.asksaveasfilename(defaultextension=".png",
                                            filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if img_path:
        # Plot als Bild speichern
        figs.savefig(img_path)

def save_results_to_excel(df, folder, filename_prefix):
    """Speichert die Ergebnisse in CSV- und XLSX-Dateien."""
    create_data_folder(folder)
    csv_path = os.path.join(folder, f"{filename_prefix}.csv")
    xlsx_path = os.path.join(folder, f"{filename_prefix}.xlsx")
    df.to_csv(csv_path, index=True)
    df.to_excel(xlsx_path, index=True)

def create_data_folder(folder_name):
    try:
        # Erstelle den Unterordner, wenn er noch nicht existiert
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)  # Verwende makedirs, um Unterordner zu erstellen, falls erforderlich
            print(f"Der Ordner '{folder_name}' wurde erfolgreich erstellt.")
        else:
            print(f"Der Ordner '{folder_name}' existiert bereits.")
    except Exception as e:
        print(f"Fehler beim Erstellen des Ordners '{folder_name}': {e}")

def get_data(entries): 
    # Standortdaten extrahieren
    location_data = extract_location_data(entries)
    standort = Location(latitude=location_data['latitude'], longitude=location_data['longitude'], 
                        altitude=location_data['altitude'], tz=c.ZEITZONE)
    # print(f"Standort definiert: {standort}")

    # TMY-Daten einlesen
    filename = f"pv_gis_data_{location_data['latitude']}_{location_data['longitude']}.csv"
    file_path = os.path.join(c.DATA_FOLDER, filename)
    if not os.path.exists(file_path):
        download_tmy(location_data['latitude'], location_data['longitude'], filename)

    wetterdaten = pd.read_csv(file_path, index_col=0, parse_dates=True)
    wetterdaten.index = pd.to_datetime(wetterdaten.index).tz_localize(None)
    wetterdaten = wetterdaten[location_data['startzeit']:location_data['endzeit']]

    return standort, wetterdaten, location_data

def download_tmy(latitude, longitude, filename):
    try:
        print(f"Downloading TMY data for latitude: {latitude}, longitude: {longitude}")
        pv_gis_data, input_data, meta, additional_info = pvlib.iotools.get_pvgis_tmy(
            latitude=latitude,
            longitude=longitude,
            startyear=c.STARTJAHR,
            endyear=c.ENDJAHR,
            outputformat='json',
            usehorizon=True,
            userhorizon=None,
            url='https://re.jrc.ec.europa.eu/api/v5_2/',
            map_variables=True,
            timeout=30
        )
        pv_gis_data.index = pd.date_range(
            start="2021-01-01 00:00",
            end="2021-12-31 23:00",
            freq="h",
        )

        # Ordner erstellen, falls nicht vorhanden
        create_data_folder(c.DATA_FOLDER)

        pv_gis_data.to_csv(os.path.join(c.DATA_FOLDER, filename))  # Vollständigen Pfad verwenden
        print(f"{filename} wurde gespeichert")
    except Exception as e:
        print(f"Fehler beim Herunterladen der TMY-Daten: {e}")
        raise

def extract_location_data(entries):
    return {
        'latitude': float(entries[0]['Breitengrad'].get()),
        'longitude': float(entries[0]['Laengengrad'].get()),
        'altitude': float(entries[0]['Hoehe'].get()),
        'tilt': float(entries[0]['Anstellwinkel'].get()),
        'azimuth': float(entries[0]['azimuth'].get()),
        'startzeit': pd.Timestamp(entries[0]['startzeit'].get()),
        'endzeit': pd.Timestamp(entries[0]['endzeit'].get()),
        'schrittweite': int(entries[0]['schrittweite'].get())
    }

def extract_module_parameters(entries):
    return {
        'pdc0': float(entries[1]['pdc0'].get()),
        'gamma_pdc': float(entries[1]['gamma_pdc'].get()),
        'a_ref': float(entries[1]['a_ref'].get()),
        'Il_ref': float(entries[1]['Il_ref'].get()),
        'I0_ref': float(entries[1]['I0_ref'].get()),
        'Rs_ref': float(entries[1]['Rs_ref'].get()),
        'Rsh_ref': float(entries[1]['Rsh_ref'].get()),
        'Adjust': float(entries[1]['Adjust'].get()),
        'Technology': entries[1]['Technology'].get()
    }

def extract_inverter_parameters(entries):
    return {
        'pdc0': float(entries[2]['pdc0_inv'].get()),
        'eta_inv_nom': float(entries[2]['eta_inv_nom'].get()),
        'eta_inv_ref': float(entries[2]['eta_inv_ref'].get())
    }

def extract_wind_parameters(entries):
    return {
        'Anzahl WEA': float(entries[3]['Anzahl WEA'].get()),
        'v_min': float(entries[3]['v_min'].get()),
        'v_n': float(entries[3]['v_n'].get()),
        'v_max': float(entries[3]['v_max'].get()),
        'P_n': float(entries[3]['P_n'].get())
    }

def extract_bat_data(entries): 
    return {
        'Batteriekapazitaet': float(entries[4]['Batteriekapazitaet'].get()),
        'Ladeeffizienz': float(entries[4]['Ladeeffizienz'].get()),
        'Entladeeffizienz': float(entries[4]['Entladeeffizienz'].get()),
        'Max Ladeleistung': float(entries[4]['Max Ladeleistung'].get()),
        'Max Entladeleistung': float(entries[4]['Max Entladeleistung'].get()),
        'Anfangsenergie': float(entries[4]['Anfangsenergie'].get()), 
        'Min Ladezustand': float(entries[4]['Min Ladezustand'].get()), 
        'Max Ladezustand': float(entries[4]['Max Ladezustand'].get())

    }



def update_vars(anzahl_vars, belegung_vars):
    for zelt, var in anzahl_vars.items():
        print(f"Updating {zelt}_ANZAHL to {var.get()}")
    for zelt, belegungen in belegung_vars.items():
        for belegung, var in belegungen.items():
            print(f"Updating {zelt}_{belegung} to {var.get()}")

def get_load_profile(entries):
    num_tents = 4
    # Standortdaten extrahieren
    location_data = extract_location_data(entries)
    
    # Definieren des Zeitbereichs
    startzeit = pd.to_datetime(location_data['startzeit'])
    endzeit = pd.to_datetime(location_data['endzeit'])
    num_days = (endzeit - startzeit).days + 1
    time_range = pd.date_range(start=startzeit, end=endzeit, freq='H')
    
    # Erstellung eines leeren DataFrames
    df_load = pd.DataFrame(index=time_range, columns=['Leistungsbedarf Zelt'])

    # Definition der Lastprofile für verschiedene Tageszeiten
    time_intervals = [
        ('00:00', '06:00', 0.200),
        ('06:00', '09:00', 0.500),
        ('09:00', '18:00', 0.300),
        ('18:00', '22:00', 0.600),
        ('22:00', '00:00', 0.300)
    ]

    # Füllen des DataFrames mit Lastprofil-Daten
    # num_tents = location_data['num_tents']
    
    for start, end, load in time_intervals:
        daily_mask = (df_load.index.time >= pd.to_datetime(start).time()) & (df_load.index.time < pd.to_datetime(end).time())
        for day in range(num_days):
            mask = daily_mask & (df_load.index.date == (startzeit.date() + pd.Timedelta(days=day)))
            df_load.loc[mask, 'Leistungsbedarf Zelt'] = load 

    # Korrektur für den Zeitbereich '22:00' bis '00:00' jeden Tag
    for day in range(num_days):
        mask = (df_load.index.time >= pd.to_datetime('22:00').time()) & (df_load.index.time < pd.to_datetime('23:59').time()) & (df_load.index.date == (startzeit.date() + pd.Timedelta(days=day)))
        df_load.loc[mask, 'Leistungsbedarf Zelt'] = 0.300 

    df_load['Leistungsbedarf Wohnbereich'] = df_load['Leistungsbedarf Zelt'] * num_tents
    df_load['Gesamtlast'] = df_load['Leistungsbedarf Wohnbereich']

    return df_load

def sum_re(df_results):
    df_results['Erzeugung EE'] = df_results['PV Erzeugung'] + df_results['Wind Erzeugung']
    return df_results
