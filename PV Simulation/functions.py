import constants as c
import pvlib
# from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.modelchain import ModelChain
import pandas as pd
import numpy as np
import time
from tkinter import messagebox
from sub_functions import create_data_folder, extract_module_parameters, extract_inverter_parameters



def process_zelt(zelt, anzahl_vars, belegung_vars, modul_parameter, temp_model_params):
    arrays = []
    array_names = []
    if zelt not in anzahl_vars or anzahl_vars[zelt].get() == 0 or zelt not in belegung_vars:
        return arrays, array_names

    zelt_mappings = {
        'Dach Ost': ('DACH_OST_', 'DACH_', 'MPS', 'STRINGS'),
        'Dach West': ('DACH_WEST_', 'DACH_', 'MPS', 'STRINGS'),
        'Seite Ost': ('SEITE_OST_', 'SEITEN_', 'MPS', 'STRINGS'),
        'Seite West': ('SEITE_WEST_', 'SEITEN_', 'MPS', 'STRINGS')
    }

    for key, (mount_prefix, module_prefix, mps_suffix, strings_suffix) in zelt_mappings.items():
        if belegung_vars[zelt][key].get():
            mount = getattr(c, f"{mount_prefix}{zelt}")
            modules_per_string = getattr(c, f"{module_prefix}{zelt}_{mps_suffix}")
            strings = getattr(c, f"{module_prefix}{zelt}_{strings_suffix}")
            arrays.append(Array(mount=mount, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params,
                                modules_per_string=modules_per_string, strings=strings))
            array_names.append(f"{key} {zelt}")
    return arrays, array_names

def run_model_chain(system, standort, wetterdaten, schrittweite):
    mc = ModelChain(system, standort, aoi_model=c.AOI_MODEL, spectral_model=c.SPECTRAL_MODEL)
    start_time = time.time()
    mc.run_model(wetterdaten)
    end_time = time.time()
    stromerzeugung = mc.results.ac
    erzeugte_energie = stromerzeugung.sum() * schrittweite / 60 / 1000  # in kWh umrechnen
    return erzeugte_energie, stromerzeugung, end_time - start_time

def calculation_pv(entries, anzahl_vars, belegung_vars, standort, wetterdaten, location_data, df_load):
    try:
        print("Berechnung gestartet")

        # Last aus df_loaf in df_result übernehmen
        df_results = df_load 

        # Modul- und Wechselrichterparameter extrahieren
        modul_parameter = extract_module_parameters(entries)
        wechselrichter_parameter = extract_inverter_parameters(entries)
        temp_model_params = {'u_c': 29.0, 'u_v': 0.0}

        # Arrays für alle Zelttypen erstellen
        zelttypen = ["SG20", "SG30", "SG40", "SG50"]
        arrays = []
        array_names = []
        for zelt in zelttypen:
            zelt_arrays, zelt_array_names = process_zelt(zelt, anzahl_vars, belegung_vars, modul_parameter, temp_model_params)
            arrays.extend(zelt_arrays)
            array_names.extend(zelt_array_names)

        if not arrays:
            raise ValueError("Es wurden keine Flächen ausgewählt.")

        erzeugte_energien = []
        stromerzeugungen = []
        berechnungszeiten = []

        for array in arrays:
            system = PVSystem(arrays=[array], inverter_parameters=wechselrichter_parameter)
            erzeugte_energie, stromerzeugung, berechnungszeit = run_model_chain(system, standort, wetterdaten, location_data['schrittweite'])
            erzeugte_energien.append(erzeugte_energie)
            stromerzeugungen.append(stromerzeugung)
            berechnungszeiten.append(berechnungszeit)

            # print Ausgabe
            # print(f"Array: {array}")
            
        #     print(f"Erzeugte Energie (kWh): {erzeugte_energie}")
        # DataFrame zusammenfügen
        df = pd.DataFrame(stromerzeugungen).T
        df.columns = array_names
        df_results  =pd.concat([df_results, df], axis=1)

        df_results[array_names] = df_results[array_names] / 1000        # von W in kW 

        # Summe der Zelte  
        df_results['PV Erzeugung'] = df_results[array_names].sum(axis=1)

        # print("array_names")
        # print(array_names)
        # print(f"df_results: \n{df_results}")

        return erzeugte_energien, stromerzeugungen, berechnungszeiten, df_results

    except Exception as e:
        print(f"Fehler bei der Durchführung der Berechnung: {e}")
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
        return None, None, None, None


