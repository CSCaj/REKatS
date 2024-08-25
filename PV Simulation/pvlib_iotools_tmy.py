import pvlib
import pandas as pd 
import constants as c 


pv_gis_data, input, meta = pvlib.iotools.get_pvgis_tmy(
    latitude = c.BREITENGRAD, 
    longitude = c.LAENGENGRAD, 
    start=2020, end=2020, 
    raddatabase="PVGIS-SARAH2", components=True, 
    surface_tilt=45, surface_azimuth=0, 
    outputformat='json', usehorizon=True, 
    userhorizon=None, 
    pvcalculation=False, # deaktiviert die PV Kalkulation von PV lib 
    peakpower=None, pvtechchoice='crystSi', 
    mountingplace='free', loss=0, trackingtype=0, 
    optimal_surface_tilt=False, optimalangles=False, 
    url='https://re.jrc.ec.europa.eu/api/v5_2/', 
    map_variables=True, timeout=30)



pv_gis_data['poa_diffuse'] = pv_gis_data['poa_sky_diffuse']+ pv_gis_data['poa_ground_diffuse']
pv_gis_data['poa_global'] = pv_gis_data['poa_diffuse'] + pv_gis_data['poa_direct']

# pv_gis_data.index = pd.to_datetime(pv_gis_data.index, format="%Y%m%d:H&M") print(pv_gis_data)
# pv_gis_data.to_csv("pv_gis_data.csv")

print(pv_gis_data)