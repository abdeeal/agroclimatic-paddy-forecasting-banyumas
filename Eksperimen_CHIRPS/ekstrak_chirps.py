# =========================================================
# EKSTRAKSI CURAH HUJAN CHIRPS v2.0 BULANAN PER KECAMATAN (BANYUMAS)
# Sumber : https://data.chc.ucsb.edu/products/CHIRPS/v2.0/global_monthly/cogs/
# Metode : COG dibaca jarak jauh (hanya jendela Banyumas), lalu rata-rata
#          tertimbang luas piksel yang beririsan dengan poligon kecamatan.
# Output : CHIRPS_Bulanan_Kecamatan.csv (format lebar seperti Curah-hujan.csv)
# =========================================================
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from rasterio.features import rasterize
from concurrent.futures import ThreadPoolExecutor

sys.stdout.reconfigure(encoding='utf-8')

URL = "https://data.chc.ucsb.edu/products/CHIRPS/v2.0/global_monthly/cogs/chirps-v2.0.{y}.{m:02d}.cog"
YEARS = range(2013, 2025)
MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
SUPERSAMPLE = 10  # tiap piksel 0,05° dibagi 10x10 untuk menghitung fraksi luas irisan

gdf = gpd.read_file("ADMINISTRASIDESA_AR_25K.shp")
gdf = gdf[gdf['WADMKK'] == 'Kabupaten Banyumas'].dissolve(by='WADMKC').reset_index()[['WADMKC', 'geometry']]
master_kec = set(pd.read_csv("Dataset_Master_TA_Padi_Spatial.csv")['WADMKC'])
print(f"Kecamatan di shapefile: {len(gdf)} | di dataset master: {len(master_kec)}")
print("Tidak cocok:", sorted(set(gdf['WADMKC']) ^ master_kec) or "tidak ada")

minx, miny, maxx, maxy = gdf.total_bounds
pad = 0.1
env = {'GDAL_DISABLE_READDIR_ON_OPEN': 'EMPTY_DIR', 'GDAL_HTTP_MAX_RETRY': '5', 'GDAL_HTTP_RETRY_DELAY': '2'}

# Grid jendela & bobot fraksi luas per kecamatan (dihitung sekali)
with rasterio.Env(**env), rasterio.open(URL.format(y=2020, m=1)) as src:
    win = from_bounds(minx - pad, miny - pad, maxx + pad, maxy + pad, src.transform).round_offsets().round_lengths()
    w_transform = src.window_transform(win)
    shape = (int(win.height), int(win.width))
    nodata = src.nodata
fine_transform = w_transform * rasterio.Affine.scale(1 / SUPERSAMPLE)
fine_shape = (shape[0] * SUPERSAMPLE, shape[1] * SUPERSAMPLE)
weights = {}
for kec, geom in zip(gdf['WADMKC'], gdf.geometry):
    fine = rasterize([(geom, 1)], out_shape=fine_shape, transform=fine_transform, dtype='uint8')
    weights[kec] = fine.reshape(shape[0], SUPERSAMPLE, shape[1], SUPERSAMPLE).mean(axis=(1, 3))
n_pix = {k: int((w > 0).sum()) for k, w in weights.items()}
print(f"Jendela raster: {shape[0]}x{shape[1]} piksel; piksel tersentuh per kecamatan: "
      f"min {min(n_pix.values())}, median {int(np.median(list(n_pix.values())))}, max {max(n_pix.values())}")

def read_month(ym):
    y, m = ym
    with rasterio.Env(**env), rasterio.open(URL.format(y=y, m=m)) as src:
        arr = src.read(1, window=win).astype(float)
    if nodata is not None:
        arr[arr == nodata] = np.nan
    arr[arr < 0] = np.nan
    return ym, arr

with ThreadPoolExecutor(max_workers=6) as ex:
    rasters = dict(ex.map(read_month, [(y, m) for y in YEARS for m in range(1, 13)]))
print(f"Raster terbaca: {len(rasters)} bulan")

rows = []
for y in YEARS:
    for kec, w in weights.items():
        rec = {'WADMKC': kec, 'YEAR': y}
        for m in range(1, 13):
            a = rasters[(y, m)]
            ok = ~np.isnan(a) & (w > 0)
            rec[MONTHS[m - 1]] = round(float((a[ok] * w[ok]).sum() / w[ok].sum()), 2)
        rec['ANN'] = round(sum(rec[c] for c in MONTHS), 2)
        rows.append(rec)
df = pd.DataFrame(rows).sort_values(['YEAR', 'WADMKC'])
df.to_csv("CHIRPS_Bulanan_Kecamatan.csv", index=False)
pd.DataFrame({'WADMKC': list(n_pix), 'N_PIKSEL_CHIRPS': list(n_pix.values())}).to_csv("CHIRPS_Piksel_per_Kecamatan.csv", index=False)
print("Tersimpan: CHIRPS_Bulanan_Kecamatan.csv", df.shape)
