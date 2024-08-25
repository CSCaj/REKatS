import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import tkinter as tk
from tkinter import ttk
import constants as c
import constants_wind as cw
from sub_functions import create_data_folder, extract_location_data, save_results_to_excel, extract_wind_parameters
# from functions_wind import load_data, calculate_energy_output, calculate_daily_output, save_results, plot_wind_results, set_date_as_index


def wind_sim(entries, df_results):
    # Standortdaten extrahieren
    location_data = extract_location_data(entries)
    filename = f"pv_gis_data_{location_data['latitude']}_{location_data['longitude']}.csv"
    file_path = os.path.join(c.DATA_FOLDER, filename)
    print(f"WEA Standortdaten extrahieren: {filename}")

    # # CSV-Datei einlesen
    # df_wind = load_data(file_path)

    # # Datumsspalte als Index setzen
    # df_wind = set_date_as_index(df_wind)

    df_wind = pd.read_csv(file_path, index_col=0, parse_dates=True)
    df_wind.index = pd.to_datetime(df_wind.index).tz_localize(None)
    df_wind = df_wind[location_data['startzeit']:location_data['endzeit']]

    # Dynamische Parameter extrahieren
    params = extract_wind_parameters(entries)
    Anzahl = params['Anzahl WEA']
    v_min = params['v_min']
    v_n = params['v_n']
    v_max = params['v_max']
    P_n = params['P_n']

    

    # Ertragsberechnung durchführen
    df_wind = calculate_energy_output(
        df_wind, 
        v_min, 
        v_n, 
        v_max, 
        P_n
    )

    # Gesamtertrag für eine Anlage berechnen
    wind_energy_output_single = df_wind['power_output_wea'].sum() / 1000 # in kW
    # Gesamtertrag für alle Anlagen berechnen
    wind_energy_output_total = wind_energy_output_single * Anzahl

    # in df übertragen 
    df_results['power_output_wea'] = pd.DataFrame(df_wind['power_output_wea'])
    df_results['Wind Erzeugung'] = df_results['power_output_wea'] * Anzahl 
    # print('NEU df_results')
    # print(df_results)


    # Ergebnis speichern
    save_results_to_excel(
            df_wind, 
            c.EXPORT_FOLDER, 
            f"wind_power_output_{location_data['latitude']}_{location_data['longitude']}"
        )
    
    return df_wind, wind_energy_output_single, wind_energy_output_total, Anzahl


def power_curve(wind_speed, cut_in_speed, rated_speed, cut_out_speed, rated_power):
    """Berechnet die Leistung basierend auf der Windgeschwindigkeit."""

    if wind_speed < cut_in_speed:
        return 0
    elif cut_in_speed <= wind_speed < rated_speed:
        return rated_power * ((wind_speed - cut_in_speed) / (rated_speed - cut_in_speed)) ** 3
    elif rated_speed <= wind_speed < cut_out_speed:
        return rated_power
    else:
        return 0

def set_date_as_index(df_wind):
    """Setzt die Datumsspalte als Index."""
    df_wind.set_index(df_wind.columns[0], inplace=True)
    return df_wind

def load_data(file_path):
    """Lädt die Daten aus der CSV-Datei."""
    return pd.read_csv(file_path, parse_dates=[0])

def calculate_energy_output(df_wind, cut_in_speed, rated_speed, cut_out_speed, rated_power):
    """Berechnet den Energieausstoß basierend auf der Windgeschwindigkeit."""
    df_wind['power_output_wea'] = df_wind['wind_speed'].apply(lambda ws: power_curve(ws, cut_in_speed, rated_speed, cut_out_speed, rated_power))
    
    return df_wind

def calculate_daily_output(df_wind):
    """Berechnet den täglichen Energieausstoß."""
    df_wind['date'] = df_wind.iloc[:, 0].dt.date
    return df_wind.groupby('date')['power_output_wea'].sum()

# def plot_results(df, daily_output, cut_in_speed, rated_speed, cut_out_speed):
#     """Erstellt Diagramme für die Leistungskurve und den täglichen Energieausstoß."""
#     fig, axs = plt.subplots(2, 1, figsize=(10, 12))

#     # Leistungskurve
#     axs[0].plot(df['wind_speed'], df['power_output'], label='Leistungskurve', linestyle='none', marker='o')
#     axs[0].axvline(cut_in_speed, color='grey', linestyle='--', label='Schnittgeschwindigkeit')
#     axs[0].axvline(rated_speed, color='red', linestyle='--', label='Nenngeschwindigkeit')
#     axs[0].axvline(cut_out_speed, color='grey', linestyle='--', label='Abschaltgeschwindigkeit')
#     axs[0].set_xlabel('Windgeschwindigkeit (m/s)')
#     axs[0].set_ylabel('Leistung (W)')
#     axs[0].set_title(f"Leistungskurve einer Kleinwindkraftanlage mit einer Nennleistung von {cw.RATED_POWER} W")
#     axs[0].legend()
#     axs[0].grid(True)

#     # Täglicher Ertrag
#     axs[1].plot(daily_output.index, daily_output.values, label='Täglicher Ertrag')
#     axs[1].set_xlabel('Datum')
#     axs[1].set_ylabel('Täglicher Ertrag (Wh)')
#     axs[1].set_title('Täglicher Energieertrag über das Jahr')
#     axs[1].legend()
#     axs[1].grid(True)

