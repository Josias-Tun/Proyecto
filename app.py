from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)

MONGO_URI = "mongodb+srv://josiastun024_db_user:$4APMJMAGPEJE@proyecto.xdcjiis.mongodb.net/"

client = MongoClient(MONGO_URI)
db = client["paqueteria"]

# ---------------- INICIO (ANTES ERA LOGIN) ----------------
@app.route("/")
def home():
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
        return redirect("/")

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
    return redirect("/")


# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    pedidos = list(db.pedidos.find())
    return render_template("admin.html", pedidos=pedidos)


if __name__ == "__main__":
    app.run(debug=True)
