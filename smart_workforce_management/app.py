from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from main import DB_PATH, OUTPUT_DIR, build_project_artifacts
from workforce.database import DatabaseManager
from workforce.models import Employee


app = Flask(__name__)


def currency(value: float) -> str:
    return f"Rs. {value:,.0f}"


app.jinja_env.filters["currency"] = currency


def refresh_artifacts() -> dict[str, object]:
    return build_project_artifacts()


def dashboard_context() -> dict[str, object]:
    artifacts = refresh_artifacts()
    dataframe = artifacts["dataframe"]
    department_summary = artifacts["department_summary"]
    filtered_view = artifacts["filtered_view"]
    numpy_summary = artifacts["numpy_summary"]
    database: DatabaseManager = artifacts["database"]
    top_employee = (
        dataframe.sort_values(by=["performance_score", "salary"], ascending=[False, False])
        .iloc[0]
        .to_dict()
    )
    chart_names = [Path(chart).name for chart in artifacts["chart_files"]]
    return {
        "employees": database.get_all_employees(),
        "department_summary": department_summary.to_dict(orient="records"),
        "top_performers": filtered_view.head(8).to_dict(orient="records"),
        "numpy_summary": numpy_summary,
        "chart_names": chart_names,
        "metrics": {
            "employee_count": int(len(dataframe)),
            "average_salary": float(numpy_summary["mean_salary"]),
            "median_salary": float(numpy_summary["median_salary"]),
            "avg_attendance": float(dataframe["attendance_rate"].mean()),
            "top_employee": top_employee,
        },
    }


@app.route("/")
def dashboard():
    return render_template("dashboard.html", **dashboard_context())


@app.get("/charts/<path:filename>")
def chart_file(filename: str):
    return send_from_directory(OUTPUT_DIR, filename)


@app.post("/employees")
def add_employee():
    database = DatabaseManager(DB_PATH)
    employee = Employee(
        name=request.form["name"].strip(),
        department=request.form["department"].strip(),
        role=request.form["role"].strip(),
        salary=float(request.form["salary"]),
        experience_years=float(request.form["experience_years"]),
        performance_score=float(request.form["performance_score"]),
        attendance_rate=float(request.form["attendance_rate"]),
    )
    database.add_employee(employee)
    refresh_artifacts()
    return redirect(url_for("dashboard"))


@app.post("/employees/<int:employee_id>/salary")
def update_salary(employee_id: int):
    database = DatabaseManager(DB_PATH)
    database.update_employee_salary(employee_id, float(request.form["salary"]))
    refresh_artifacts()
    return redirect(url_for("dashboard"))


@app.post("/employees/<int:employee_id>/delete")
def delete_employee(employee_id: int):
    database = DatabaseManager(DB_PATH)
    database.delete_employee(employee_id)
    refresh_artifacts()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    refresh_artifacts()
    app.run(debug=True)

