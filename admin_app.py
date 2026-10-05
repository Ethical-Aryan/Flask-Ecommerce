import os, uuid, requests
from flask import Flask, request, render_template, redirect, session, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ecommerce_admin_portal_secret'

# FastAPI Backend URL
API_URL = 'http://127.0.0.1:8000'

# Shared upload directory (static/uploads/)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp'}


def save_image(file):
    """Save uploaded image to static/uploads and return relative web path."""
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext in ALLOWED_EXT:
            name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
            file.save(os.path.join(UPLOAD_FOLDER, name))
            return f"/static/uploads/{name}"
    return ""


def api(method, endpoint, **kwargs):
    """Helper to query the FastAPI backend."""
    try:
        r = requests.request(method, f"{API_URL}{endpoint}", timeout=5, **kwargs)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"API Error ({endpoint}): {e}")
        return None


# --- Admin Portal Routes (Running on Port 5001) ---
@app.route("/")
def admin_root():
    if "admin" in session:
        return redirect(url_for("dashboard"))
    return render_template("admin_login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "admin" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        res = api("POST", "/admin/login", json={
            "username": request.form.get("username"),
            "password": request.form.get("password")
        })
        if res and "username" in res:
            session["admin"] = res["username"]
            return redirect(url_for("dashboard"))
        return render_template("admin_login.html", error="Invalid Username or Password!")

    return render_template("admin_login.html")


@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", 
                           admin=session["admin"], 
                           categories=api("GET", "/categories") or [], 
                           products=api("GET", "/products") or [])


@app.route("/add_category", methods=["POST"])
def add_category():
    if "admin" not in session:
        return redirect(url_for("login"))
    api("POST", "/categories", json={
        "name": request.form.get("name"),
        "icon": request.form.get("icon") or "bi bi-tag",
        "description": request.form.get("description") or ""
    })
    flash("Category added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/add_product", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect(url_for("login"))
    img = save_image(request.files.get("image")) or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500"
    payload = {
        "title": request.form.get("title"),
        "category_id": int(request.form.get("category_id")),
        "price": float(request.form.get("price")),
        "original_price": float(request.form.get("original_price")) if request.form.get("original_price") else None,
        "stock": int(request.form.get("stock") or 0),
        "badge": request.form.get("badge") or "New",
        "image": img,
        "description": request.form.get("description") or ""
    }
    api("POST", "/products", json=payload)
    flash("Product added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/delete_category/<int:cat_id>", methods=["POST"])
def delete_category(cat_id):
    if "admin" not in session:
        return redirect(url_for("login"))
    api("DELETE", f"/categories/{cat_id}")
    flash("Category deleted!", "info")
    return redirect(url_for("dashboard"))


@app.route("/delete_product/<int:prod_id>", methods=["POST"])
def delete_product(prod_id):
    if "admin" not in session:
        return redirect(url_for("login"))
    api("DELETE", f"/products/{prod_id}")
    flash("Product deleted!", "info")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    print("[Admin Portal] Running on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)
