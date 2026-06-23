from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        # For now just print (later we save in DB)
        print("New User:", name, email, username, password)

        return "✅ User Registered Successfully!"

    return render_template('register.html')


# ---------------- STUDENT LOGIN ----------------
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # TEMP LOGIN CHECK (demo)
        if username == "admin" and password == "1234":
            return redirect(url_for('student_dashboard'))
        else:
            return "❌ Invalid Login"

    return render_template('student_login.html')


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/dashboard_student')
def student_dashboard():
    return render_template('dashboard_student.html')


# ---------------- TEACHER LOGIN ----------------
@app.route('/teacher_login', methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "teacher" and password == "1234":
            return redirect(url_for('teacher_dashboard'))
        else:
            return "❌ Invalid Login"

    return render_template('teacher_login.html')


# ---------------- TEACHER DASHBOARD ----------------
@app.route('/dashboard_teacher')
def teacher_dashboard():
    return render_template('dashboard_teacher.html')


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
