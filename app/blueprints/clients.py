from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Client

bp = Blueprint("clients", __name__)

@bp.route("/")
def list_clients():
    clients = Client.query.order_by(Client.created_at.desc()).all()
    return render_template("clients/list.html", clients=clients)

@bp.route("/create", methods=["GET", "POST"])
def create_client():
    if request.method == "POST":
        pharma = request.form.get("pharma")
        brand = request.form.get("brand")
        agency = request.form.get("agency")
        indication = request.form.get("indication")
        c = Client(pharma=pharma, brand=brand, agency=agency, indication=indication)
        db.session.add(c)
        db.session.commit()
        flash("Client created", "success")
        return redirect(url_for("clients.list_clients"))
    return render_template("clients/form.html")
