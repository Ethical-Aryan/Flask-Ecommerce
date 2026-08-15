from flask import Flask, request, render_template, redirect, session, url_for
import requests

app = Flask(__name__)
app.secret_key = 'super_secret_key'
API_URL = "http://127.0.0.1:8000"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/adminlogin", methods=['GET', 'POST'])
def handle_admin_login():
    if request.method == 'POST':
        u = request.form.get('username')
        p = request.form.get('password')
        res = requests.post(f"{API_URL}/admin/login", json={"username": u, "password": p})
        if res.status_code == 200:
            session['admin'] = u
            return redirect(url_for('dashboard'))
        return render_template("admin_login.html", error="Invalid Username or Password!")
    return render_template("admin_login.html")

@app.route("/dashboard")
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('handle_admin_login'))
    return render_template("dashboard.html", admin=session['admin'])

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('handle_admin_login'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        n = request.form.get('name')
        e = request.form.get('email')
        p = request.form.get('password')
        res = requests.post(f"{API_URL}/student/insert", json={"name": n, "email": e, "password": p})
        if res.status_code in [200, 201]:
            return render_template("login.html", mess="Registration successful!")
        return render_template("register.html", mess="Registration failed!")
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
