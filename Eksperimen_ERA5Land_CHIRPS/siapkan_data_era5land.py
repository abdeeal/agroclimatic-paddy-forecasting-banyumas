# =========================================================
# SIAPKAN DATASET MASTER VERSI ERA5-LAND + CHIRPS
# Hujan (TOTAL_HUJAN, BULAN_BASAH)  : CHIRPS v2.0 (sudah ada di dataset master versi CHIRPS)
# Suhu & kelembaban                 : ERA5-Land (0,1°), harian -> tahunan
# Radiasi                           : ERA5 (0,25°), harian -> tahunan
# Definisi agregasi tahunan (tahun kalender t):
#   MAX_SUHU_THN   = maksimum suhu maksimum harian
#   MIN_SUHU_THN   = minimum suhu minimum harian
#   AVG_SUHU       = rata-rata suhu rata-rata harian
#   AVG_KELEMBABAN = rata-rata kelembaban relatif harian (%)
#   AVG_RADIASI    = rata-rata radiasi gelombang pendek harian (MJ/m²/hari)
# =========================================================
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

d = pd.read_csv("ERA5_Harian_Kecamatan.csv", parse_dates=['DATE'])
d['YEAR'] = d['DATE'].dt.year
ann = d.groupby(['WADMKC', 'YEAR']).agg(
    MAX_SUHU_THN=('temperature_2m_max', 'max'),
    MIN_SUHU_THN=('temperature_2m_min', 'min'),
    AVG_SUHU=('temperature_2m_mean', 'mean'),
    AVG_KELEMBABAN=('relative_humidity_2m_mean', 'mean'),
    AVG_RADIASI=('shortwave_radiation_sum', 'mean'),
).reset_index()

ERA_COLS = ['MAX_SUHU_THN', 'MIN_SUHU_THN', 'AVG_SUHU', 'AVG_KELEMBABAN', 'AVG_RADIASI']
master = pd.read_csv("Dataset_Master_TA_Padi_Spatial.csv")  # versi CHIRPS (hujan)
nasa = pd.read_csv("Dataset_Master_TA_Padi_Spatial_NASA.csv")
master = master.drop(columns=ERA_COLS).merge(
    ann, left_on=['WADMKC', 'YEAR_fitur'], right_on=['WADMKC', 'YEAR'], how='left').drop(columns='YEAR')
assert master[ERA_COLS].notna().all().all(), "ada baris tanpa data ERA5"
master = master[nasa.columns]
for c in ERA_COLS:
    master[c] = master[c].round(2)
master.to_csv("Dataset_Master_TA_Padi_Spatial.csv", index=False)

print("Dataset master ERA5-Land + CHIRPS:", master.shape)
cmp = master.merge(nasa, on=['WADMKC', 'YEAR_fitur'], suffixes=('_ERA', '_NASA'))
rows = []
for c in ['TOTAL_HUJAN', 'BULAN_BASAH'] + ERA_COLS:
    within = master.groupby('YEAR_fitur')[c].transform(lambda s: s - s.mean())
    rows.append({
        'Fitur': c,
        'Rata2 NASA': round(cmp[c + '_NASA'].mean(), 2), 'Rata2 Baru': round(cmp[c + '_ERA'].mean(), 2),
        'Korelasi NASA vs Baru': round(cmp[c + '_NASA'].corr(cmp[c + '_ERA']), 3),
        'Nilai unik/tahun (min-maks)': f"{master.groupby('YEAR_fitur')[c].nunique().min()}-"
                                       f"{master.groupby('YEAR_fitur')[c].nunique().max()}",
        'Porsi variasi antar-kecamatan': round(within.var() / master[c].var(), 3),
    })
print(pd.DataFrame(rows).to_string(index=False))
