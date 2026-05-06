from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

MONGO_URI = "mongodb+srv://josiastun024_db_user:$4APMJMAGPEJE@proyecto.xdcjiis.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["paqueteria"]

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.usuarios.find_one({
            "username": username,
            "password": password
        })

        if user:
            session["user"] = user["username"]
            return redirect("/dashboard")
        else:
            error = "Usuario o contraseña incorrectos"

    return render_template("login.html", error=error)


# ---------------- REGISTRO ----------------
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        user = {
            "username": request.form["username"],
            "password": request.form["password"]
        }
        db.usuarios.insert_one(user)
        return redirect("/")

    return render_template("registro.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    pedidos = list(db.pedidos.find({
        "usuario": session["user"]
    }))

    return render_template("dashboard.html", pedidos=pedidos)


# ---------------- CREAR PEDIDO ----------------
@app.route("/crear", methods=["GET", "POST"])
def crear():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        pedido = {
            "cliente": request.form["cliente"],
            "direccion": request.form["direccion"],
            "usuario": session["user"],  # 🔥 clave
            "estado": "Creado",
            "historial": [
                {
                    "estado": "Creado",
                    "fecha": datetime.now()
                }
            ]
        }
        db.pedidos.insert_one(pedido)
        return redirect("/dashboard")

    return render_template("crear.html")


# ---------------- SEGUIMIENTO ----------------
@app.route("/seguimiento/<id>")
def seguimiento(id):
    if "user" not in session:
        return redirect("/")

    pedido = db.pedidos.find_one({
        "_id": ObjectId(id),
        "usuario": session["user"]
    })

    return render_template("seguimiento.html", pedido=pedido)


# ---------------- CANCELAR ----------------
@app.route("/cancelar/<id>")
def cancelar(id):
    if "user" not in session:
        return redirect("/")

    db.pedidos.update_one(
        {
            "_id": ObjectId(id),
            "usuario": session["user"]  # 🔥 seguridad
        },
        {
            "$set": {"estado": "Cancelado"},
            "$push": {
                "historial": {
                    "estado": "Cancelado",
                    "fecha": datetime.now()
                }
            }
        }
    )
    return redirect("/dashboard")


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")

    pedidos = list(db.pedidos.find())
    return render_template("admin.html", pedidos=pedidos)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
