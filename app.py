
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "secret123"

# URI (puedes moverla a variables de entorno luego)
MONGO_URI = "MONGO_URI = "mongodb+srv://josiastun024_db_user:$4APMJMAGPEJE@proyecto.xdcjiis.mongodb.net/paqueteria?retryWrites=true&w=majority""

client = MongoClient(MONGO_URI)
db = client["paqueteria"]

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = db.usuarios.find_one({
            "username": request.form["username"],
            "password": request.form["password"]
        })
        if user:
            session["user"] = user["username"]
            return redirect("/dashboard")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    pedidos = list(db.pedidos.find())
    return render_template("dashboard.html", pedidos=pedidos)

# ---------------- CREAR PEDIDO ----------------
@app.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        pedido = {
            "cliente": request.form["cliente"],
            "direccion": request.form["direccion"],
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
    pedido = db.pedidos.find_one({"_id": ObjectId(id)})
    return render_template("seguimiento.html", pedido=pedido)

# ---------------- CANCELAR ----------------
@app.route("/cancelar/<id>")
def cancelar(id):
    db.pedidos.update_one(
        {"_id": ObjectId(id)},
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
    pedidos = list(db.pedidos.find())
    return render_template("admin.html", pedidos=pedidos)

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
