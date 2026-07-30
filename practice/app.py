from flask import Flask, request,render_template

app = Flask(__name__)

@app.route("/",methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/about",methods=['GET']) #Query parameter
def about():
    usernname = request.args.get("name")
    address = request.args.get("address")
    print(usernname,address)
    return render_template("about.html",name=usernname,address=address)

@app.route("/services/<name>/<age>",methods=['GET'])  #path parameter
def services(name,age):
    return render_template("services.html",name=name,age=age)

@app.route("/login" , methods=['GET','POST'])
def login():
    if request.method == "POST":
        username = request.form.get('email')
        password = request.form.get('password')
        if username == "admin" and password == "admin@123":
            return render_template('dashboard.html',message="Sucess")
        else:
            return render_template('login.html',message="UnSucess")

    else:
        return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)