#     plt.tight_layout()
#     plt.show()

# def plot_wind_results(df_wind, cut_in_speed, rated_speed, cut_out_speed, total_wind_energy_output):
#     """Erstellt Diagramme für die Leistungskurve und den stündlichen Energieausstoß."""
#     ergebnis_win = tk.Tk()
#     ergebnis_win.title("Ergebnis der Stromerzeugung")

#     notebook = ttk.Notebook(ergebnis_win)
#     notebook.pack(expand=1, fill='both')

#     #################################################
#     # 1. Tab
#     wind_frame = ttk.Frame(notebook)
#     notebook.add(wind_frame, text="Windsimulation")

#     fig = Figure(figsize=(10, 12))
#     axs = fig.subplots(2, 1)

#     # Leistungskurve
#     axs[0].plot(df_wind['wind_speed'], df_wind['power_output'], label='Leistungskurve', linestyle='none', marker='o')
#     axs[0].axvline(cut_in_speed, color='grey', linestyle='--', label='Schnittgeschwindigkeit')
#     axs[0].axvline(rated_speed, color='red', linestyle='--', label='Nenngeschwindigkeit')
#     axs[0].axvline(cut_out_speed, color='grey', linestyle='--', label='Abschaltgeschwindigkeit')
#     axs[0].set_xlabel('Windgeschwindigkeit (m/s)')
#     axs[0].set_ylabel('Leistung (W)')
#     axs[0].set_title('Leistungskurve einer Kleinwindkraftanlage basierend auf CSV-Daten')
#     axs[0].legend()
#     axs[0].grid(True)

#     # Stündlicher Ertrag
#     axs[1].plot(df_wind.index, df_wind['power_output'], label='Stündlicher Ertrag')
#     axs[1].set_xlabel('Datum und Uhrzeit')
#     axs[1].set_ylabel('Stündlicher Ertrag (Wh)')
#     axs[1].set_title('Stündlicher Energieertrag')
#     axs[1].legend()
#     axs[1].grid(True)

#     fig.tight_layout()

#     # Erstelle den Canvas und die Toolbar
#     canvas = FigureCanvasTkAgg(fig, master=wind_frame)
#     canvas.draw()
#     canvas_widget = canvas.get_tk_widget()
#     canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

#     toolbar = NavigationToolbar2Tk(canvas, wind_frame)
#     toolbar.update()
#     toolbar.pack(side=tk.TOP, fill=tk.X)

#     # Gesamtertrag anzeigen
#     result_label = tk.Label(wind_frame, text=f"Gesamtertrag: {total_wind_energy_output} Wh", font=("Helvetica", 16))
#     result_label.pack(pady=10)

#     ergebnis_win.mainloop()

def plot_wind_results(parent_frame, df_wind, cut_in_speed, rated_speed, cut_out_speed, wind_energy_output_single, wind_energy_output_total, Anzahl):
    """Erstellt Diagramme für die Leistungskurve und den stündlichen Energieausstoß."""
    fig = Figure(figsize=(8, 12))
    axs = fig.subplots(2, 1)

    # Leistungskurve für eine Einzelanlage
    axs[0].plot(df_wind['wind_speed'], df_wind['power_output_wea'], label='Leistungskurve', linestyle='none', marker='o')
    axs[0].axvline(cut_in_speed, color='grey', linestyle='--', label='Schnittgeschwindigkeit')
    axs[0].axvline(rated_speed, color='red', linestyle='--', label='Nenngeschwindigkeit')
    axs[0].axvline(cut_out_speed, color='grey', linestyle='--', label='Abschaltgeschwindigkeit')
    axs[0].set_xlabel('Windgeschwindigkeit (m/s)')
    axs[0].set_ylabel('Leistung (W)')
    axs[0].set_title('Leistungskurve einer Kleinwindkraftanlage')
    axs[0].legend()
    axs[0].grid(True)

    # Stündlicher Ertrag für eine Einzelanlage und alle Anlagen
    df_wind['total_power_output'] = df_wind['power_output_wea'] * Anzahl
    axs[1].plot(df_wind.index, df_wind['power_output_wea'], label='Stündlicher Ertrag einer Einzelanlage', color='blue')
    axs[1].plot(df_wind.index, df_wind['total_power_output'], label='Stündlicher Ertrag aller Anlagen', color='red')
    axs[1].set_xlabel('Datum und Uhrzeit')
    axs[1].set_ylabel('Stündlicher Ertrag (Wh)')
    axs[1].set_title('Stündlicher Energieertrag')
    axs[1].legend()
    axs[1].grid(True)

    fig.tight_layout()

    # Erstelle den Canvas und die Toolbar
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    toolbar = NavigationToolbar2Tk(canvas, parent_frame)
    toolbar.update()
    toolbar.pack(side=tk.TOP, fill=tk.X)

    # Gesamtertrag anzeigen
    result_label = tk.Label(parent_frame, text=f"Gesamtertrag einer Einzelanlage: {wind_energy_output_single:.2f} kWh\n"
                                              f"Gesamtertrag aller Anlagen: {wind_energy_output_total:.2f} kWh",
                           font=("Helvetica", 16))
    result_label.pack(pady=10)


