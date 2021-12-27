from cs50 import SQL
from flask_session import Session
from flask import Flask, render_template, redirect, request, session, jsonify
from datetime import datetime

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///data.db")


@app.route("/")
def index():
    products = db.execute("SELECT * FROM products ORDER BY name ASC")
    shirtsLen = len(products)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        products = db.execute("SELECT * FROM products ORDER BY name ASC")
        shirtsLen = len(products)
        return render_template("index.html", shoppingCart=shoppingCart, products=products, shopLen=shopLen,
                               shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session)
    return render_template("index.html", products=products, shoppingCart=shoppingCart, shirtsLen=shirtsLen,
                           shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/buy/")
def buy():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        products = db.execute("SELECT * FROM products WHERE id = :id", id=id)
        if products[0]["onSale"] == 1:
            price = products[0]["onSalePrice"]
        else:
            price = products[0]["price"]
        name = products[0]["name"]
        image = products[0]["image"]
        subTotal = qty * price
        db.execute(
            "INSERT INTO basket (id, qty, name, image, price, subTotal) VALUES (:id, :qty, :name, :image, :price, :subTotal)",
            id=id, qty=qty, name=name, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        products = db.execute("SELECT * FROM products ORDER BY name ASC")
        shirtsLen = len(products)
        return render_template("index.html", shoppingCart=shoppingCart, products=products, shopLen=shopLen,
                               shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session)


@app.route("/update/")
def update():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    qty = int(request.args.get('quantity'))
    if session:
        id = int(request.args.get('id'))
        db.execute("DELETE FROM basket WHERE id = :id", id=id)
        products = db.execute("SELECT * FROM products WHERE id = :id", id=id)
        if products[0]["onSale"] == 1:
            price = products[0]["onSalePrice"]
        else:
            price = products[0]["price"]
        name = products[0]["name"]
        image = products[0]["image"]
        subTotal = qty * price
        db.execute(
            "INSERT INTO basket (id, qty, name, image, price, subTotal) VALUES (:id, :qty, :name, :image, :price, :subTotal)",
            id=id, qty=qty, name=name, image=image, price=price, subTotal=subTotal)
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems,
                               display=display, session=session)


@app.route("/filter/")
def filter():
    if request.args.get('category'):
        query = request.args.get('category')
        products = db.execute("SELECT * FROM products WHERE category = :query ORDER BY name ASC", query=query)
    if request.args.get('sale'):
        query = request.args.get('sale')
        products = db.execute("SELECT * FROM products WHERE onSale = :query ORDER BY name ASC", query=query)
    if request.args.get('id'):
        query = int(request.args.get('id'))
        products = db.execute("SELECT * FROM products WHERE id = :query ORDER BY name ASC", query=query)
    if request.args.get('kind'):
        query = request.args.get('kind')
        products = db.execute("SELECT * FROM products WHERE kind = :query ORDER BY name ASC", query=query)
    if request.args.get('price'):
        query = request.args.get('price')
        products = db.execute("SELECT * FROM products ORDER BY onSalePrice ASC")
    shirtsLen = len(products)
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    if 'user' in session:
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
        return render_template("index.html", shoppingCart=shoppingCart, products=products, shopLen=shopLen,
                               shirtsLen=shirtsLen, total=total, totItems=totItems, display=display, session=session)
    return render_template("index.html", products=products, shoppingCart=shoppingCart, shirtsLen=shirtsLen,
                           shopLen=shopLen, total=total, totItems=totItems, display=display)


@app.route("/form/")
def form():
    return render_template("form.html")


@app.route("/checkout/")
def checkout():
    order = db.execute("SELECT * from basket")
    for item in order:
        db.execute("INSERT INTO purchases (uid, id, name, image, quantity) VALUES(:uid, :id, :name, :image, :quantity)",
                   uid=session["uid"], id=item["id"], name=item["name"], image=item["image"], quantity=item["qty"])
    db.execute("DELETE from basket")
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    return redirect('/')


@app.route("/remove/", methods=["GET"])
def remove():
    out = int(request.args.get("id"))
    db.execute("DELETE from basket WHERE id=:id", id=out)
    totItems, total, display = 0, 0, 0
    shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
    shopLen = len(shoppingCart)
    for i in range(shopLen):
        total += shoppingCart[i]["SUM(subTotal)"]
        totItems += shoppingCart[i]["SUM(qty)"]
    display = 1
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems,
                           display=display, session=session)


@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/new/", methods=["GET"])
def new():
    return render_template("new.html")


@app.route("/logged/", methods=["POST"])
def logged():
    user = request.form["username"].lower()
    pwd = request.form["password"]
    if user == "" or pwd == "":
        return render_template("login.html")
    query = "SELECT * FROM customers WHERE username = :user AND password = :pwd"
    rows = db.execute(query, user=user, pwd=pwd)

    if len(rows) == 1:
        session['user'] = user
        session['time'] = datetime.now()
        session['uid'] = rows[0]["id"]
    if 'user' in session:
        return redirect("/")
    return render_template("login.html", msg="Wrong username or password.")


@app.route("/history/")
def history():
    shoppingCart = []
    shopLen = len(shoppingCart)
    totItems, total, display = 0, 0, 0
    myShirts = db.execute("SELECT * FROM purchases WHERE uid=:uid", uid=session["uid"])
    myShirtsLen = len(myShirts)
    return render_template("history.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems,
                           display=display, session=session, myShirts=myShirts, myShirtsLen=myShirtsLen)


@app.route("/logout/")
def logout():
    db.execute("DELETE from basket")
    session.clear()
    return redirect("/")


@app.route("/register/", methods=["POST"])
def registration():
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm"]
    fname = request.form["fname"]
    lname = request.form["lname"]
    email = request.form["email"]
    rows = db.execute("SELECT * FROM customers WHERE username = :username ", username=username)
    if len(rows) > 0:
        return render_template("new.html", msg="Username already exists!")
    new = db.execute(
        "INSERT INTO customers (username, password, fname, lname, email) VALUES (:username, :password, :fname, :lname, :email)",
        username=username, password=password, fname=fname, lname=lname, email=email)
    return render_template("login.html")


@app.route("/cart/")
def cart():
    if 'user' in session:
        totItems, total, display = 0, 0, 0
        shoppingCart = db.execute("SELECT name, image, SUM(qty), SUM(subTotal), price, id FROM basket GROUP BY name")
        # Get variable values
        shopLen = len(shoppingCart)
        for i in range(shopLen):
            total += shoppingCart[i]["SUM(subTotal)"]
            totItems += shoppingCart[i]["SUM(qty)"]
    return render_template("cart.html", shoppingCart=shoppingCart, shopLen=shopLen, total=total, totItems=totItems,
                           display=display, session=session)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
