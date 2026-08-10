from flask import Flask, request, render_template, redirect, session, url_for
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_secret_key'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/products")
def products():
    return render_template("products.html")


@app.route("/admin_login", methods=['GET'])
def admin_login():
    if 'admin' in session:
        return redirect(url_for('dashboard'))
    return render_template("admin_login.html")


@app.route("/adminlogin", methods=['POST'])
def handle_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
                admin_user = cursor.fetchone()
                if admin_user:
                    session['admin'] = username
                    return redirect(url_for('dashboard'))
        except Exception as e:
            print(f"Database Query Error: {e}")
        finally:
            conn.close()

    # Fallback check for default admin credentials
    if username == 'admin' and password == 'admin123':
        session['admin'] = username
        return redirect(url_for('dashboard'))

    return render_template("admin_login.html", error="Invalid Username or Password!")


@app.route("/dashboard")
def dashboard():
    # Require admin session to access dashboard
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    return render_template("dashboard.html", admin=session['admin'])


@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.get("/login")
def login():
    return render_template("login.html")


@app.get("/register")
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run(debug=True)
