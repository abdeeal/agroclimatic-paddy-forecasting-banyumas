# =========================================================
# SIAPKAN INPUT NOTEBOOK VERSI CHIRPS
# - Dataset_Master_TA_Padi_Spatial.csv : TOTAL_HUJAN & BULAN_BASAH diganti CHIRPS
#   (suhu, radiasi, kelembaban tetap NASA POWER)
# - Curah-hujan.csv : hujan bulanan CHIRPS per kecamatan, LAT/LON = titik representatif
#   di dalam poligon kecamatan, sehingga pemetaan sjoin_nearest di notebook = 1 kecamatan : 1 titik
# Versi NASA POWER asli disimpan dengan akhiran _NASA.csv
# =========================================================
import os
import sys
import shutil
import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

WET_MM = 200
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

for f in ["Dataset_Master_TA_Padi_Spatial.csv", "Curah-hujan.csv"]:
    nasa = f.replace(".csv", "_NASA.csv")
    if not os.path.exists(nasa):
        shutil.copy(f, nasa)

chirps = pd.read_csv("CHIRPS_Bulanan_Kecamatan.csv")
chirps['BB_CHIRPS'] = (chirps[MONTHS] > WET_MM).sum(axis=1)

master = pd.read_csv("Dataset_Master_TA_Padi_Spatial_NASA.csv")
master = master.merge(chirps[['WADMKC', 'YEAR', 'ANN', 'BB_CHIRPS']],
                      left_on=['WADMKC', 'YEAR_fitur'], right_on=['WADMKC', 'YEAR'], how='left')
assert master['ANN'].notna().all(), "ada baris master tanpa data CHIRPS"
master['TOTAL_HUJAN'] = master['ANN']
master['BULAN_BASAH'] = master['BB_CHIRPS']
master = master.drop(columns=['YEAR', 'ANN', 'BB_CHIRPS'])
master.to_csv("Dataset_Master_TA_Padi_Spatial.csv", index=False)

gdf = gpd.read_file("ADMINISTRASIDESA_AR_25K.shp")
gdf = gdf[gdf['WADMKK'] == 'Kabupaten Banyumas'].dissolve(by='WADMKC').reset_index()
pts = gdf.to_crs(epsg=32749).representative_point().to_crs(epsg=4326)
loc = pd.DataFrame({'WADMKC': gdf['WADMKC'], 'LAT': pts.y.round(5), 'LON': pts.x.round(5)})

ch = chirps.merge(loc, on='WADMKC')
ch.insert(0, 'PARAMETER', 'CHIRPS_V2_PRECIP')
ch = ch[['PARAMETER', 'YEAR', 'LAT', 'LON'] + MONTHS + ['ANN']].sort_values(['YEAR', 'LAT', 'LON'])
ch.to_csv("Curah-hujan.csv", index=False)

print("Master:", master.shape, "| Curah-hujan:", ch.shape, "| titik unik:", len(loc))
print(master[['TOTAL_HUJAN', 'BULAN_BASAH']].describe().round(1).to_string())
