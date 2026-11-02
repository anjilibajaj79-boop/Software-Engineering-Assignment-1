import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000/students"

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Student Management System")
st.caption("University Student Records Management Dashboard")


def get_students():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        st.error("Cannot connect to Flask API. Please start app.py first.")
        return []


students = get_students()

# Dashboard
st.subheader("Dashboard Overview")

col1, col2 = st.columns(2)

with col1:
    st.metric("Total Students", len(students))

with col2:
    departments = set(s["department"] for s in students)
    st.metric("Departments", len(departments))

st.divider()

# Display Students
st.subheader("📋 All Students")

if students:
    df = pd.DataFrame(students)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("No students available. Add a new student below.")

st.divider()

# Add Student
st.subheader("➕ Add New Student")

with st.form("add_student_form"):
    name = st.text_input("Student Name")
    department = st.text_input("Department")
    email = st.text_input("Email Address")

    add_button = st.form_submit_button("Add Student")

    if add_button:
        if name.strip() and department.strip() and email.strip():
            try:
                response = requests.post(
                    API_URL,
                    json={
                        "name": name.strip(),
                        "department": department.strip(),
                        "email": email.strip()
                    },
                    timeout=5
                )

                if response.status_code == 201:
                    st.success("Student added successfully!")
                    st.rerun()
                else:
                    st.error(response.json().get("error", "Unable to add student"))

            except requests.RequestException:
                st.error("API connection failed.")
        else:
            st.warning("Please fill all fields.")

st.divider()

# Update and Delete
st.subheader("⚙️ Manage Existing Students")

if students:

    student_options = {
        f"{s['id']} - {s['name']}": s for s in students
    }

    selected_label = st.selectbox(
        "Select a Student",
        list(student_options.keys())
    )

    selected_student = student_options[selected_label]
    student_id = selected_student["id"]

    st.write("### ✏️ Update Student")

    with st.form("update_student_form"):

        updated_name = st.text_input(
            "Name",
            value=selected_student["name"]
        )

        updated_department = st.text_input(
            "Department",
            value=selected_student["department"]
        )

        updated_email = st.text_input(
            "Email",
            value=selected_student["email"]
        )

        update_button = st.form_submit_button("Update Student")

        if update_button:
            try:
                response = requests.put(
                    f"{API_URL}/{student_id}",
                    json={
                        "name": updated_name.strip(),
                        "department": updated_department.strip(),
                        "email": updated_email.strip()
                    },
                    timeout=5
                )

                if response.status_code == 200:
                    st.success("Student updated successfully!")
                    st.rerun()
                else:
                    st.error(response.json().get("error", "Update failed"))

            except requests.RequestException:
                st.error("API connection failed.")

    st.write("### 🗑️ Delete Student")

    if st.button("Delete Selected Student", type="primary"):
        try:
            response = requests.delete(
                f"{API_URL}/{student_id}",
                timeout=5
            )

            if response.status_code == 200:
                st.success("Student deleted successfully!")
                st.rerun()
            else:
                st.error(response.json().get("error", "Delete failed"))

        except requests.RequestException:
            st.error("API connection failed.")

else:
    st.info("Add a student first to use Update and Delete options.")

st.divider()

st.caption(
    "Student Management System | Developed using Flask, SQLite and Streamlit"
)