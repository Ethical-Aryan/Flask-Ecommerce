import os, json, requests
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


@app.context_processor
def inject_global_data():
    """Ensure categories are available in the navbar across all templates."""
    return {
        "categories": api("GET", "/categories") or []
    }


# --- Customer Storefront Routes ---
@app.route("/")
def index():
    return render_template("index.html", products=api("GET", "/products") or [])


@app.route("/products")
def products():
    cat_id = request.args.get("category")
    search_q = request.args.get("search", "").strip().lower()
    params = {"category_id": cat_id} if cat_id else None
    all_products = api("GET", "/products", params=params) or []
    
    if search_q:
        all_products = [
            p for p in all_products 
            if search_q in p.get("title", "").lower() or search_q in (p.get("description") or "").lower()
        ]
        
    return render_template("products.html", 
                           products=all_products,
                           current_category=cat_id,
                           search_query=request.args.get("search", ""))


@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = api("GET", f"/products/{product_id}")
    if not product:
        return redirect(url_for("products"))
    related = api("GET", "/products", params={"category_id": product.get("category_id")}) or []
    related = [p for p in related if p.get("id") != product_id][:4]
    return render_template("product_detail.html", product=product, related_products=related)


# --- Checkout & Order Management ---
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        payload = {
            "customer_name": request.form.get("customer_name"),
            "customer_email": request.form.get("customer_email"),
            "customer_phone": request.form.get("customer_phone"),
            "address_line1": request.form.get("address_line1"),
            "address_line2": request.form.get("address_line2") or "",
            "city": request.form.get("city"),
            "state": request.form.get("state"),
            "postal_code": request.form.get("postal_code"),
            "country": request.form.get("country") or "United States",
            "payment_method": request.form.get("payment_method") or "Credit Card",
            "subtotal": float(request.form.get("subtotal") or 0),
            "shipping": float(request.form.get("shipping") or 0),
            "total": float(request.form.get("total") or 0),
            "items_json": request.form.get("items_json") or "[]"
        }
        res = api("POST", "/orders", json=payload)
        if res and "order_number" in res:
            return redirect(url_for("order_success", order_number=res["order_number"]))
        return render_template("checkout.html", error="Could not place order. Please try again.")
    return render_template("checkout.html")


@app.route("/order-success/<order_number>")
def order_success(order_number):
    order = api("GET", f"/orders/{order_number}")
    if not order:
        return redirect(url_for("index"))
    items = []
    if order.get("items_json"):
        try:
            items = json.loads(order["items_json"])
        except Exception:
            items = []
    return render_template("order_success.html", order=order, items=items)


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