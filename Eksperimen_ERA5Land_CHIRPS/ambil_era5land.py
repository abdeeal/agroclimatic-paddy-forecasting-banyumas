# =========================================================
# AMBIL DATA HARIAN ERA5-LAND (0,1°) & ERA5 (0,25°) PER KECAMATAN, 2013-2024
# Sumber : Open-Meteo Historical Weather API (archive-api.open-meteo.com),
#          yang menyajikan ulang reanalysis ECMWF ERA5-Land dan ERA5.
#   ERA5-Land : suhu maks/min/rata-rata harian, kelembaban relatif rata-rata harian
#   ERA5      : radiasi gelombang pendek harian (Open-Meteo tidak menyediakan
#               radiasi ERA5-Land)
# Titik      : titik representatif di dalam poligon tiap kecamatan; sel grid terdekat
#              (cell_selection=nearest) tanpa koreksi elevasi (elevation=nan).
# Output     : ERA5_Harian_Kecamatan.csv
# =========================================================
import sys
import json
import time
import urllib.request
import urllib.error
import geopandas as gpd
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

URL = "https://archive-api.open-meteo.com/v1/archive"
START, END = "2013-01-01", "2024-12-31"
REQUESTS = [
    ('era5_land', ['temperature_2m_max', 'temperature_2m_min', 'temperature_2m_mean', 'relative_humidity_2m_mean']),
    ('era5', ['shortwave_radiation_sum']),
]

gdf = gpd.read_file("ADMINISTRASIDESA_AR_25K.shp")
gdf = gdf[gdf['WADMKK'] == 'Kabupaten Banyumas'].dissolve(by='WADMKC').reset_index()
pts = gdf.to_crs(epsg=32749).representative_point().to_crs(epsg=4326)
loc = pd.DataFrame({'WADMKC': gdf['WADMKC'], 'LAT': pts.y.round(4), 'LON': pts.x.round(4)})

def fetch(lat, lon, model, variables):
    q = (f"{URL}?latitude={lat}&longitude={lon}&start_date={START}&end_date={END}"
         f"&daily={','.join(variables)}&models={model}&elevation=nan&cell_selection=nearest"
         f"&timezone=Asia%2FJakarta")
    for attempt in range(8):
        try:
            with urllib.request.urlopen(q, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(65)  # batas laju per menit
                continue
            raise
        except urllib.error.URLError:
            time.sleep(10)
    raise RuntimeError(f"gagal mengambil {model} untuk {lat},{lon}")

frames, cells = [], []
for _, r in loc.iterrows():
    parts = []
    for model, variables in REQUESTS:
        js = fetch(r.LAT, r.LON, model, variables)
        d = pd.DataFrame(js['daily'])
        d['time'] = pd.to_datetime(d['time'])
        parts.append(d.set_index('time'))
        cells.append({'WADMKC': r.WADMKC, 'MODEL': model, 'GRID_LAT': round(js['latitude'], 3),
                      'GRID_LON': round(js['longitude'], 3), 'ELEVASI_GRID': js.get('elevation')})
    df = pd.concat(parts, axis=1).reset_index().rename(columns={'time': 'DATE'})
    df.insert(0, 'WADMKC', r.WADMKC)
    frames.append(df)
    print(f"  {r.WADMKC:20s} OK ({len(df)} hari)", flush=True)
    time.sleep(2)

out = pd.concat(frames)
out.to_csv("ERA5_Harian_Kecamatan.csv", index=False)
cell_df = pd.DataFrame(cells)
cell_df.to_csv("ERA5_Grid_per_Kecamatan.csv", index=False)
print("Tersimpan: ERA5_Harian_Kecamatan.csv", out.shape)
print("Missing per kolom:\n", out.isna().sum().to_string())
for m, g in cell_df.groupby('MODEL'):
    print(f"{m}: {g[['GRID_LAT', 'GRID_LON']].drop_duplicates().shape[0]} sel grid unik untuk 27 kecamatan")
