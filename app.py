import os, requests
from flask import Flask, request, render_template, redirect, session, url_for

app = Flask(__name__)
app.secret_key = 'ecommerce_storefront_secret'

# FastAPI Backend URL
API_URL = 'http://127.0.0.1:8000'


def api(method, endpoint, **kwargs):
    """Helper to query the FastAPI backend."""
    try:
        r = requests.request(method, f"{API_URL}{endpoint}", timeout=5, **kwargs)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"API Error ({endpoint}): {e}")
        return None


# --- Customer Storefront Routes ---
@app.route("/")
def index():
    return render_template("index.html", 
                           categories=api("GET", "/categories") or [], 
                           products=api("GET", "/products") or [])


@app.route("/products")
def products():
    cat_id = request.args.get("category")
    params = {"category_id": cat_id} if cat_id else None
    return render_template("products.html", 
                           categories=api("GET", "/categories") or [], 
                           products=api("GET", "/products", params=params) or [])


# --- Customer Authentication ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        p, cp = request.form.get("password"), request.form.get("cpassword")
        if p != cp:
            return render_template("register.html", error="Passwords do not match!")
        res = api("POST", "/user/register", json={
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": p
        })
        if res and "error" not in res:
            return render_template("login.html", mess="Account created! Please log in.")
        return render_template("register.html", error=(res.get("error") if res else "Backend API offline"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        res = api("POST", "/user/login", json={
            "email": request.form.get("email"),
            "password": request.form.get("password")
        })
        if res and "user" in res:
            session["user"] = res["user"]
            return redirect(url_for("index"))
        return render_template("login.html", error=(res.get("error") if res else "Invalid email or password!"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    print("[Storefront] Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
