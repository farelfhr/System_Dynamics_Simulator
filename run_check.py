"""Readiness checks for the System Dynamics simulator project."""

from pathlib import Path

import pandas as pd

from src.simulator_utils import validate_required_columns, validate_required_parameters


PROJECT_ROOT = Path(__file__).resolve().parent

REQUIRED_FOLDERS = [
    "01_data/raw",
    "01_data/processed",
    "01_data/parameters",
    "02_notebooks",
    "03_outputs/figures",
    "03_outputs/tables",
    "04_paper_figures",
    "05_docs",
    "src",
]

BASELINE_COLUMNS = ["parameter", "value", "unit", "description"]
RISK_COLUMNS = ["parameter", "value", "unit", "description"]
SCENARIO_COLUMNS = [
    "scenario",
    "description",
    "waste_growth_rate_per_year",
    "treatment_improvement_rate",
    "diversion_improvement_rate",
    "residual_restriction_rate",
]

BASELINE_PARAMETERS = [
    "initial_incoming_waste_tpd",
    "initial_treatment_capacity_tpd",
    "initial_residual_waste_tpd",
    "initial_diverted_waste_tpd",
    "organic_waste_tpd",
    "inorganic_waste_tpd",
    "initial_accumulated_waste_ton",
    "total_landfill_capacity_ton",
    "remaining_capacity_ton",
    "waste_pile_height_m",
    "time_step_day",
    "simulation_horizon_year",
]

RISK_PARAMETERS = [
    "risk_index_arithmetic",
    "risk_index_geometric",
    "risk_category",
    "bod",
    "cod",
    "tss",
    "ph",
    "capacity_operational_load_weight",
    "waste_characteristics_weight",
    "leachate_quality_weight",
]

SCENARIOS = [
    "S0_BAU",
    "S1_Increased_Waste_Generation",
    "S2_Improved_Organic_Treatment",
    "S3_Residual_Waste_Restriction",
    "S4_Combined_Intervention",
]

REQUIRED_CSVS = {
    "baseline_parameters.csv": {
        "path": PROJECT_ROOT / "01_data/parameters/baseline_parameters.csv",
        "columns": BASELINE_COLUMNS,
        "required_values": BASELINE_PARAMETERS,
        "value_column": "parameter",
    },
    "risk_parameters.csv": {
        "path": PROJECT_ROOT / "01_data/parameters/risk_parameters.csv",
        "columns": RISK_COLUMNS,
        "required_values": RISK_PARAMETERS,
        "value_column": "parameter",
    },
    "scenario_parameters.csv": {
        "path": PROJECT_ROOT / "01_data/parameters/scenario_parameters.csv",
        "columns": SCENARIO_COLUMNS,
        "required_values": SCENARIOS,
        "value_column": "scenario",
    },
}


def main() -> int:
    errors: list[str] = []

    for folder in REQUIRED_FOLDERS:
        path = PROJECT_ROOT / folder
        if not path.exists():
            errors.append(f"Missing required folder: {folder}")

    for filename, config in REQUIRED_CSVS.items():
        path = config["path"]
        if not path.exists():
            errors.append(f"Missing required CSV file: {path.relative_to(PROJECT_ROOT)}")
            continue

        try:
            data = pd.read_csv(path)
            validate_required_columns(data, config["columns"], filename)
            validate_required_parameters(
                data,
                config["required_values"],
                parameter_column=config["value_column"],
                file_label=filename,
            )
        except Exception as exc:
            errors.append(f"{filename}: {exc}")

    if errors:
        print("Project readiness check failed.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Project ready: all required folders, input CSV files, and schemas are valid.")
    print("Next step: open 02_notebooks/System_Dynamics_Simulator.ipynb and run all cells.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

