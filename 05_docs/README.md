# System Dynamics Simulator

This project provides a Python and Google Colab-compatible System Dynamics simulator for Net Landfill Load forecasting at Butus Landfill. It supports operational scenario comparison, overload tracking, and one-at-a-time sensitivity analysis for policy and planning interpretation.

## Folder Structure

- `01_data/raw/`: source Excel files from the Fuzzy AHP and landfill data workflow.
- `01_data/parameters/`: required model input CSV files.
- `01_data/processed/`: reserved for processed intermediate datasets.
- `02_notebooks/`: executable simulator notebook.
- `03_outputs/figures/`: generated PNG figures.
- `03_outputs/tables/`: generated CSV and Excel result tables.
- `04_paper_figures/`: placeholders for manuscript figure development.
- `05_docs/`: documentation and model assumptions.
- `src/`: reusable Python simulator functions.

## Required Input Files

The simulator expects these CSV files in `01_data/parameters/`:

- `baseline_parameters.csv`
- `risk_parameters.csv`
- `scenario_parameters.csv`

The raw Excel files in `01_data/raw/` are preserved as source data and are not overwritten by the simulator.

## Running in Google Colab

1. Upload the full `System_Dynamics_Simulator` folder to Colab or Google Drive.
2. Open `02_notebooks/System_Dynamics_Simulator.ipynb`.
3. Run the cells from top to bottom.
4. Confirm that the CSV files remain in `01_data/parameters/`.

The notebook uses relative paths through `pathlib.Path` and can also be run in local Jupyter.

## Expected Outputs

The notebook exports result tables to `03_outputs/tables/`:

- `simulation_daily_results.csv`
- `scenario_summary.csv`
- `scenario_settings.csv`
- `baseline_parameters_checked.csv`
- `risk_parameters_checked.csv`
- `sensitivity_analysis.csv`
- `sensitivity_summary.csv`
- `system_dynamics_simulation_results.xlsx`

It exports paper-ready PNG figures to `03_outputs/figures/`.

## Scenario Meaning

- `S0_BAU`: current conditions without additional intervention.
- `S1_Increased_Waste_Generation`: higher waste generation due to growth.
- `S2_Improved_Organic_Treatment`: improved treatment capacity.
- `S3_Residual_Waste_Restriction`: policy restriction on residual waste disposal.
- `S4_Combined_Intervention`: combined growth, treatment, diversion, and residual restriction assumptions.

## Main Output Variables

- Residual Waste: incoming waste minus treated and diverted waste.
- Net Landfill Load: residual waste after residual restriction adjustment.
- Accumulated Waste: the landfill stock updated each day by Net Landfill Load.
- Remaining Capacity: total capacity minus accumulated waste.
- Overload Accumulation: excess accumulated waste beyond remaining capacity.
- Time to Overload: estimated years until overload under the simulated average Net Landfill Load.

