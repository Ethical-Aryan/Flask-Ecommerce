import os, uuid, requests
from flask import Flask, request, render_template, redirect, session, url_for, flash, abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ecommerce_secret_key'

# Secret path param to access admin (e.g. /admin/portal)
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'portal')

# Backend FastAPI URL
API_URL = 'http://127.0.0.1:8000'

# Local image upload directory
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'webp'}


# --- Helpers ---
def save_image(file):
    """Save an uploaded image to static/uploads and return its URL."""
    if file and file.filename:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext in ALLOWED_EXT:
            name = f"{uuid.uuid4().hex[:8]}_{secure_filename(file.filename)}"
            file.save(os.path.join(UPLOAD_FOLDER, name))
            return f"/static/uploads/{name}"
    return ""


def api(method, endpoint, **kwargs):
    """Single helper function to call FastAPI backend endpoints."""
    try:
        r = requests.request(method, f"{API_URL}{endpoint}", timeout=5, **kwargs)
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print(f"API Error ({endpoint}): {e}")
        return None


# --- Storefront Routes (Customer Facing) ---
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


# --- Customer Auth ---
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


# --- Admin Portal (Accessible ONLY via /admin/<key>) ---
@app.route("/admin/<key>", methods=["GET", "POST"])
def admin_portal(key):
    if key != ADMIN_KEY:
        abort(404)
    if "admin" in session:
        return redirect(url_for("admin_dashboard", key=key))
    if request.method == "POST":
        res = api("POST", "/admin/login", json={
            "username": request.form.get("username"),
            "password": request.form.get("password")
        })
        if res and "username" in res:
            session["admin"] = res["username"]
            return redirect(url_for("admin_dashboard", key=key))
        return render_template("admin_login.html", admin_key=key, error="Invalid Username or Password!")
    return render_template("admin_login.html", admin_key=key)


@app.route("/admin/<key>/dashboard")
def admin_dashboard(key):
    if key != ADMIN_KEY:
        abort(404)
    if "admin" not in session:
        return redirect(url_for("admin_portal", key=key))
    return render_template("dashboard.html", 
                           admin=session["admin"], 
                           admin_key=key, 
                           categories=api("GET", "/categories") or [], 
                           products=api("GET", "/products") or [])


@app.route("/admin/<key>/add_category", methods=["POST"])
def admin_add_category(key):
    if key != ADMIN_KEY or "admin" not in session:
        abort(404)
    img = save_image(request.files.get("image"))
    api("POST", "/categories", json={
        "name": request.form.get("name"),
        "icon": request.form.get("icon") or "bi bi-tag",
        "image": img,
        "description": request.form.get("description") or ""
    })
    flash("Category added!", "success")
    return redirect(url_for("admin_dashboard", key=key))


@app.route("/admin/<key>/add_product", methods=["POST"])
def admin_add_product(key):
    if key != ADMIN_KEY or "admin" not in session:
        abort(404)
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
    flash("Product added!", "success")
    return redirect(url_for("admin_dashboard", key=key))


@app.route("/admin/<key>/delete_category/<int:cat_id>", methods=["POST"])
def admin_delete_category(key, cat_id):
    if key != ADMIN_KEY or "admin" not in session:
        abort(404)
    api("DELETE", f"/categories/{cat_id}")
    flash("Category deleted!", "info")
    return redirect(url_for("admin_dashboard", key=key))


@app.route("/admin/<key>/delete_product/<int:prod_id>", methods=["POST"])
def admin_delete_product(key, prod_id):
    if key != ADMIN_KEY or "admin" not in session:
        abort(404)
    api("DELETE", f"/products/{prod_id}")
    flash("Product deleted!", "info")
    return redirect(url_for("admin_dashboard", key=key))


@app.route("/admin/<key>/logout")
def admin_logout(key):
    session.pop("admin", None)
    return redirect(url_for("admin_portal", key=key))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
