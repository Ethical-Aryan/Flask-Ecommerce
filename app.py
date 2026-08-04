from flask import Flask, request, render_template, redirect, session, url_for
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# =========================================================
# FLASK & MYSQL CONNECTION FLOW (5 EASY STEPS):
# 1. conn = get_db_connection()   -> XAMPP MySQL se connect karo
# 2. cursor = conn.cursor()        -> SQL query run karne ka tool banao
# 3. cursor.execute("SQL Query")   -> Database me query bhejo
# 4. data = cursor.fetchone()      -> MySQL se data fetch karo
# 5. conn.close()                 -> Connection band karo
# =========================================================


@app.route('/')
def home():
    # Step 1: MySQL se connect karo
    conn = get_db_connection()
    products = []
    
    if conn:
        # Step 2: Cursor open karo
        cursor = conn.cursor()
        try:
            # Step 3 & 4: Query execute karo aur data fetch karo
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()
        except Exception:
            pass
        # Step 5: Connection close karo
        conn.close()

    return render_template('index.html', products=products)


@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        # Form se username aur password get karo
        username = request.form['username']
        password = request.form['password']

        # Step 1: MySQL connect karo
        conn = get_db_connection()
        if not conn:
            return render_template('admin_login.html', error='Database Connection Failed! Start XAMPP MySQL.')

        # Step 2: Cursor open karo
        cursor = conn.cursor()
        
        # Step 3: MySQL me admin username search karo (%s parameterized SQL Injection se bachata hai)
        cursor.execute("SELECT username, password FROM admin WHERE username=%s", (username,))
        
        # Step 4: Record fetch karo
        admin = cursor.fetchone()
        
        # Step 5: Connection close karo
        conn.close()

        # Credentials check aur session set karo
        if admin:
            db_username, db_password = admin
            if db_username == username and db_password == password:
                session['username'] = username
                return redirect(url_for('dashboard'))

        return render_template('admin_login.html', error='Invalid username or password!')

    return render_template('admin_login.html')


@app.route('/dashboard')
def dashboard():
    # Session check (logged in user only)
    if 'username' in session:
        return render_template('dashboard.html', admin=session['username'])
    return redirect(url_for('admin_login'))


@app.route('/logout')
def logout():
    # Logout (Session clear)
    session.pop('username', None)
    return redirect(url_for('admin_login'))


if __name__ == '__main__':
    app.run(debug=True)