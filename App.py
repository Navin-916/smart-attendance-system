from flask import Flask, render_template, request
from datetime import date
import sqlite3
import os

app = Flask(__name__)

@app.route("/")
def attendance_page():

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, roll_no, name
    FROM students
    ORDER BY roll_no
    """)

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance.html",
        students=students
    )
@app.route("/save-attendance", methods=["POST"])
def save_attendance():

    selected_students = request.form.getlist("present")

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute(
        "DELETE FROM attendance WHERE attendance_date = ?",
        (today,)
    )

    cursor.execute(
        "SELECT id FROM students"
    )

    all_students = cursor.fetchall()

    for student in all_students:

        student_id = student[0]

        if str(student_id) in selected_students:
            status = "Present"
        else:
            status = "Absent"

        cursor.execute("""
        INSERT INTO attendance
        (
            student_id,
            attendance_date,
            status
        )
        VALUES (?, ?, ?)
        """,
        (
            student_id,
            today,
            status
        ))

    conn.commit()
    conn.close()

    return """
    <h1>Attendance Saved Successfully</h1>

    <a href="/report">
    Generate Report
    </a>
    """      
   
@app.route("/report")
def report():

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    today = date.today().isoformat()

    cursor.execute("""
    SELECT
        s.roll_no,
        s.name
    FROM attendance a
    JOIN students s
    ON a.student_id = s.id
    WHERE
        a.attendance_date = ?
        AND a.status = 'Absent'
    """,
    (today,)
    )

    absent_students = cursor.fetchall()

    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    """)

    total_strength = cursor.fetchone()[0]

    absent_count = len(absent_students)

    present_count = total_strength - absent_count

    report_text = f"""
AI&DS Attendance Report

Date: {today}

Total Strength: {total_strength}
Present: {present_count}
Absent: {absent_count}

Absent Students

"""

    for roll_no, name in absent_students:
        report_text += f"{roll_no} - {name}\n"

    conn.close()

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Attendance Report</title>

        <style>

        body {{
            font-family: Arial, sans-serif;
            padding: 30px;
        }}

        button {{
            padding: 10px 20px;
            cursor: pointer;
            margin-top: 15px;
        }}

        pre {{
            background: #f4f4f4;
            padding: 20px;
            border-radius: 8px;
        }}

        </style>

    </head>

    <body>

        <h1>Attendance Report</h1>

        <pre id="report">{report_text}</pre>

        <button onclick="copyReport()">
            Copy Report
        </button>

        <br><br>

        <a href="/">
            Back to Attendance Page
        </a>

        <script>

        function copyReport() {{

            const text =
            document.getElementById("report").innerText;

            navigator.clipboard.writeText(text);

            alert("Report Copied Successfully!");
        }}

        </script>

    </body>
    </html>
    """
if __name__ == "__main__":
    app.run(debug=True)