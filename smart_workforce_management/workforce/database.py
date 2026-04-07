from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from workforce.models import Employee


class DatabaseManager:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_table(self) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    department TEXT NOT NULL,
                    role TEXT NOT NULL,
                    salary REAL NOT NULL,
                    experience_years REAL NOT NULL,
                    performance_score REAL NOT NULL,
                    attendance_rate REAL NOT NULL
                )
                """
            )
            connection.commit()

    def add_employee(self, employee: Employee) -> int:
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO employees (
                    name,
                    department,
                    role,
                    salary,
                    experience_years,
                    performance_score,
                    attendance_rate
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    employee.name,
                    employee.department,
                    employee.role,
                    employee.salary,
                    employee.experience_years,
                    employee.performance_score,
                    employee.attendance_rate,
                ),
            )
            connection.commit()
            return int(cursor.lastrowid)

    def bulk_insert(self, employees: Iterable[Employee]) -> None:
        with self.connect() as connection:
            connection.executemany(
                """
                INSERT INTO employees (
                    name,
                    department,
                    role,
                    salary,
                    experience_years,
                    performance_score,
                    attendance_rate
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        employee.name,
                        employee.department,
                        employee.role,
                        employee.salary,
                        employee.experience_years,
                        employee.performance_score,
                        employee.attendance_rate,
                    )
                    for employee in employees
                ],
            )
            connection.commit()

    def get_all_employees(self) -> list[Employee]:
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM employees ORDER BY department, salary DESC"
            ).fetchall()
        return [self._row_to_employee(row) for row in rows]

    def get_employee(self, employee_id: int) -> Employee | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM employees WHERE id = ?",
                (employee_id,),
            ).fetchone()
        if row is None:
            return None
        return self._row_to_employee(row)

    def update_employee_salary(self, employee_id: int, new_salary: float) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE employees SET salary = ? WHERE id = ?",
                (new_salary, employee_id),
            )
            connection.commit()

    def delete_employee(self, employee_id: int) -> None:
        with self.connect() as connection:
            connection.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            connection.commit()

    def employee_count(self) -> int:
        with self.connect() as connection:
            row = connection.execute("SELECT COUNT(*) AS count FROM employees").fetchone()
        return int(row["count"])

    @staticmethod
    def _row_to_employee(row: sqlite3.Row) -> Employee:
        return Employee(
            id=row["id"],
            name=row["name"],
            department=row["department"],
            role=row["role"],
            salary=row["salary"],
            experience_years=row["experience_years"],
            performance_score=row["performance_score"],
            attendance_rate=row["attendance_rate"],
        )
