from flask import Flask, render_template, request, redirect, session, send_from_directory, url_for
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx", "pptx", "txt"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
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

# ---------------- HELPER ----------------
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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
        c.execute("SELECT * FROM users WHERE username=? AND role=?", (username, role))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user"] = username
            session["role"] = role
            return redirect(f"/dashboard/{role}")
        else:
            return "Invalid Login"

    return render_template(f"{role}_login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard/<role>")
def dashboard(role):
    if "user" not in session:
        return redirect("/")

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

# ---------------- REGISTER (NEW) ----------------
@app.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = sqlite3.connect("database.db")
        c = conn.cursor()

        try:
            c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                      (username, password, role))
            conn.commit()
        except:
            return "User already exists"

        conn.close()
        return redirect(f"/login/{role}")

    return render_template("register.html", role=role)

# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["POST"])
def upload():
    if "user" not in session:
        return redirect("/")

    file = request.files["file"]
    year = request.form["year"]
    subject = request.form["subject"]

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO files (filename, uploaded_by, year, subject) VALUES (?, ?, ?, ?)",
                  (filename, session["user"], year, subject))
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
        try:
            os.remove(os.path.join(app.config["UPLOAD_FOLDER"], file[0]))
        except:
            pass

        c.execute("DELETE FROM files WHERE id=?", (id,))
        conn.commit()

    conn.close()
    return redirect(request.referrer)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
