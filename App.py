from flask import Flask, render_template, request
from datetime import date
import sqlite3
import os

app = Flask(__name__)


@app.route("/")
def home():

    return render_template(
        "home.html"
    )

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
        "attendance_v2.html",
        students=students
    )


@app.route("/save-attendance", methods=["POST"])
def save_attendance():

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

    cursor.execute("""
    SELECT id
    FROM students
    """)

    students = cursor.fetchall()

    for student in students:

        student_id = student[0]

        status = request.form.get(
            f"status_{student_id}",
            "Absent"
        )

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

    <br><br>

    <a href="/">
        Back to Attendance
    </a>
    """

@app.route("/history")
def history():

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        attendance_date,
        COUNT(CASE WHEN status='Present' THEN 1 END),
        COUNT(CASE WHEN status='OD' THEN 1 END),
        COUNT(CASE WHEN status='Absent' THEN 1 END)
    FROM attendance
    GROUP BY attendance_date
    ORDER BY attendance_date DESC
    """)

    history_data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history_data=history_data
    )


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

    # Absent Students
    cursor.execute("""
    SELECT s.roll_no, s.name
    FROM attendance a
    JOIN students s
    ON a.student_id = s.id
    WHERE
        a.attendance_date = ?
        AND a.status = 'Absent'
    ORDER BY s.roll_no
    """,
    (today,)
    )

    absent_students = cursor.fetchall()

    # OD Students
    cursor.execute("""
    SELECT s.roll_no, s.name
    FROM attendance a
    JOIN students s
    ON a.student_id = s.id
    WHERE
        a.attendance_date = ?
        AND a.status = 'OD'
    ORDER BY s.roll_no
    """,
    (today,)
    )

    od_students = cursor.fetchall()

    # Present Count
    cursor.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE
        attendance_date = ?
        AND status = 'Present'
    """,
    (today,)
    )

    present_count = cursor.fetchone()[0]

    absent_count = len(absent_students)
    od_count = len(od_students)

    # Total Strength
    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    """)

    total_strength = cursor.fetchone()[0]

    report_text = f"""
AI&DS Attendance Report

Date: {today}

Total Strength: {total_strength}

Present: {present_count}
OD: {od_count}
Absent: {absent_count}

OD Students

"""

    for roll_no, name in od_students:
        report_text += f"{roll_no} - {name}\n"

    report_text += "\nAbsent Students\n\n"

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
    margin-right: 10px;
}}

pre {{
    background: #f4f4f4;
    padding: 20px;
    border-radius: 8px;
    white-space: pre-wrap;
}}

</style>

</head>

<body>

<h1>Attendance Report</h1>

<pre id="report">{report_text}</pre>

<button onclick="copyReport()">
    Copy Report
</button>

<button onclick="shareWhatsApp()">
    Share on WhatsApp
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

function shareWhatsApp() {{

    const text =
    document.getElementById("report").innerText;

    window.open(
        "https://wa.me/?text=" +
        encodeURIComponent(text)
    );
}}

</script>

</body>
</html>
"""
@app.route("/report/<attendance_date>")
def view_old_report(attendance_date):

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Absent Students
    cursor.execute("""
    SELECT s.roll_no, s.name
    FROM attendance a
    JOIN students s
    ON a.student_id = s.id
    WHERE
        a.attendance_date = ?
        AND a.status = 'Absent'
    ORDER BY s.roll_no
    """,
    (attendance_date,)
    )

    absent_students = cursor.fetchall()

    # OD Students
    cursor.execute("""
    SELECT s.roll_no, s.name
    FROM attendance a
    JOIN students s
    ON a.student_id = s.id
    WHERE
        a.attendance_date = ?
        AND a.status = 'OD'
    ORDER BY s.roll_no
    """,
    (attendance_date,)
    )

    od_students = cursor.fetchall()

    # Present Count
    cursor.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE
        attendance_date = ?
        AND status = 'Present'
    """,
    (attendance_date,)
    )

    present_count = cursor.fetchone()[0]

    absent_count = len(absent_students)
    od_count = len(od_students)

    # Total Strength
    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    """)

    total_strength = cursor.fetchone()[0]

    report_text = f"""
AI&DS Attendance Report

Date: {attendance_date}

Total Strength: {total_strength}

Present: {present_count}
OD: {od_count}
Absent: {absent_count}

OD Students

"""

    for roll_no, name in od_students:
        report_text += f"{roll_no} - {name}\n"

    report_text += "\nAbsent Students\n\n"

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

    pre {{
        background: #f4f4f4;
        padding: 20px;
        border-radius: 8px;
        white-space: pre-wrap;
    }}

    </style>

</head>

<body>

    <h1>Attendance Report</h1>

    <pre>{report_text}</pre>

    <br>

    <a href="/history">
        Back to History
    </a>

</body>
</html>
"""
if __name__ == "__main__":
    app.run(debug=True)