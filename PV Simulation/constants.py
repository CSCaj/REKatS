from pvlib.pvsystem import FixedMount

# Geographische Daten 
BREITENGRAD = 47.9936
LAENGENGRAD =  7.8522 
HOEHE = 278

# PV_parameter 
ANSTELLWINKEL = 30
AZIMUTH = 180 
STARTZEIT = '2021-06-04 00:00:00'
ENDZEIT =  '2021-06-04 23:59:59'
ZEITZONE = 'Europe/Berlin'

# TMY Parameter 
STARTJAHR = 2005
ENDJAHR = 2016

# Simulationsparameter 
SCHRITTWEITE = 1        # Noch nicht ganz richtig in der Funktion 
PDC0 = 300              # Nominal power of the module in W
GAMMA_PDC = -0.004      # Temperature coefficient in 1/C
A_REF = 1.5             
IL_REF = 6
I0_REF = 0.001
RS_REF = 0.5
RSH_REF =2000
ADJUST = 8.2
TECHNOLOGY = 'monocrystalline'
PDC0_INV = 3000          # Nominal power of the inverter in W
ETA_INV_NOM = 0.96      # Nominal efficiency
ETA_INV_REF = 0.9637    # Reference efficiency
AOI_MODEL = 'physical'  # AOI-Modells
SPECTRAL_MODEL = 'no_loss'     # Keine spektralen Verluste berücksichtigen

# Speicherpfade
DATA_FOLDER = 'pv_data' 
EXPORT_FOLDER = 'export'

## Zeltparameter 
# SG 20
DACH_OST_SG20 = FixedMount(surface_tilt=20, surface_azimuth=90)
DACH_WEST_SG20 = FixedMount(surface_tilt=20, surface_azimuth=270)
DACH_SG20_MPS = 8       # Modules per string 
DACH_SG20_STRINGS = 1   # Strings 

SEITE_OST_SG20 = FixedMount(surface_tilt=70, surface_azimuth=90)
SEITE_WEST_SG20 = FixedMount(surface_tilt=70, surface_azimuth=270)
SEITEN_SG20_MPS = 4
SEITEN_SG20_STRINGS = 2

SG20_LAENGE = 5.0
SG20_BREITE = 4.74
SG20_GEWICHT = 68
SG20_FELDBETTEN = 6

# SG 30 
DACH_OST_SG30 = FixedMount(surface_tilt=30, surface_azimuth=90)
DACH_WEST_SG30 = FixedMount(surface_tilt=30, surface_azimuth=270)
DACH_SG30_MPS = 12       # Modules per string 
DACH_SG30_STRINGS = 1   # Strings 

SEITE_OST_SG30 = FixedMount(surface_tilt=80, surface_azimuth=90)
SEITE_WEST_SG30 = FixedMount(surface_tilt=80, surface_azimuth=270)
SEITEN_SG30_MPS = 4
SEITEN_SG30_STRINGS = 2

SG30_LAENGE = 6.0
SG30_BREITE = 5.64
SG30_GEWICHT = 92 
SG30_FELDBETTEN = 10
SG30_GARNITUREN = 6
SG30_PLAETZE = 8 * SG30_GARNITUREN

# SG 40 
DACH_OST_SG40 = FixedMount(surface_tilt=40, surface_azimuth=90)
DACH_WEST_SG40 = FixedMount(surface_tilt=40, surface_azimuth=270)
DACH_SG40_MPS = 14       # Modules per string 
DACH_SG40_STRINGS = 1   # Strings 

SEITE_OST_SG40 = FixedMount(surface_tilt=90, surface_azimuth=90)
SEITE_WEST_SG40 = FixedMount(surface_tilt=90, surface_azimuth=270)
SEITEN_SG40_MPS = 4
SEITEN_SG40_STRINGS = 2

SG40_LAENGE = 8.0
SG40_BREITE = 5.64
SG40_GEWICHT = 116
SG40_FELDBETTEN = 12
SG40_GARNITUREN = 8
SG40_PLAETZE = 8 * SG40_GARNITUREN

# SG 50 
DACH_OST_SG50 = FixedMount(surface_tilt=50, surface_azimuth=90)
DACH_WEST_SG50 = FixedMount(surface_tilt=50, surface_azimuth=270)
DACH_SG50_MPS = 16       # Modules per string                           !!!!
DACH_SG50_STRINGS = 1   # Strings 

SEITE_OST_SG50 = FixedMount(surface_tilt=100, surface_azimuth=90)
SEITE_WEST_SG50 = FixedMount(surface_tilt=100, surface_azimuth=270)
SEITEN_SG50_MPS = 8                                                     # !
SEITEN_SG50_STRINGS = 2

SG50_LAENGE = 10.0
SG50_BREITE = 5.64
SG50_GEWICHT = 133
SG50_FELDBETTEN = 14
SG50_GARNITUREN = 12
SG50_PLAETZE = 8 * SG50_GARNITUREN

# Anzahl der jeweiligen SG
SG20_ANZAHL = 1
SG30_ANZAHL = 0
SG40_ANZAHL = 0
SG50_ANZAHL = 0


# Standardwerte für die Belegungen
SG20_BELEGUNGEN = {'Dach Ost': True, 'Dach West': True, 'Seite Ost': False, 'Seite West': False}
SG30_BELEGUNGEN = {'Dach Ost': True, 'Dach West': True, 'Seite Ost': False, 'Seite West': False}
SG40_BELEGUNGEN = {'Dach Ost': False, 'Dach West': False, 'Seite Ost': False, 'Seite West': False}
SG50_BELEGUNGEN = {'Dach Ost': False, 'Dach West': False, 'Seite Ost': False, 'Seite West': False}


## Diesel       (https://de.wikipedia.org/wiki/Dieselkraftstoff) 
# Wirkungsgrad Verbrenner
DIESEL_MOTOR_ETA = 0.35

#Dichte 
DIESEL_DICHTE = 0.8325 # kg/l (15°C)

# Energiekonstanten 
DIESEL_E_DICHTE = 9.8 # kWh/l (Heizwert)

# Kohlendioxidemissionen bei Verbrennung
DIESEL_CO2 = 2.65 # kg/l