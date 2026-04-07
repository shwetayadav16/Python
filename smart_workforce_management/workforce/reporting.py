from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


class ReportGenerator:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_visualizations(self, dataframe: pd.DataFrame) -> list[Path]:
        return [
            self._salary_by_department(dataframe),
            self._salary_vs_performance(dataframe),
            self._salary_distribution(dataframe),
            self._department_workforce_share(dataframe),
        ]

    def _salary_by_department(self, dataframe: pd.DataFrame) -> Path:
        chart_path = self.output_dir / "salary_by_department.png"
        averages = dataframe.groupby("department")["salary"].mean().sort_values()
        plt.figure(figsize=(9, 5))
        averages.plot(kind="bar", color="#2f6690")
        plt.title("Average Salary by Department")
        plt.xlabel("Department")
        plt.ylabel("Average Salary")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def _salary_vs_performance(self, dataframe: pd.DataFrame) -> Path:
        chart_path = self.output_dir / "salary_vs_performance.png"
        plt.figure(figsize=(8, 5))
        plt.scatter(
            dataframe["performance_score"],
            dataframe["salary"],
            c=dataframe["experience_years"],
            cmap="viridis",
            s=90,
            edgecolors="black",
        )
        plt.title("Salary vs Performance Score")
        plt.xlabel("Performance Score")
        plt.ylabel("Salary")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def _salary_distribution(self, dataframe: pd.DataFrame) -> Path:
        chart_path = self.output_dir / "salary_distribution.png"
        plt.figure(figsize=(8, 5))
        plt.hist(dataframe["salary"], bins=6, color="#d17a22", edgecolor="black")
        plt.title("Salary Distribution")
        plt.xlabel("Salary")
        plt.ylabel("Employees")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

    def _department_workforce_share(self, dataframe: pd.DataFrame) -> Path:
        chart_path = self.output_dir / "department_workforce_share.png"
        shares = dataframe["department"].value_counts()
        plt.figure(figsize=(7, 7))
        plt.pie(shares, labels=shares.index, autopct="%1.1f%%", startangle=140)
        plt.title("Department Workforce Share")
        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close()
        return chart_path

