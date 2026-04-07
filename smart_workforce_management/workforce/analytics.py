from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


class AnalyticsEngine:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def load_dataframe(self) -> pd.DataFrame:
        with sqlite3.connect(self.db_path) as connection:
            return pd.read_sql_query("SELECT * FROM employees", connection)

    def department_salary_analysis(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        summary = (
            dataframe.groupby("department", as_index=False)["salary"]
            .agg(["mean", "min", "max", "count"])
            .reset_index()
        )
        return summary.rename(
            columns={
                "mean": "average_salary",
                "min": "minimum_salary",
                "max": "maximum_salary",
                "count": "employee_count",
            }
        )

    def filtered_and_sorted_view(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        filtered = dataframe[dataframe["performance_score"] >= 4.0]
        return filtered.sort_values(by=["department", "salary"], ascending=[True, False])

    def numpy_statistics(self, dataframe: pd.DataFrame) -> dict[str, object]:
        salary = dataframe["salary"].to_numpy(dtype=float)
        performance = dataframe["performance_score"].to_numpy(dtype=float)
        attendance = dataframe["attendance_rate"].to_numpy(dtype=float)
        normalized_salary = (salary - salary.min()) / (salary.max() - salary.min())
        correlation_matrix = np.corrcoef(np.vstack([salary, performance, attendance])).round(3)
        return {
            "mean_salary": float(np.mean(salary)),
            "median_salary": float(np.median(salary)),
            "salary_std_dev": float(np.std(salary)),
            "normalized_salary": normalized_salary.round(3).tolist(),
            "correlation_matrix": correlation_matrix.tolist(),
        }
