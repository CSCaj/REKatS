import constants as c
import pvlib
from pvlib.location import Location
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.modelchain import ModelChain
import pandas as pd
import numpy as np
import os
import time
from tkinter import messagebox



def create_data_folder():
    try:
        # Erstelle den Unterordner, wenn er noch nicht existiert
        if not os.path.exists(c.DATA_FOLDER):
            os.makedirs(c.DATA_FOLDER)  # Verwende makedirs, um Unterordner zu erstellen, falls erforderlich
            print(f"Der Ordner '{c.DATA_FOLDER}' wurde erfolgreich erstellt.")
        else:
            print(f"Der Ordner '{c.DATA_FOLDER}' existiert bereits.")
    except Exception as e:
        print(f"Fehler beim Erstellen des Ordners '{c.DATA_FOLDER}': {e}")

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
        create_data_folder()

        pv_gis_data.to_csv(os.path.join(c.DATA_FOLDER, filename))  # Vollständigen Pfad verwenden
        print(f"{filename} wurde gespeichert")
    except Exception as e:
        print(f"Fehler beim Herunterladen der TMY-Daten: {e}")
        raise

def berechnung_durchfuehren(entries, anzahl_vars, belegung_vars):
    try:
        # Ordner erstellen, falls nicht vorhanden
        create_data_folder()
        print("Berechnung gestartet")
        latitude = float(entries[0]['Breitengrad'].get())
        longitude = float(entries[0]['Laengengrad'].get())
        altitude = float(entries[0]['Hoehe'].get())
        tilt = float(entries[0]['Anstellwinkel'].get())
        azimuth = float(entries[0]['azimuth'].get())
        startzeit = pd.Timestamp(entries[0]['startzeit'].get())
        endzeit = pd.Timestamp(entries[0]['endzeit'].get())
        schrittweite = int(entries[0]['schrittweite'].get())

        print(f"Standortdaten: latitude={latitude}, longitude={longitude}, altitude={altitude}")

        standort = Location(
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            tz=c.ZEITZONE
        )
        print(f"Standort definiert: {standort}")

        # Dateiname basierend auf den Koordinaten generieren
        filename = f"pv_gis_data_{latitude}_{longitude}.csv"

        # Prüfen, ob die Datei bereits existiert
        file_path = os.path.join(c.DATA_FOLDER, filename)
        if not os.path.exists(file_path):
            # TMY-Daten herunterladen und speichern
            download_tmy(latitude, longitude, filename)

        # TMY-Daten einlesen
        wetterdaten = pd.read_csv(file_path, index_col=0, parse_dates=True)

        # Wetterdaten-Zeitzone anpassen
        wetterdaten.index = pd.to_datetime(wetterdaten.index).tz_localize(None)

        # Filtern nach startzeit und endzeit
        wetterdaten = wetterdaten[startzeit:endzeit]

        modul_parameter = {
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

        wechselrichter_parameter = {
            'pdc0': float(entries[2]['pdc0_inv'].get()),
            'eta_inv_nom': float(entries[2]['eta_inv_nom'].get()),
            'eta_inv_ref': float(entries[2]['eta_inv_ref'].get())
        }

        temp_model_params = {
            'u_c': 29.0,
            'u_v': 0.0
        }

        arrays = []
        zelttypen = ["SG20", "SG30", "SG40", "SG50"]
        print(f"Zelttypen: {zelttypen}")


        for zelt in zelttypen:
            print(f"Verarbeitung von Zelt: {zelt}")
            if zelt not in anzahl_vars:
                print(f"Zelt {zelt} nicht in anzahl_vars vorhanden.")
                continue
            
            if anzahl_vars[zelt].get() == 0:
                continue  # Skip this tent type if its count is 0
            
            if zelt not in belegung_vars:
                print(f"Zelt {zelt} nicht in belegung_vars vorhanden.")
                continue
            
            # Montagesysteme definieren für Ost- und Westausrichtung des Daches und der Seiten für den aktuellen Zelttyp
            mount_dach_ost = getattr(c, f"DACH_OST_{zelt}")
            mount_dach_west = getattr(c, f"DACH_WEST_{zelt}")
            mount_seite_ost = getattr(c, f"SEITE_OST_{zelt}")
            mount_seite_west = getattr(c, f"SEITE_WEST_{zelt}")

            if belegung_vars[zelt]['Dach Ost'].get():  # Dach Ost
                modules_per_string = getattr(c, f"DACH_{zelt}_MPS")
                strings = getattr(c, f"DACH_{zelt}_STRINGS")
                array_dach_ost = Array(mount=mount_dach_ost, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params,
                                       modules_per_string=modules_per_string, strings=strings)
                arrays.append(array_dach_ost)

            if belegung_vars[zelt]['Dach West'].get():  # Dach West
                modules_per_string = getattr(c, f"DACH_{zelt}_MPS")
                strings = getattr(c, f"DACH_{zelt}_STRINGS")
                array_dach_west = Array(mount=mount_dach_west, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params,
                                        modules_per_string=modules_per_string, strings=strings)
                arrays.append(array_dach_west)

            if belegung_vars[zelt]['Seite Ost'].get():  # Seite Ost
                modules_per_string = getattr(c, f"SEITEN_{zelt}_MPS")
                strings = getattr(c, f"SEITEN_{zelt}_STRINGS")
                array_seite_ost = Array(mount=mount_seite_ost, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params,
                                        modules_per_string=modules_per_string, strings=strings)
                arrays.append(array_seite_ost)

            if belegung_vars[zelt]['Seite West'].get():  # Seite West
                modules_per_string = getattr(c, f"SEITEN_{zelt}_MPS")
                strings = getattr(c, f"SEITEN_{zelt}_STRINGS")
                array_seite_west = Array(mount=mount_seite_west, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params,
                                         modules_per_string=modules_per_string, strings=strings)
                arrays.append(array_seite_west)

        if not arrays:
            raise ValueError("Es wurden keine Flächen ausgewählt.")

        erzeugte_energien = []
        stromerzeugungen = []
        berechnungszeiten = []

        for array in arrays:
            # PV-System mit ausgewähltem Array erstellen
            system = PVSystem(arrays=[array], inverter_parameters=wechselrichter_parameter)

            mc = ModelChain(system, standort, aoi_model=c.AOI_MODEL, spectral_model=c.SPECTRAL_MODEL)

            start_time = time.time()
            mc.run_model(wetterdaten)
            end_time = time.time()

            stromerzeugung = mc.results.ac
            erzeugte_energie = stromerzeugung.sum() * schrittweite / 60 / 1000  # in kWh umrechnen

            erzeugte_energien.append(erzeugte_energie)
            stromerzeugungen.append(stromerzeugung)
            berechnungszeiten.append(end_time - start_time)

        return erzeugte_energien, stromerzeugungen, berechnungszeiten

    except Exception as e:
        print(f"Fehler bei der Durchführung der Berechnung: {e}")
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
        return None, None, None
