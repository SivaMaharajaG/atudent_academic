from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'database/student.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            course TEXT NOT NULL
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT NOT NULL,
            marks INTEGER,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
    """)
    conn.commit()
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()
    students = conn.execute('SELECT * FROM students').fetchall()
    return render_template('student_list.html', students=students)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect('/')
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        course = request.form['course']
        conn = get_db()
        conn.execute('INSERT INTO students (name, roll, course) VALUES (?, ?, ?)', (name, roll, course))
        conn.commit()
        flash('Student added successfully')
        return redirect('/')
    return render_template('add_student.html')

@app.route('/view/<int:id>')
def view_marks(id):
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()
    student = conn.execute('SELECT * FROM students WHERE id=?', (id,)).fetchone()
    marks = conn.execute('SELECT * FROM marks WHERE student_id=?', (id,)).fetchall()
    return render_template('view_marks.html', student=student, marks=marks)

@app.route('/attendance/<int:id>', methods=['GET', 'POST'])
def attendance(id):
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()
    if request.method == 'POST':
        date = request.form['date']
        status = request.form['status']
        conn.execute('INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)', (id, date, status))
        conn.commit()
    records = conn.execute('SELECT * FROM attendance WHERE student_id=?', (id,)).fetchall()
    return render_template('attendance.html', records=records, student_id=id)

@app.route('/reports')
def reports():
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()
    report_data = conn.execute('SELECT s.name, s.roll, AVG(m.marks) as avg_marks FROM students s JOIN marks m ON s.id = m.student_id GROUP BY s.id').fetchall()
    return render_template('reports.html', reports=report_data)

if __name__ == '__main__':
    app.run(debug=True)
