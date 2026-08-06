from flask import Flask, request, render_template, redirect, session, url_for
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = 'super_secret_key'


@app.get("/login")
def login():
    return render_template("login.html")
if __name__ == '__main__':
    app.run(debug=True)