from flask import Flask, request,render_template , redirect,url_for

app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
    if request.method == "POST":    
        name = request.form.get("username")
        return render_template("index.html", username=name)
    return render_template("index.html", username=" ")

@app.route("/about",methods=['GET']) #Query parameter
def about():
    usernname = request.args.get("name")
    address = request.args.get("address")
    print(usernname,address)
    return render_template("about.html",name=usernname,address=address)

@app.route("/services/<name>/<age>",methods=['GET'])  #path parameter
def services(name,age):
    return render_template("services.html",name=name,age=age)

@app.get("/dashboard")
def dashboard():
    message = request.args.get('message')
    username = request.args.get('username')
    return render_template("dashboard.html", message=message, username=username)

@app.route("/register" , methods=['GET','POST'])
def register():
    if request == "POST":
        name = request.form.get('name')
        username= request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        return render_template("login.html" , mess="Registeration sucessfull")
    else:
        return render_template("register.html",mess="Registeration Unsuccessfull")


@app.route("/login" , methods=['GET','POST'])
def login():
    if request.method == "POST":
        name = request.form.get('username')
        username = request.form.get('email')
        password = request.form.get('password')
        return render_template("index.html" , message="Login Successfull" , mess="Registeration successfull now login")
    else:
        return render_template('login.html')


if __name__ == "__main__":
    app.run(debug=True)