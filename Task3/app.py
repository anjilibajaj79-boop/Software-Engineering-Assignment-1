
from flask import Flask, request, jsonify
import sqlite3
import secrets
import hashlib
import hmac

app = Flask(__name__)

DB_NAME = "employees.db"

# Demo login accounts
USERS = {
    "admin": {
        "password": hashlib.sha256("Admin@123".encode()).hexdigest(),
        "role": "Administrator"
    },
    "employee": {
        "password": hashlib.sha256("Employee@123".encode()).hexdigest(),
        "role": "Employee"
    }
}

# Temporary authentication tokens
TOKENS = {}


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# CREATE DATABASE AND SAMPLE RECORDS
def initialize_database():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            salary REAL NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    if count == 0:
        conn.executemany("""
            INSERT INTO employees
            (name, department, position, salary)
            VALUES (?, ?, ?, ?)
        """, [
            ("Ali Khan", "IT", "Developer", 60000),
            ("Sara Ahmed", "HR", "HR Officer", 50000),
            ("Usman Malik", "Finance", "Accountant", 55000)
        ])

    conn.commit()
    conn.close()


# CHECK LOGIN TOKEN
def get_logged_in_user():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    return TOKENS.get(token)


# CHECK ADMIN PERMISSION
def admin_required():
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Authentication required. Please login first."
        }), 401

    if user["role"] != "Administrator":
        return jsonify({
            "error": "Access denied. Administrator permission required."
        }), 403

    return None


# 1. LOGIN API
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "")
    password = data.get("password", "")

    account = USERS.get(username)

    if account is None:
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    if not hmac.compare_digest(
        password_hash, account["password"]
    ):
        return jsonify({
            "error": "Invalid username or password"
        }), 401

    token = secrets.token_urlsafe(32)

    TOKENS[token] = {
        "username": username,
        "role": account["role"]
    }

    return jsonify({
        "message": "Login successful",
        "username": username,
        "role": account["role"],
        "token": token
    }), 200


# 2. VIEW EMPLOYEES (Both roles)
@app.route("/employees", methods=["GET"])
def view_employees():
    user = get_logged_in_user()

    if user is None:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = get_db()

    employees = conn.execute(
        "SELECT * FROM employees"
    ).fetchall()

    conn.close()

    return jsonify({
        "message": "Employees retrieved successfully",
        "role": user["role"],
        "employees": [dict(emp) for emp in employees]
    }), 200


# 3. ADD EMPLOYEE (ADMIN ONLY)
@app.route("/employees", methods=["POST"])
def add_employee():
    error = admin_required()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    required = ["name", "department", "position", "salary"]

    if not all(field in data for field in required):
        return jsonify({
            "error": "All employee fields are required"
        }), 400

    try:
        salary = float(data["salary"])

        if salary < 0:
            raise ValueError()

    except (ValueError, TypeError):
        return jsonify({
            "error": "Salary must be a valid non-negative number"
        }), 400

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO employees
        (name, department, position, salary)
        VALUES (?, ?, ?, ?)
    """, (
        data["name"],
        data["department"],
        data["position"],
        salary
    ))

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "message": "Employee added successfully",
        "employee_id": new_id
    }), 201


# 4. UPDATE EMPLOYEE (ADMIN ONLY)
@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    error = admin_required()

    if error:
        return error

    data = request.get_json(silent=True) or {}

    required = ["name", "department", "position", "salary"]

    if not all(field in data for field in required):
        return jsonify({
            "error": "All employee fields are required"
        }), 400

    try:
        salary = float(data["salary"])

        if salary < 0:
            raise ValueError()

    except (ValueError, TypeError):
        return jsonify({
            "error": "Salary must be a valid non-negative number"
        }), 400

    conn = get_db()

    cursor = conn.execute("""
        UPDATE employees
        SET name=?, department=?, position=?, salary=?
        WHERE id=?
    """, (
        data["name"],
        data["department"],
        data["position"],
        salary,
        employee_id
    ))

    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return jsonify({
            "error": "Employee not found"
        }), 404

    return jsonify({
        "message": "Employee updated successfully"
    }), 200


# 5. DELETE EMPLOYEE (ADMIN ONLY)
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    error = admin_required()

    if error:
        return error

    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM employees WHERE id=?",
        (employee_id,)
    )

    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({
            "error": "Employee not found"
        }), 404

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


# START SERVER
if __name__ == "__main__":
    initialize_database()

    print("================================")
    print("EMPLOYEE MANAGEMENT API")
    print("Server running on port 5002")
    print("================================")

    app.run(
        debug=False,
        port=5002,
        use_reloader=False
    )
