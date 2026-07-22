from flask import Flask, request, render_template, redirect, session
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route('/')
@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        # Database se username aur password fetch kar rahe hain
        cursor.execute("SELECT username, password FROM admin WHERE username=%s", (username,))
        admin = cursor.fetchone() # returns (db_username, db_password)
        conn.close()

        # Python if condition se matching check
        if admin:
            db_username, db_password = admin
            if db_username == username and db_password == password:
                session['username'] = username
                return redirect('/dashboard')

        return render_template('admin_login.html', error='Invalid username or password')

    return render_template('admin_login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', admin=session['username'])
    return redirect('/adminlogin')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/adminlogin')

if __name__ == '__main__':
    app.run(debug=True)