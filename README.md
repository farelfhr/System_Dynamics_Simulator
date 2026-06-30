# System Dynamics Simulator - Net Landfill Load Forecasting

Repository ini berisi simulator **System Dynamics** berbasis Python untuk penelitian:

**Sustainable Waste Management System Based on Integrated Risk Assessment and System Dynamics for Net Landfill Load Forecasting at Butus Landfill**

Simulator ini dibuat untuk memproyeksikan **Net Landfill Load (NLL)**, akumulasi sampah, kapasitas tersisa, dan potensi overload TPA berdasarkan beberapa skenario kebijakan. Model ini dapat dijalankan di **Google Colab**, **Jupyter Notebook**, atau lingkungan Python lokal.

## 1. Latar Belakang Awal

Project ini dimulai dari kebutuhan membangun bagian **System Dynamics** dari penelitian pengelolaan sampah berkelanjutan di Butus Landfill. Data awal yang sudah tersedia meliputi:

- Data parameter operasional landfill dalam format CSV.
- Data hasil dan template Fuzzy AHP dalam format Excel.
- Parameter risiko seperti risk index, kategori risiko, kualitas lindi, dan bobot kriteria.

File input awal yang dipertahankan:

- `01_data/parameters/baseline_parameters.csv`
- `01_data/parameters/risk_parameters.csv`
- `01_data/parameters/scenario_parameters.csv`
- `01_data/raw/fuzzy_ahp_landfill_data_template.xlsx`
- `01_data/raw/fuzzy_ahp_landfill_results.xlsx`

File Excel mentah dan CSV parameter tidak dihapus, tidak diubah nama, dan tidak ditimpa oleh proses pembuatan simulator.

## 2. Tujuan Project

Simulator ini bertujuan menghitung dan membandingkan:

- Residual Waste
- Net Landfill Load
- Accumulated Waste
- Remaining Landfill Capacity
- Overload Accumulation
- Time to Overload
- Scenario comparison
- Sensitivity analysis

Model ini bersifat **simulation-based forecasting**, bukan machine learning. Fokus utamanya adalah melihat dinamika stok dan aliran sampah berdasarkan parameter operasional serta asumsi skenario.

## 3. Progress Pekerjaan yang Sudah Dibuat

Pekerjaan yang sudah diselesaikan dalam repository ini:

- Struktur folder project sudah dibuat lengkap.
- Notebook utama simulator sudah dibuat di `02_notebooks/System_Dynamics_Simulator.ipynb`.
- Modul Python reusable sudah dibuat di `src/simulator_utils.py`.
- Script pengecekan kesiapan project sudah dibuat di `run_check.py`.
- File dependency sudah dibuat di `requirements.txt`.
- Dokumentasi model sudah dibuat di `05_docs/model_assumptions.md`.
- Output tabel simulasi sudah tersedia di `03_outputs/tables/`.
- Output figure simulasi sudah tersedia di `03_outputs/figures/`.
- Placeholder figure untuk kebutuhan paper sudah tersedia di `04_paper_figures/`.

Status validasi:

- `python run_check.py` berhasil dijalankan.
- Struktur folder dan file input CSV sudah valid.
- Simulasi menghasilkan 18,250 baris data harian untuk 5 skenario selama 10 tahun.
- Sensitivity analysis menghasilkan 21 percobaan parameter.

## 4. Struktur Folder

```text
System_Dynamics_Simulator/
|
|-- 01_data/
|   |-- raw/
|   |   |-- fuzzy_ahp_landfill_data_template.xlsx
|   |   `-- fuzzy_ahp_landfill_results.xlsx
|   |-- processed/
|   |   `-- .gitkeep
|   `-- parameters/
|       |-- baseline_parameters.csv
|       |-- risk_parameters.csv
|       `-- scenario_parameters.csv
|
|-- 02_notebooks/
|   `-- System_Dynamics_Simulator.ipynb
|
|-- 03_outputs/
|   |-- figures/
|   `-- tables/
|
|-- 04_paper_figures/
|   |-- Fig_CLD_placeholder.txt
|   |-- Fig_SFD_placeholder.txt
|   `-- Fig_Scenario_Result_placeholder.txt
|
|-- 05_docs/
|   |-- README.md
|   `-- model_assumptions.md
|
|-- src/
|   |-- __init__.py
|   `-- simulator_utils.py
|
|-- requirements.txt
|-- run_check.py
`-- README.md
```

## 5. File Input

### `baseline_parameters.csv`

Berisi parameter dasar operasional landfill, seperti:

- `initial_incoming_waste_tpd`
- `initial_treatment_capacity_tpd`
- `initial_residual_waste_tpd`
- `initial_diverted_waste_tpd`
- `initial_accumulated_waste_ton`
- `total_landfill_capacity_ton`
- `remaining_capacity_ton`
- `time_step_day`
- `simulation_horizon_year`

### `risk_parameters.csv`

Berisi parameter risiko dari pendekatan Fuzzy AHP, seperti:

