import pandas as pd
import numpy as np
import pvlib
from pvlib.pvsystem import PVSystem, Array, FixedMount
from pvlib.modelchain import ModelChain
from pvlib.location import Location
from tkinter import messagebox
import time
import constants as c



def download_tmy(latitude, longitude):
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
        start= "2021-01-01 00:00", 
            end= "2021-12-31 23:00", 
        freq= "h" 
    )
    
        pv_gis_data.to_csv("pv_gis_data.csv")
        print("pv_gis_data.csv wurde gespeichert")




def berechnung_durchfuehren(entries):
    try:
        latitude = float(entries[0]['Breitengrad'].get())
        longitude = float(entries[0]['Laengengrad'].get())
        altitude = float(entries[0]['Hoehe'].get())
        tilt = float(entries[0]['Anstellwinkel'].get())
        azimuth = float(entries[0]['azimuth'].get())
        startzeit = pd.Timestamp(entries[0]['startzeit'].get(), tz=c.ZEITZONE)
        endzeit = pd.Timestamp(entries[0]['endzeit'].get(), tz=c.ZEITZONE)
        schrittweite = int(entries[0]['schrittweite'].get())

        # standort = Location(
        #     latitude=latitude,
        #     longitude=longitude,
        #     altitude=altitude,
        #     tz=c.ZEITZONE
        # )

        # zeit_index = pd.date_range(start=startzeit, end=endzeit, freq=f'{schrittweite}min', tz=c.ZEITZONE)
        
        # # keine clear sky einstrahlung sondern tmy 
        # solare_einstrahlung = standort.get_clearsky(zeit_index)

        # #anpassung durch reale Temperatur 
        # temperaturen = pd.Series(20 + 5 * np.sin(np.linspace(0, 2 * np.pi, len(zeit_index))), index=zeit_index)
        # windgeschwindigkeit = pd.Series(2, index=zeit_index)

        # dni = pvlib.irradiance.erbs(solare_einstrahlung['ghi'], standort.get_solarposition(zeit_index)['apparent_zenith'], zeit_index)['dni']
        # dhi = solare_einstrahlung['ghi'] - dni * np.cos(np.radians(standort.get_solarposition(zeit_index)['apparent_zenith']))

        # wetterdaten = pd.DataFrame({
        #     'temp_air': temperaturen,
        #     'wind_speed': windgeschwindigkeit,
        #     'ghi': solare_einstrahlung['ghi'],
        #     'dni': dni,
        #     'dhi': dhi
        # }, index=zeit_index)

        #####################################################

        # TMY-Daten herunterladen und speichern
        download_tmy(latitude, longitude)
        
        # TMY-Daten einlesen
        wetterdaten = pd.read_csv('pv_gis_data.csv', index_col=0, parse_dates=True)
        
        # Wetterdaten-Zeitzone anpassen
        wetterdaten.index = wetterdaten.index.tz_localize(c.ZEITZONE, ambiguous='NaT')
        # Bei bereits tz-aware Daten:
        # wetterdaten.index = wetterdaten.index.tz_convert(c.ZEITZONE)
        
        # Filtern nach startzeit und endzeit
        wetterdaten = wetterdaten[startzeit:endzeit]

        #####################################################

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

        mount = FixedMount(surface_tilt=tilt, surface_azimuth=azimuth)

        array = Array(mount=mount, module_parameters=modul_parameter, temperature_model_parameters=temp_model_params)
        system = PVSystem(arrays=[array], inverter_parameters=wechselrichter_parameter)

        mc = ModelChain(system, standort, aoi_model='physical', spectral_model='no_loss')
        
        start_time = time.time()
        mc.run_model(wetterdaten)
        end_time = time.time()

        stromerzeugung = mc.results.ac
        erzeugte_energie = stromerzeugung.sum() * schrittweite / 60 / 1000  # in kWh umrechnen

        return erzeugte_energie, stromerzeugung, end_time - start_time

    except Exception as e:
        messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {e}")
        return None, None, None
