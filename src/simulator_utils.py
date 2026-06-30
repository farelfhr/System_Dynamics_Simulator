"""Utility functions for Net Landfill Load System Dynamics simulation."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import numpy as np
import pandas as pd


DEFAULT_SENSITIVITY_GRID = {
    "waste_growth_rate_per_year": [-0.10, 0.00, 0.10, 0.20],
    "treatment_improvement_rate": [-0.20, -0.10, 0.00, 0.10, 0.20, 0.30],
    "diversion_improvement_rate": [-0.20, -0.10, 0.00, 0.10, 0.20, 0.30],
    "residual_restriction_rate": [0.00, 0.10, 0.20, 0.30, 0.40],
}


def _coerce_number(value: Any) -> Any:
    """Convert numeric-looking values while preserving labels such as risk categories."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip()
    try:
        return float(text)
    except ValueError:
        return text


def _as_mapping(row: Mapping[str, Any] | pd.Series) -> dict[str, Any]:
    if isinstance(row, pd.Series):
        return row.to_dict()
    return dict(row)


def _required_float(values: Mapping[str, Any], key: str) -> float:
    if key not in values:
        raise KeyError(f"Missing required parameter: {key}")
    value = _coerce_number(values[key])
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Parameter '{key}' must be numeric, got {values[key]!r}") from exc
    if np.isnan(number):
        raise ValueError(f"Parameter '{key}' must not be blank")
    return number