- `risk_index_arithmetic`
- `risk_index_geometric`
- `risk_category`
- `bod`
- `cod`
- `tss`
- `ph`
- Bobot kriteria risiko

Parameter risiko digunakan sebagai **lapisan interpretasi dan pendukung keputusan**, bukan sebagai persamaan utama Net Landfill Load.

### `scenario_parameters.csv`

Berisi lima skenario simulasi:

| Scenario | Arti |
|---|---|
| `S0_BAU` | Kondisi saat ini tanpa intervensi tambahan |
| `S1_Increased_Waste_Generation` | Peningkatan timbulan sampah |
| `S2_Improved_Organic_Treatment` | Peningkatan kapasitas atau efektivitas pengolahan |
| `S3_Residual_Waste_Restriction` | Pembatasan sampah residu yang masuk landfill |
| `S4_Combined_Intervention` | Kombinasi pertumbuhan, pengolahan, diversion, dan pembatasan residu |

## 6. Ringkasan Model

Model menggunakan timestep harian. Horizon simulasi dibaca dari parameter `simulation_horizon_year`, lalu dikonversi menjadi hari.

Persamaan utama:

```text
Residual Waste:
RW(t) = IW(t) - TW(t) - DW(t)

Net Landfill Load:
NLL(t) = RW(t)

Accumulated Waste:
AW(t) = AW(t-1) + NLL(t) x delta_t

Remaining Capacity:
RC(t) = TC - AW(t)

Overload Accumulation:
Overload(t) = max(0, -RC(t))

Time to Overload:
TTO(t) = RC(t) / Average NLL
```

Aturan penting dalam model:

- Residual Waste tidak boleh negatif.
- Net Landfill Load tidak boleh negatif.
- Jika Remaining Capacity sudah 0 atau negatif, Time to Overload diset menjadi 0.
- Jika landfill sudah overload, tambahan overload tetap dihitung dari waktu ke waktu.

## 7. Cara Menjalankan Project

### Menjalankan di lokal

Buka terminal dari folder project:

```powershell
cd D:\Dev\UTHM\System_Dynamics_Simulator
```

Install dependency:

```powershell
python -m pip install -r requirements.txt
```

Jalankan pengecekan project:

```powershell
python run_check.py
```

Jika berhasil, akan muncul pesan:

```text
Project ready: all required folders, input CSV files, and schemas are valid.
```

Setelah itu buka notebook:

```text
02_notebooks/System_Dynamics_Simulator.ipynb
```

Lalu jalankan semua cell dari atas ke bawah.

### Menjalankan di Google Colab

1. Upload seluruh folder `System_Dynamics_Simulator` ke Google Drive.
2. Buka `02_notebooks/System_Dynamics_Simulator.ipynb` di Colab.
3. Mount Google Drive.
4. Arahkan working directory ke folder project.
5. Jalankan semua cell.

Contoh:

```python
from google.colab import drive
drive.mount('/content/drive')

%cd /content/drive/MyDrive/System_Dynamics_Simulator
```

## 8. Output Tabel

Output tabel disimpan di `03_outputs/tables/`.

| File | Isi |
|---|---|
| `simulation_daily_results.csv` | Hasil simulasi harian semua skenario |
| `scenario_summary.csv` | Ringkasan akhir tiap skenario |
| `scenario_settings.csv` | Salinan konfigurasi skenario yang digunakan |
| `baseline_parameters_checked.csv` | Parameter baseline yang sudah divalidasi |
| `risk_parameters_checked.csv` | Parameter risiko yang sudah divalidasi |
| `sensitivity_analysis.csv` | Hasil lengkap sensitivity analysis |
| `sensitivity_summary.csv` | Ringkasan pengaruh parameter sensitivity |
| `system_dynamics_simulation_results.xlsx` | Workbook Excel berisi semua sheet hasil utama |

Workbook Excel memuat sheet:

- `baseline_parameters`
- `risk_parameters`
- `scenario_settings`
- `daily_results`
- `scenario_summary`
- `sensitivity_analysis`
- `sensitivity_summary`

## 9. Output Figure

Output figure disimpan di `03_outputs/figures/` dalam format PNG 300 dpi.

| File | Isi |
|---|---|
| `fig_nll_forecast.png` | Proyeksi Net Landfill Load |
| `fig_accumulated_waste_projection.png` | Proyeksi akumulasi sampah |
| `fig_remaining_capacity_projection.png` | Proyeksi kapasitas tersisa |
| `fig_overload_accumulation_projection.png` | Proyeksi overload accumulation |
| `fig_final_nll_by_scenario.png` | Perbandingan final NLL tiap skenario |
| `fig_final_overload_by_scenario.png` | Perbandingan final overload tiap skenario |
| `fig_sensitivity_overload_range.png` | Pengaruh parameter terhadap overload |

## 10. Ringkasan Hasil Simulasi

Berdasarkan output `scenario_summary.csv`, simulasi 10 tahun menghasilkan ringkasan berikut.

