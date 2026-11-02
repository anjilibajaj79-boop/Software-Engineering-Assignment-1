
from flask import Flask, request, jsonify
from database import get_connection, create_table

app = Flask(__name__)

# Create database table
create_table()


# GET: Display all students
@app.route('/students', methods=['GET'])
def get_students():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return jsonify([dict(student) for student in students]), 200


# GET: Display student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student)), 200


# POST: Add new student
@app.route('/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    name = data.get('name')
    department = data.get('department')
    email = data.get('email')

    if not all([name, department, email]):
        return jsonify({"error": "All fields are required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO students (name, department, email)
               VALUES (?, ?, ?)""",
            (name, department, email)
        )

        conn.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        conn.close()


# PUT: Update student
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON data required"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (id,))
    student = cursor.fetchone()

    if student is None:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    name = data.get('name', student['name'])
    department = data.get('department', student['department'])
    email = data.get('email', student['email'])

    try:
        cursor.execute("""
            UPDATE students
            SET name = ?, department = ?, email = ?
            WHERE id = ?
        """, (name, department, email, id))

        conn.commit()

        return jsonify({"message": "Student updated successfully"}), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400

    finally:
        conn.close()


# DELETE: Delete student
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()

    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"}), 200


# Start Flask server
if __name__ == '__main__':
    app.run(debug=True, port=5000)
