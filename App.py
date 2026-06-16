from flask import Flask, render_template, request, redirect
from flask import Flask, render_template, request
from datetime import date
import sqlite3
import os

app = Flask(__name__)
USERS = {
    "AIDS_A": {
        "password": "AIDSA2026",
        "section": "A"
    },
    "AIDS_B": {
        "password": "AIDSB2026",
        "section": "B"
    }
}
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username in USERS and password == USERS[username]["password"]:

            section = USERS[username]["section"]

            return redirect(f"/section/{section}")

        return "Invalid Login"

    return render_template("login.html")

@app.route("/")
def home():

    return redirect("/login")
@app.route("/section/<section>")
def attendance_page(section):

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
    WHERE section = ?
    ORDER BY roll_no
    """,
    (section,)
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "attendance_v2.html",
        students=students,
        section=section
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

    today = request.form.get(
    "attendance_date",
    date.today().isoformat()
    )

    section = request.form.get("section")

    cursor.execute(
        """
        DELETE FROM attendance
        WHERE attendance_date = ?
        AND section = ?
        """,
        (today, section)
    )

    cursor.execute("""
    SELECT id
    FROM students
    WHERE section = ?
    """,
    (section,)
    )

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
            status,
            section
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            student_id,
            today,
            status,
            section
        ))

    conn.commit()
    conn.close()

    return f"""
    <h1>Attendance Saved Successfully</h1>

    <a href="/report/{section}">
        Generate Report
    </a>

    <br><br>

    <a href="/section/{section}">
        Back to Attendance
    </a>
    """
@app.route("/history/<section>")
def history(section):

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
    WHERE section = ?
    GROUP BY attendance_date
    ORDER BY attendance_date DESC
    """,
    (section,)
    )

    history_data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history_data=history_data,
        section=section
    )

@app.route("/report/<section>")
def report(section):

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
        AND a.section = ?
    ORDER BY s.roll_no
    """,
    (today, section)
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
        AND a.section = ?
    ORDER BY s.roll_no
    """,
    (today, section)
    )

    od_students = cursor.fetchall()

    # Present Count
    cursor.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE
        attendance_date = ?
        AND status = 'Present'
        AND section = ?
    """,
    (today, section)
    )

    present_count = cursor.fetchone()[0]

    absent_count = len(absent_students)
    od_count = len(od_students)

    # Total Strength
    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    WHERE section = ?
    """,
    (section,)
    )

    total_strength = cursor.fetchone()[0]

    report_text = f"""
AI&DS {section} Attendance Report

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

<h1>Attendance Report - Section {section}</h1>

<pre id="report">{report_text}</pre>

<button onclick="copyReport()">
    Copy Report
</button>

<button onclick="shareWhatsApp()">
    Share on WhatsApp
</button>

<a href="/section/{section}">
    <button>Edit Today's Attendance</button>
</a>

<br><br>

<a href="/section/{section}">
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
@app.route("/report/<section>/<attendance_date>")
def view_old_report(section, attendance_date):

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
        AND a.section = ?
    ORDER BY s.roll_no
    """,
    (attendance_date, section)
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
        AND a.section = ?
    ORDER BY s.roll_no
    """,
    (attendance_date, section)
    )

    od_students = cursor.fetchall()

    # Present Count
    cursor.execute("""
    SELECT COUNT(*)
    FROM attendance
    WHERE
        attendance_date = ?
        AND status = 'Present'
        AND section = ?
    """,
    (attendance_date, section)
    )

    present_count = cursor.fetchone()[0]

    absent_count = len(absent_students)
    od_count = len(od_students)

    # Total Strength
    cursor.execute("""
    SELECT COUNT(*)
    FROM students
    WHERE section = ?
    """,
    (section,)
    )

    total_strength = cursor.fetchone()[0]

    report_text = f"""
AI&DS {section} Attendance Report

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

button {{
    padding: 10px 20px;
    cursor: pointer;
}}

</style>

</head>

<body>

<h1>Attendance Report - Section {section}</h1>

<pre>{report_text}</pre>

<br>

<a href="/edit/{section}/{attendance_date}">
    <button>
        Edit Attendance
    </button>
</a>

<br><br>
<a href="/history/{section}">
    <button>
        Back to History
    </button>
</a>

</body>
</html>
"""
@app.route("/edit/<section>/<attendance_date>")
def edit_attendance(section, attendance_date):

    db_path = os.path.join(
        os.path.dirname(__file__),
        "Database",
        "attendance.db"
    )

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        s.id,
        s.roll_no,
        s.name,
        a.status
    FROM students s
    LEFT JOIN attendance a
    ON s.id = a.student_id
    WHERE
        s.section = ?
        AND a.attendance_date = ?
    ORDER BY s.roll_no
    """,
    (section, attendance_date)
    )

    students = cursor.fetchall()

    conn.close()

    return render_template(
        "edit_attendance.html",
        students=students,
        section=section,
        attendance_date=attendance_date
    )

if __name__ == "__main__":
    app.run(debug=True)