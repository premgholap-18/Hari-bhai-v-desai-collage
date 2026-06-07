from flask import Flask, render_template, request, redirect, session, send_from_directory
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        password TEXT,
        role TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        filename TEXT,
        uploaded_by TEXT,
        year TEXT,
        subject TEXT
    )''')

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route("/")
def index():
    return render_template("index.html")

# ---------------- LOGIN ----------------
@app.route("/login/<role>", methods=["GET", "POST"])
def login(role):
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?",
                  (username, password, role))
        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["role"] = role
            return redirect(f"/dashboard/{role}")
        else:
            return "Invalid Login"

    return render_template(f"{role}_login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard/<role>")
def dashboard(role):
    year = request.args.get("year")
    subject = request.args.get("subject")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    if year and subject:
        c.execute("SELECT * FROM files WHERE year=? AND subject=?", (year, subject))
    elif year:
        c.execute("SELECT * FROM files WHERE year=?", (year,))
    else:
        c.execute("SELECT * FROM files")

    files = c.fetchall()
    conn.close()

    return render_template(f"dashboard_{role}.html", files=files)

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    year = request.form["year"]
    subject = request.form["subject"]

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO files (filename, uploaded_by, year, subject) VALUES (?, ?, ?, ?)",
                  (file.filename, session["user"], year, subject))
        conn.commit()
        conn.close()

    return redirect(request.referrer)

# ---------------- DOWNLOAD ----------------
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "teacher":
        return "Access Denied"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("SELECT filename FROM files WHERE id=?", (id,))
    file = c.fetchone()

    if file:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file[0]))
        c.execute("DELETE FROM files WHERE id=?", (id,))
        conn.commit()

    conn.close()
    return redirect(request.referrer)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)