def _optional_float(values: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    if key not in values or pd.isna(values[key]):
        return default
    value = _coerce_number(values[key])
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Scenario setting '{key}' must be numeric, got {values[key]!r}") from exc


def load_parameter_csv(
    path: str | Path,
    required_columns: Iterable[str] | None = None,
    required_parameters: Iterable[str] | None = None,
    parameter_column: str = "parameter",
    file_label: str | None = None,
) -> pd.DataFrame:
    """Load a CSV file and optionally validate its columns and required keys."""
    csv_path = Path(path)
    label = file_label or str(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing required CSV file: {csv_path}")

    data = pd.read_csv(csv_path)
    if required_columns is not None:
        validate_required_columns(data, required_columns, label)
    if required_parameters is not None:
        validate_required_parameters(data, required_parameters, parameter_column, label)
    return data


def validate_required_columns(
    data: pd.DataFrame,
    required_columns: Iterable[str],
    file_label: str = "input data",
) -> None:
    """Raise a clear error if any required columns are absent."""
    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"{file_label} is missing required column(s): {missing_text}")


def validate_required_parameters(
    data: pd.DataFrame,
    required_parameters: Iterable[str],
    parameter_column: str = "parameter",
    file_label: str = "input data",
) -> None:
    """Raise a clear error if required parameter or scenario names are absent."""
    validate_required_columns(data, [parameter_column], file_label)
    observed = set(data[parameter_column].astype(str).str.strip())
    missing = [parameter for parameter in required_parameters if parameter not in observed]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(
            f"{file_label} is missing required {parameter_column} value(s): {missing_text}"
        )


def parameters_to_dict(
    data: pd.DataFrame,
    parameter_col: str = "parameter",
    value_col: str = "value",
) -> dict[str, Any]:
    """Convert parameter/value rows into a dictionary with numeric values parsed."""
    validate_required_columns(data, [parameter_col, value_col], "parameter table")
    result: dict[str, Any] = {}
    for _, row in data.iterrows():
        key = str(row[parameter_col]).strip()
        result[key] = _coerce_number(row[value_col])
    return result


def run_simulation(
    baseline_parameters: Mapping[str, Any],
    scenario_settings: Mapping[str, Any] | pd.Series,
    scenario_name: str | None = None,
) -> pd.DataFrame:
    """Run a daily discrete-time System Dynamics simulation for one scenario."""
    scenario = _as_mapping(scenario_settings)

    name = scenario_name or str(scenario.get("scenario", "Scenario"))
    description = str(scenario.get("description", ""))

    incoming_waste_0 = _required_float(baseline_parameters, "initial_incoming_waste_tpd")
    treatment_capacity_0 = _required_float(
        baseline_parameters, "initial_treatment_capacity_tpd"
    )
    diverted_waste_0 = _required_float(baseline_parameters, "initial_diverted_waste_tpd")
    accumulated_waste = _required_float(
        baseline_parameters, "initial_accumulated_waste_ton"
    )
    total_capacity = _required_float(baseline_parameters, "total_landfill_capacity_ton")
    time_step_day = _required_float(baseline_parameters, "time_step_day")
    horizon_year = _required_float(baseline_parameters, "simulation_horizon_year")

    if time_step_day <= 0:
        raise ValueError("time_step_day must be greater than 0")
    if horizon_year <= 0:
        raise ValueError("simulation_horizon_year must be greater than 0")

    growth_rate = _optional_float(scenario, "waste_growth_rate_per_year")
    treatment_improvement = _optional_float(scenario, "treatment_improvement_rate")
    diversion_improvement = _optional_float(scenario, "diversion_improvement_rate")
    residual_restriction = _optional_float(scenario, "residual_restriction_rate")

    if growth_rate <= -1:
        raise ValueError("waste_growth_rate_per_year must be greater than -1")

    simulation_horizon_day = int(round(horizon_year * 365))
    number_of_steps = max(1, int(round(simulation_horizon_day / time_step_day)))

    cumulative_nll = 0.0
    rows: list[dict[str, Any]] = []

    for step in range(1, number_of_steps + 1):
        day = step * time_step_day
        year = day / 365.0

        incoming_waste = max(0.0, incoming_waste_0 * ((1.0 + growth_rate) ** year))
        treated_waste = max(0.0, treatment_capacity_0 * (1.0 + treatment_improvement))
        diverted_waste = max(0.0, diverted_waste_0 * (1.0 + diversion_improvement))
        residual_waste = max(0.0, incoming_waste - treated_waste - diverted_waste)
        net_landfill_load = max(0.0, residual_waste * (1.0 - residual_restriction))

        accumulated_waste += net_landfill_load * time_step_day
        remaining_capacity = total_capacity - accumulated_waste
        overload_accumulation = max(0.0, -remaining_capacity)

        cumulative_nll += net_landfill_load
        average_nll = cumulative_nll / step
        if remaining_capacity <= 0:
            time_to_overload = 0.0
        elif average_nll <= 0:
            time_to_overload = np.inf
        else:
            time_to_overload = remaining_capacity / average_nll / 365.0

        rows.append(
            {
                "scenario": name,
                "description": description,
                "day": day,
                "year": year,
                "time_step_day": time_step_day,
                "waste_growth_rate_per_year": growth_rate,
                "treatment_improvement_rate": treatment_improvement,
                "diversion_improvement_rate": diversion_improvement,
                "residual_restriction_rate": residual_restriction,
                "incoming_waste_tpd": incoming_waste,
                "treated_waste_tpd": treated_waste,
                "diverted_waste_tpd": diverted_waste,
                "residual_waste_tpd": residual_waste,
                "net_landfill_load_tpd": net_landfill_load,
                "accumulated_waste_ton": accumulated_waste,
                "remaining_capacity_ton": remaining_capacity,
                "overload_accumulation_ton": overload_accumulation,
                "average_nll_tpd": average_nll,
                "time_to_overload_year": time_to_overload,
            }
        )

    return pd.DataFrame(rows)


def summarize_scenarios(daily_results: pd.DataFrame) -> pd.DataFrame:
    """Create one final summary row per scenario."""
    required = [
        "scenario",
        "day",
        "net_landfill_load_tpd",
        "accumulated_waste_ton",
        "remaining_capacity_ton",
        "overload_accumulation_ton",
        "time_to_overload_year",
    ]
    validate_required_columns(daily_results, required, "daily simulation results")

    summary_rows: list[dict[str, Any]] = []
    for scenario, group in daily_results.sort_values("day").groupby("scenario", sort=False):
        group = group.sort_values("day")
        final = group.iloc[-1]
        overload_rows = group[group["remaining_capacity_ton"] <= 0]
        if overload_rows.empty:
            first_overload_day = np.nan
            first_overload_year = np.nan
        else:
            first_overload_day = float(overload_rows.iloc[0]["day"])
            first_overload_year = float(overload_rows.iloc[0]["year"])

        summary_rows.append(
            {
                "scenario": scenario,
                "description": final.get("description", ""),
                "waste_growth_rate_per_year": final.get("waste_growth_rate_per_year", np.nan),
                "treatment_improvement_rate": final.get(
                    "treatment_improvement_rate", np.nan
                ),
                "diversion_improvement_rate": final.get(
                    "diversion_improvement_rate", np.nan
                ),
                "residual_restriction_rate": final.get("residual_restriction_rate", np.nan),
                "final_net_landfill_load_tpd": final["net_landfill_load_tpd"],
                "mean_net_landfill_load_tpd": group["net_landfill_load_tpd"].mean(),
                "final_accumulated_waste_ton": final["accumulated_waste_ton"],
                "final_remaining_capacity_ton": final["remaining_capacity_ton"],
                "final_overload_accumulation_ton": final["overload_accumulation_ton"],
                "final_time_to_overload_year": final["time_to_overload_year"],
                "first_overload_day": first_overload_day,
                "first_overload_year": first_overload_year,
                "total_landfill_load_ton": (
                    group["net_landfill_load_tpd"] * group["time_step_day"]
                ).sum(),
            }
        )

    return pd.DataFrame(summary_rows)


def plot_scenarios(
    daily_results: pd.DataFrame,
    y_column: str,
    title: str,
    ylabel: str,
    output_path: str | Path | None = None,
):
    """Plot scenario time series and optionally save a 300 dpi PNG."""
    import matplotlib.pyplot as plt

    validate_required_columns(
        daily_results, ["scenario", "year", y_column], "daily simulation results"
    )
    fig, ax = plt.subplots(figsize=(9, 5))
    for scenario, group in daily_results.groupby("scenario", sort=False):
        ax.plot(group["year"], group[y_column], linewidth=1.8, label=scenario)

    ax.set_title(title)
    ax.set_xlabel("Simulation year")
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
    ax.legend(fontsize=8)
    fig.tight_layout()

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300)
    return fig, ax


