# Agroclimatic Feature Engineering for Forecasting Paddy Productivity: Wet-Month Indicators, Temporal Windows, and Benchmark Evaluation

Official source code, datasets, and reproducibility materials for the paper:

> **Agroclimatic Feature Engineering for Forecasting Paddy Productivity: Wet-Month Indicators, Temporal Windows, and Benchmark Evaluation**  
> Abdee Alamsyah Noer Siyam, Rona Nisa Sofia Amriza, Nicolas Euclides Wahyu Nugroho  
> Faculty of Informatics, Telkom University Purwokerto, Indonesia

---

## Repository Structure

Each experiment folder is **self-contained** (all paths inside notebooks and scripts are relative to their own folder):

```text
.
├── Eksperimen_XGB_Lag/             # Main experiments (NASA POWER + BPS, Tables IV–VIII, SHAP, 2025 Projection & Fig. 1–2)
│   ├── Eksperimen_XGB_Lag.ipynb    # Primary notebook reproducing all main paper results
│   ├── buat_alur_penelitian.py     # Script generating the research workflow diagram (Fig. 1)
│   ├── Dataset_Master_TA_Padi_Spatial.csv
│   ├── Curah-hujan.csv
│   ├── ADMINISTRASIDESA_AR_25K.*   # Banyumas subdistrict boundary shapefile (Ina-Geoportal)
│   ├── Eksp10_*.csv, Eksp11_*.csv, Eksp12_*.csv
│   ├── Prediksi_Produksi_Banyumas_2025_XGB_Lag.csv
│   └── *.png                       # Generated figures (SHAP, feature importance, 2025 map, etc.)
│
├── Eksperimen_ERA5Land_CHIRPS/     # Climate robustness check using CHIRPS + ERA5-Land + ERA5
│   ├── Eksperimen_ERA5Land_CHIRPS.ipynb
│   ├── ambil_era5land.py           # Fetch ERA5-Land / ERA5 data via Open-Meteo Historical API
│   ├── siapkan_data_era5land.py    # Prepare merged dataset with ERA5-Land + CHIRPS
│   ├── Dataset_Master_TA_Padi_Spatial.csv
│   ├── ERA5_Harian_Kecamatan.csv
│   ├── CHIRPS_Bulanan_Kecamatan.csv
│   └── ...
│
├── Eksperimen_CHIRPS/              # Climate robustness check using CHIRPS rainfall + NASA POWER
│   ├── Eksperimen_CHIRPS.ipynb
│   ├── ekstrak_chirps.py           # Extract CHIRPS v2.0 monthly rainfall COGs per subdistrict
│   ├── siapkan_data_chirps.py      # Prepare merged dataset with CHIRPS rainfall
│   ├── Dataset_Master_TA_Padi_Spatial.csv
│   ├── CHIRPS_Bulanan_Kecamatan.csv
│   └── ...
│
├── requirements.txt
└── README.md
```

---

## Quick Start (How to Run)

### 1. Clone the Repository

```bash
git clone https://github.com/abdeeal/agroclimatic-paddy-forecasting-banyumas.git
cd agroclimatic-paddy-forecasting-banyumas
```

### 2. Create a Python Environment & Install Dependencies

Tested on **Python 3.12.5**:

```bash
python -m venv .venv
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Main Paper Notebook

Open Jupyter inside `Eksperimen_XGB_Lag/` (important so relative paths resolve to the folder):

```bash
cd Eksperimen_XGB_Lag
jupyter notebook Eksperimen_XGB_Lag.ipynb
```

Or execute headlessly via `nbconvert`:

```bash
cd Eksperimen_XGB_Lag
jupyter nbconvert --to notebook --execute --inplace Eksperimen_XGB_Lag.ipynb
```

To regenerate Fig. 1 (workflow diagram):

```bash
cd Eksperimen_XGB_Lag
python buat_alur_penelitian.py
```

### 4. Run Climate Source Robustness Checks (Optional)

Pre-downloaded climate datasets (`CHIRPS_Bulanan_Kecamatan.csv`, `ERA5_Harian_Kecamatan.csv`, `Dataset_Master_TA_Padi_Spatial.csv`) are already included in each folder, so you can run the notebooks directly without re-downloading climate archives:

```bash
cd Eksperimen_ERA5Land_CHIRPS
jupyter notebook Eksperimen_ERA5Land_CHIRPS.ipynb
```

```bash
cd Eksperimen_CHIRPS
jupyter notebook Eksperimen_CHIRPS.ipynb
```

If you want to re-fetch the raw CHIRPS or ERA5-Land data from public sources (`data.chc.ucsb.edu` and `archive-api.open-meteo.com`), run `ekstrak_chirps.py` / `siapkan_data_chirps.py` or `ambil_era5land.py` / `siapkan_data_era5land.py` inside their respective folders.

---

## Mapping Paper Results to Code Outputs

| Paper Section / Table | Source File / Experiment | Key Verified Result |
|---|---|---|
| Table IV (Benchmarks on SW-5) | `Eksperimen_XGB_Lag.ipynb` (Eksp 11) / `Eksp11_perbandingan_model.csv` | XGBoost + lag: R² `0.738`, RMSE `0.200` t/ha, MAE `0.138`, MAPE `2.41%` (vs Persistence `0.734`) |
| Table V (Temporal Scenarios) | `Eksperimen_XGB_Lag.ipynb` (Eksp 10) / `Eksp10_model_utama_per_skenario.csv` | SW-5 `0.738`, SW-6 `0.733`, SW-7 `0.725`, SW-8 `0.964`, EW-7 `0.716`, EW-8 `0.954`, EW-9 `0.956` |
| Table VI (R² by Target Year) | `Eksperimen_XGB_Lag.ipynb` (Eksp 10) / `Eksp10_r2_per_tahun.csv` | Target years 2020–2024 |
| Table VII (10-Seed Wet-Month Ablation) | `Eksperimen_XGB_Lag.ipynb` (Eksp 10) / `Eksp10_multiseed_nested.csv` | SW-5: `0.737 ± 0.004` vs `0.700 ± 0.003` (ΔR² `0.037`, 10/10 seeds) |
| Table VIII (Oldeman Wet-Month Variants) | `Eksperimen_XGB_Lag.ipynb` (Eksp 12) / `Eksp12_varian_bulan_basah.csv` | None `0.703`, Annual count `0.738`, Run calendar `0.664`, Run season `0.681`, Count + run `0.754` |
| Out-of-sample SHAP Contributions | `Eksperimen_XGB_Lag.ipynb` (Eksp 7) | Previous-year productivity `57.0%`, Agroclimatic `36.5%`, Subdistrict `2.4%` |
| 2025 Projection & Map (Fig. 2) | `Eksperimen_XGB_Lag.ipynb` (Eksp 8) / `Prediksi_Produksi_Banyumas_2025_XGB_Lag.csv` | ~`332,000 t` (95% interval: `303,000–360,000 t`) |
| CHIRPS + ERA5-Land Comparison | `Eksperimen_ERA5Land_CHIRPS.ipynb` (Eksp 6) | SW-5 XGB + lag (nested): R² `0.684` (`0.6844`) |
