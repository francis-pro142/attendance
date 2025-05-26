from flask import Flask, request, redirect, url_for, render_template_string, flash, send_file
import sqlite3
import os
import openpyxl
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'secret'

# Ensure database exists
conn = sqlite3.connect('attendance.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        student_id TEXT,
        level TEXT,
        week_id TEXT,
        course TEXT
        
    )
''')
conn.commit()
conn.close()

# HTML TEMPLATES
login_student_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Student Login</title>
    <style>
        body { font-family: Arial; background: #f1f1f1; padding: 50px; }
        .login-box { background: -moz-linear-gradient(right , black,white); padding: 40px; border-radius: 10px; max-width: 400px; margin: auto; box-shadow: 0 0 10px blue; }
        input, button { padding: 10px; width: 100%; margin: 10px 0; }
    </style>
</head>
<body>
<div class="login-box">
    <h2>Student Login</h2>
    <form method="POST">
        <input type="text" name="index" placeholder="Index Number (10 digits)" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <p style="color: red;">{{ messages[0] }}</p>
        {% endif %}
    {% endwith %}
</div>
</body>
</html>
'''

student_form_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Submit Attendance</title>
    <style>
        body { font-family: Arial;
        padding: 50px; }
        .form-box { background: -moz-linear-gradient(right , black,white,red); padding: 40px; border-radius: 10px; max-width: 500px; margin: auto; box-shadow: 0 0 10px #ccc; }
        input, select, button 
        { padding: 10px; width: 100%; margin: 10px 0; }
    </style>
</head>
<body>
<div class="form-box">
 <a href="{{ url_for('home') }}" class="btn" style="display: inline-block; padding:10px 20px;
        margin: 10px; background-color: #4CAF50, color: white ; text-decoration:none; 
        border-radius:5px; font-weight:bold; font-size: 20px" >HOME</a>

    <h2>Submit Attendance</h2>
    <form method="POST">
        <input type="text" name="full_name" placeholder="Full Name" required>
        <input type="text" name="student_id" placeholder="Student ID" required>
        <input type="text" name="level" placeholder="Level" required>
        <input type="text" name="week_id" placeholder="Week" required>
        <select name="course" required style="background: -moz-linear-gradient(left, white,red);">
            <option disabled selected style="background: -moz-linear-gradient(left, white,red);">Choose a course</option>
            <option>Computer Network</option>
            <option>Cloud Computing</option>
            <option>Software Engineering</option>
            <option>Object Oriented Programming</option>
            <option>Automata Theory</option>
            <option>Operating System</option>
            <option>Scripting Language</option>
        </select>
        <button type="submit" style="background: -moz-linear-gradient(left, white,yellow);">Submit Attendance</button>
    </form>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <script>alert('{{ messages[0] }}');</script>
        {% endif %}
    {% endwith %}
</div>
</body>
</html>
'''

login_admin_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: Arial; background: #f1f1f1; padding: 50px; }
        .login-box { background: -moz-linear-gradient(right , black,white,red); padding: 40px; border-radius: 10px; max-width: 400px; margin: auto; box-shadow: 0 0 10px #ccc; }
        input, button { padding: 10px; width: 100%; margin: 10px 0; background: -moz-linear-gradient(right , black,white,red); }
    </style>
</head>
<body>
<div class="login-box">
    <h2>Admin Login</h2>
    <form method="POST">
        <input type="password" name="password" placeholder="Admin Password" required>
        <button type="submit">Login</button>
    </form>
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <p style="color: red;">{{ messages[0] }}</p>
        {% endif %}
    {% endwith %}
</div>
</body>
</html>
'''

admin_dashboard_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <style>
        body { font-family: Arial; background: #f0f8ff; padding: 20px; }
        table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 0 10px #ccc; }
        th, td { padding: 10px; border: 1px solid #ccc; text-align: left; }
        th { background-color: #007acc; color: white; }
        .export-btn { padding: 10px 20px; background-color: #28a745; color: white; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
    </style>
</head>
<body>
 <a href="{{ url_for('home') }}" class="btn"  style="display: inline-block; padding:10px 20px;
        margin: 10px; background-color: #4CAF50, color: white ; text-decoration:none; 
        border-radius:5px; font-weight:bold; font-size: 20px">HOME</a>

<h2>Attendance Records</h2>
<a href="{{ url_for('export') }}" class="export-btn">Export to Excel</a>
<table>
    <tr>
        <th>Full Name</th>
        <th>Student ID</th>
        <th>Level</th>
        <th>Week</th>
        <th>Course</th>
    </tr>
    {% for r in records %}
    <tr>
        <td>{{ r[0] }}</td>
        <td>{{ r[1] }}</td>
        <td>{{ r[2] }}</td>
        <td>{{ r[3] }}</td>
        <td>{{ r[4] }}</td>
    </tr>
    {% endfor %}
</table>
</body>
</html>
'''



home_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: Arial; background: #f1f1f1; padding: 50px; }
        .login-box {  background: -moz-linear-gradient(right , black,white,red); padding: 60px; border-radius: 10px; margin: auto;  }
        input, button { padding: 10px; width: 100%; margin: 10px 0; }
    </style>
</head>
<body>
<div class="login-box">
    <h2 style="text-align: center;">WELCOME TO <br> CLASS ATTENDANCE ONLINE 📗📗</h2>
    
    <p style="text-align: center;" >PLEASE CLICK ONE</p>
    <div style="text-align:center;">
        <a href="{{ url_for('student_login') }}" class="btn" style="display: inline-block; padding:10px 20px;
        margin: 10px; background-color: #4CAF50, color: white ; text-decoration:none; 
        border-radius:5px; font-weight:bold; font-size: 20px">STUDENT LOGIN</a>
        
        <a href="{{ url_for('admin_login') }}" class="btn" class="btn" style="display: inline-block; padding:10px 20px;
        margin: 10px; background-color: #4CAF50, color: white ; text-decoration:none; 
        border-radius:5px; font-weight:bold;font-size: 20px">ADMIN LOGIN</a>
    </div>
    
</div>
</body>
</html>
'''


# ROUTES
@app.route('/')
def home():
    return render_template_string(home_template)

@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        index = request.form['index']
        password = request.form['password']
        if len(index) != 10 or not index.isdigit():
            flash("Index number must be exactly 10 digits.")
        elif password != "GCTU200CS":
            flash("Invalid password.")
        else:
            return redirect(url_for('student_form'))
    return render_template_string(login_student_template)

@app.route('/student_form', methods=['GET', 'POST'])
def student_form():
    if request.method == 'POST':
        full_name = request.form['full_name']
        student_id = request.form['student_id']
        level = request.form['level']
        week_id = request.form['week_id']
        course = request.form['course']
        conn = sqlite3.connect('attendance.db')
        c = conn.cursor()
        c.execute("INSERT INTO attendance (full_name, student_id, level, week_id, course) VALUES (?, ?, ?, ?, ?)",
                  (full_name, student_id, level, week_id, course))
        conn.commit()
        conn.close()
        flash("Attendance submitted successfully.")
        return redirect(url_for('student_form'))
    return render_template_string(student_form_template)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'GCTU200':
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid admin password.")
    return render_template_string(login_admin_template)

@app.route('/admin_dashboard')
def admin_dashboard():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT full_name, student_id, level, week_id, course FROM attendance")
    records = c.fetchall()
    conn.close()
    return render_template_string(admin_dashboard_template, records=records)

@app.route('/export')
def export():
    conn = sqlite3.connect('attendance.db')
    c = conn.cursor()
    c.execute("SELECT full_name, student_id, level, week_id, course FROM attendance")
    records = c.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['Full Name', 'Student ID', 'Level', 'Week',  'Course'])
    for record in records:
        ws.append(record)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="attendance_records.xlsx", mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

# RUN APP
if __name__ == '__main__':
    app.run(debug=True)