| Scenario | Final NLL (ton/day) | Final Accumulated Waste (ton) | Final Overload (ton) |
|---|---:|---:|---:|
| `S0_BAU` | 13.00 | 468,450.00 | 47,450.00 |
| `S1_Increased_Waste_Generation` | 59.22 | 539,621.66 | 118,621.66 |
| `S2_Improved_Organic_Treatment` | 10.00 | 457,500.00 | 36,500.00 |
| `S3_Residual_Waste_Restriction` | 10.40 | 458,960.00 | 37,960.00 |
| `S4_Combined_Intervention` | 44.89 | 506,845.33 | 85,845.33 |

Interpretasi awal:

- Kondisi baseline menunjukkan landfill sudah berada pada kondisi overload karena kapasitas tersisa awal bernilai 0 ton.
- `S2_Improved_Organic_Treatment` menghasilkan final overload paling rendah dalam hasil simulasi saat ini.
- `S1_Increased_Waste_Generation` menghasilkan final overload paling tinggi karena pertumbuhan sampah meningkatkan beban landfill secara signifikan.
- `S4_Combined_Intervention` tetap memiliki overload tinggi karena skenario ini juga memasukkan pertumbuhan timbulan sampah sebesar 10 persen per tahun.

## 11. Ringkasan Sensitivity Analysis

Sensitivity analysis dilakukan terhadap:

- `waste_growth_rate_per_year`
- `treatment_improvement_rate`
- `diversion_improvement_rate`
- `residual_restriction_rate`

Ringkasan pengaruh terhadap final overload accumulation:

| Parameter | Range Final Overload (ton) |
|---|---:|
| `waste_growth_rate_per_year` | 231,025.23 |
| `treatment_improvement_rate` | 27,375.00 |
| `residual_restriction_rate` | 18,980.00 |
| `diversion_improvement_rate` | 1,825.00 |

Interpretasi sensitivity:

- Parameter paling sensitif adalah `waste_growth_rate_per_year`.
- Pengendalian pertumbuhan timbulan sampah menjadi faktor paling penting untuk menekan overload jangka panjang.
- Peningkatan pengolahan dan pembatasan residu juga membantu menurunkan overload, tetapi pengaruhnya lebih kecil dibanding pertumbuhan timbulan sampah.

## 12. File Kode Utama

### `src/simulator_utils.py`

Berisi fungsi reusable:

- `load_parameter_csv()`
- `validate_required_columns()`
- `validate_required_parameters()`
- `parameters_to_dict()`
- `run_simulation()`
- `summarize_scenarios()`
- `plot_scenarios()`
- `plot_bar_summary()`
- `run_sensitivity_analysis()`
- `summarize_sensitivity()`

### `run_check.py`

Digunakan untuk mengecek:

- Folder wajib tersedia.
- CSV parameter tersedia.
- Kolom CSV sesuai kebutuhan.
- Parameter dan scenario wajib tersedia.

### `02_notebooks/System_Dynamics_Simulator.ipynb`

Notebook utama untuk:

- Load data.
- Validasi input.
- Menjalankan semua skenario.
- Membuat summary table.
- Export CSV dan Excel.
- Membuat grafik.
- Menjalankan sensitivity analysis.
- Membuat teks bantu interpretasi hasil.

## 13. Catatan Asumsi

Ringkasan asumsi model:

- Model menggunakan timestep harian.
- Forecasting berbasis simulasi, bukan machine learning.
- Residual waste dihitung dari incoming waste, treated waste, dan diverted waste.
- Net Landfill Load adalah residual waste setelah penyesuaian residual restriction.
- Accumulated waste adalah stock utama.
- Remaining capacity adalah total landfill capacity dikurangi accumulated waste.
- Overload accumulation penting karena landfill dilaporkan sudah overloaded.
- Fuzzy AHP risk index digunakan sebagai lapisan interpretasi risiko.
- Skenario merupakan asumsi kebijakan yang dapat disesuaikan setelah validasi tim.

Detail asumsi tersedia di:

```text
05_docs/model_assumptions.md
```

## 14. Cara Membaca Hasil

Untuk analisis cepat:

1. Buka `03_outputs/tables/scenario_summary.csv`.
2. Bandingkan `final_net_landfill_load_tpd`.
3. Bandingkan `final_overload_accumulation_ton`.
4. Buka `03_outputs/tables/sensitivity_summary.csv`.
5. Lihat parameter dengan `range_overload_accumulation_ton` terbesar.
6. Gunakan figure di `03_outputs/figures/` untuk visualisasi paper atau presentasi.

## 15. Kesimpulan Sementara Project

Project ini sudah menyediakan workflow lengkap dari input parameter, validasi, simulasi System Dynamics, scenario comparison, sensitivity analysis, sampai export output untuk kebutuhan penelitian. Hasil awal menunjukkan bahwa pengendalian pertumbuhan timbulan sampah dan peningkatan pengolahan merupakan faktor penting dalam menekan Net Landfill Load dan overload accumulation.

