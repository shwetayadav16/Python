from __future__ import annotations

import json
from pathlib import Path

from workforce.analytics import AnalyticsEngine
from workforce.database import DatabaseManager
from workforce.models import Employee
from workforce.reporting import ReportGenerator


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "workforce.db"
OUTPUT_DIR = BASE_DIR / "outputs"


def sample_employees() -> list[Employee]:
    return [
        Employee("Aarav Mehta", "Engineering", "Backend Developer", 92000, 5.0, 4.5, 96.2),
        Employee("Priya Nair", "Engineering", "Data Engineer", 98000, 6.0, 4.7, 94.5),
        Employee("Rohan Das", "Engineering", "QA Lead", 86000, 7.0, 4.1, 91.3),
        Employee("Neha Kapoor", "Human Resources", "HR Manager", 72000, 8.0, 4.4, 97.0),
        Employee("Kunal Singh", "Human Resources", "Recruiter", 54000, 3.0, 3.9, 93.1),
        Employee("Sara Ali", "Finance", "Financial Analyst", 81000, 5.0, 4.3, 95.2),
        Employee("Vikram Jain", "Finance", "Accountant", 69000, 4.0, 4.0, 92.8),
        Employee("Ishita Roy", "Sales", "Sales Executive", 64000, 3.0, 4.6, 89.6),
        Employee("Manav Gupta", "Sales", "Regional Manager", 93000, 9.0, 4.8, 90.4),
        Employee("Pooja Sharma", "Operations", "Operations Analyst", 70000, 4.0, 4.2, 94.0),
        Employee("Dev Patel", "Operations", "Process Lead", 78000, 6.0, 4.1, 95.8),
        Employee("Ananya Bose", "Marketing", "SEO Specialist", 61000, 3.0, 4.0, 96.5),
        Employee("Kabir Verma", "Marketing", "Brand Strategist", 76000, 6.0, 4.4, 92.1),
        Employee("Meera Iyer", "Support", "Customer Success Lead", 65000, 5.0, 4.2, 97.4),
        Employee("Aditya Rao", "Support", "Support Engineer", 56000, 2.0, 3.8, 93.7),
    ]


def initialize_database(database: DatabaseManager) -> None:
    database.create_table()
    if database.employee_count() == 0:
        database.bulk_insert(sample_employees())


def demonstrate_crud(database: DatabaseManager) -> None:
    temp_id = database.add_employee(
        Employee("Temp Employee", "Engineering", "Intern", 35000, 1.0, 3.5, 88.0)
    )
    database.update_employee_salary(temp_id, 38000)
    database.delete_employee(temp_id)


def save_analysis_summary(department_summary, filtered_view, numpy_summary: dict[str, object]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    summary_path = OUTPUT_DIR / "analysis_summary.json"
    payload = {
        "department_salary_analysis": department_summary.to_dict(orient="records"),
        "top_performers": filtered_view.to_dict(orient="records"),
        "numpy_statistics": numpy_summary,
    }
    summary_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return summary_path


def build_project_artifacts() -> dict[str, object]:
    database = DatabaseManager(DB_PATH)
    initialize_database(database)
    analytics = AnalyticsEngine(DB_PATH)
    dataframe = analytics.load_dataframe()
    department_summary = analytics.department_salary_analysis(dataframe)
    filtered_view = analytics.filtered_and_sorted_view(dataframe)
    numpy_summary = analytics.numpy_statistics(dataframe)
    reporter = ReportGenerator(OUTPUT_DIR)
    chart_files = reporter.generate_visualizations(dataframe)
    summary_file = save_analysis_summary(department_summary, filtered_view, numpy_summary)
    return {
        "database": database,
        "dataframe": dataframe,
        "department_summary": department_summary,
        "filtered_view": filtered_view,
        "numpy_summary": numpy_summary,
        "chart_files": chart_files,
        "summary_file": summary_file,
    }


def main() -> None:
    artifacts = build_project_artifacts()
    database: DatabaseManager = artifacts["database"]
    demonstrate_crud(database)
    artifacts = build_project_artifacts()
    print("Smart Workforce Analytics & Management System")
    print(f"Database: {DB_PATH}")
    print(f"Employees loaded: {len(artifacts['dataframe'])}")
    print("Generated charts:")
    for chart in artifacts["chart_files"]:
        print(f" - {chart.name}")
    print(f"Analysis summary: {artifacts['summary_file'].name}")


if __name__ == "__main__":
    main()