def plot_bar_summary(
    summary_data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    ylabel: str,
    output_path: str | Path | None = None,
):
    """Plot a bar summary and optionally save a 300 dpi PNG."""
    import matplotlib.pyplot as plt

    validate_required_columns(summary_data, [x_column, y_column], "summary data")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(summary_data[x_column].astype(str), summary_data[y_column])
    ax.set_title(title)
    ax.set_xlabel("")
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.tick_params(axis="x", labelrotation=25)
    fig.tight_layout()

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300)
    return fig, ax


def run_sensitivity_analysis(
    baseline_parameters: Mapping[str, Any],
    base_scenario: Mapping[str, Any] | pd.Series,
    sensitivity_grid: Mapping[str, Iterable[float]] | None = None,
) -> pd.DataFrame:
    """Run one-at-a-time sensitivity tests from a base scenario."""
    grid = sensitivity_grid or DEFAULT_SENSITIVITY_GRID
    base = _as_mapping(base_scenario)
    rows: list[dict[str, Any]] = []

    for tested_parameter, tested_values in grid.items():
        for tested_value in tested_values:
            scenario = dict(base)
            scenario[tested_parameter] = tested_value
            scenario["scenario"] = f"Sensitivity_{tested_parameter}_{tested_value:+.2f}"
            scenario["description"] = (
                f"One-at-a-time sensitivity test for {tested_parameter}"
            )

            result = run_simulation(baseline_parameters, scenario)
            final = result.iloc[-1]
            rows.append(
                {
                    "tested_parameter": tested_parameter,
                    "parameter_value": tested_value,
                    "final_nll_tpd": final["net_landfill_load_tpd"],
                    "final_accumulated_waste_ton": final["accumulated_waste_ton"],
                    "final_remaining_capacity_ton": final["remaining_capacity_ton"],
                    "final_overload_accumulation_ton": final["overload_accumulation_ton"],
                    "final_time_to_overload_year": final["time_to_overload_year"],
                }
            )

    return pd.DataFrame(rows)


def summarize_sensitivity(sensitivity_results: pd.DataFrame) -> pd.DataFrame:
    """Summarize sensitivity ranges for final NLL and overload accumulation."""
    required = [
        "tested_parameter",
        "final_nll_tpd",
        "final_overload_accumulation_ton",
    ]
    validate_required_columns(sensitivity_results, required, "sensitivity results")
    summary = (
        sensitivity_results.groupby("tested_parameter", as_index=False)
        .agg(
            min_final_nll_tpd=("final_nll_tpd", "min"),
            max_final_nll_tpd=("final_nll_tpd", "max"),
            min_final_overload_accumulation_ton=(
                "final_overload_accumulation_ton",
                "min",
            ),
            max_final_overload_accumulation_ton=(
                "final_overload_accumulation_ton",
                "max",
            ),
        )
        .assign(
            range_final_nll_tpd=lambda data: data["max_final_nll_tpd"]
            - data["min_final_nll_tpd"],
            range_overload_accumulation_ton=lambda data: data[
                "max_final_overload_accumulation_ton"
            ]
            - data["min_final_overload_accumulation_ton"],
        )
        .sort_values("range_overload_accumulation_ton", ascending=False)
        .reset_index(drop=True)
    )
    return summary


__all__ = [
    "DEFAULT_SENSITIVITY_GRID",
    "load_parameter_csv",
    "validate_required_columns",
    "validate_required_parameters",
    "parameters_to_dict",
    "run_simulation",
    "summarize_scenarios",
    "plot_scenarios",
    "plot_bar_summary",
    "run_sensitivity_analysis",
    "summarize_sensitivity",
]
