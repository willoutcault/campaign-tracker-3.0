from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
import uuid
from .. import db
from ..models import Client, Contract, Campaign, Program, Placement, ProgramTargetList, TargetList

bp = Blueprint("contracts", __name__)

# Contracts
@bp.route("/")
def list_contracts():
    rows = Contract.query.order_by(Contract.created_at.desc()).all()
    return render_template("contracts/list.html", rows=rows)

@bp.route("/create", methods=["GET", "POST"])
def create_contract():
    if request.method == "POST":
        name = request.form.get("name")
        client_id = int(request.form.get("client_id"))
        start = request.form.get("flight_start") or None
        end = request.form.get("flight_end") or None
        c_uid = uuid.uuid4().hex[:12]
        obj = Contract(
            name=name,
            client_id=client_id,
            flight_start=date.fromisoformat(start) if start else None,
            flight_end=date.fromisoformat(end) if end else None,
            contract_uid=c_uid,
        )
        db.session.add(obj)
        db.session.commit()
        flash(f"Contract created with ID {obj.contract_uid}", "success")
        return redirect(url_for("contracts.list_contracts"))

    clients = Client.query.order_by(Client.pharma.asc()).all()
    return render_template("contracts/forms/contract_form.html", clients=clients)

@bp.route("/<int:contract_id>")
def view_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    return render_template("contracts/detail.html", contract=contract)

@bp.route("/<int:contract_id>/edit", methods=["GET", "POST"])
def edit_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        client_id = request.form.get("client_id")
        start = request.form.get("flight_start") or None
        end = request.form.get("flight_end") or None

        if not name or not client_id:
            flash("Name and Client are required.", "danger")
            return redirect(url_for("contracts.edit_contract", contract_id=contract.id))

        contract.name = name
        contract.client_id = int(client_id)
        contract.flight_start = (date.fromisoformat(start) if start else None)
        contract.flight_end = (date.fromisoformat(end) if end else None)

        db.session.commit()
        flash("Contract updated.", "success")
        return redirect(url_for("contracts.view_contract", contract_id=contract.id))

    # GET: render form prefilled
    clients = Client.query.order_by(Client.pharma.asc()).all()
    return render_template(
        "contracts/forms/contract_edit_form.html",
        contract=contract,
        clients=clients
    )

# Campaigns
@bp.route("/<int:contract_id>/campaigns/create", methods=["GET","POST"])
def create_campaign(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if request.method == "POST":
        name = request.form.get("name")
        camp = Campaign(contract_id=contract.id, name=name)
        db.session.add(camp)
        db.session.commit()
        flash("Campaign created", "success")
        return redirect(url_for("contracts.view_contract", contract_id=contract.id))
    return render_template("contracts/forms/campaign_form.html", contract=contract)

@bp.route("/campaigns/<int:campaign_id>/edit", methods=["GET", "POST"])
def edit_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        notes = (request.form.get("notes") or "").strip()

        if not name:
            flash("Campaign name is required.", "danger")
            return redirect(url_for("contracts.edit_campaign", campaign_id=campaign.id))

        campaign.name = name
        campaign.notes = notes
        db.session.commit()
        flash("Campaign updated.", "success")
        return redirect(url_for("contracts.view_contract", contract_id=campaign.contract_id))

    # GET: render form prefilled
    return render_template(
        "contracts/forms/campaign_edit_form.html",
        campaign=campaign
    )

# Programs
@bp.route("/campaigns/<int:campaign_id>/programs/create", methods=["GET","POST"])
def create_program(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    client_id = campaign.contract.client_id
    if request.method == "POST":
        name = request.form.get("name")
        status = request.form.get("status")
        start = request.form.get("start_date") or None
        end = request.form.get("end_date") or None
        p = Program(
            campaign_id=campaign.id,
            name=name,
            status=status or "DRAFT",
            start_date=date.fromisoformat(start) if start else None,
            end_date=date.fromisoformat(end) if end else None,
        )
        db.session.add(p)
        db.session.commit()
        flash("Program created", "success")
        return redirect(url_for("contracts.view_contract", contract_id=campaign.contract_id))

    lists = TargetList.query.join(TargetList.clients).filter(Client.id == client_id).all()
    placements = Placement.query.order_by(Placement.name.asc()).all()
    return render_template("contracts/forms/program_form.html", campaign=campaign, lists=lists, placements=placements)

@bp.route("/programs/<int:program_id>/attach-target-list", methods=["POST"])
def attach_target_list(program_id):
    program = Program.query.get_or_404(program_id)
    tl_id = int(request.form.get("target_list_id"))
    ptl = ProgramTargetList(program_id=program.id, target_list_id=tl_id)
    db.session.add(ptl)
    db.session.commit()
    flash("Target list attached", "success")
    return redirect(url_for("contracts.view_contract", contract_id=program.campaign.contract_id))

@bp.route("/programs/<int:program_id>/map-placement", methods=["POST"])
def map_placement(program_id):
    program = Program.query.get_or_404(program_id)
    placement_id = int(request.form.get("placement_id"))
    placement = Placement.query.get_or_404(placement_id)
    if not program.placements.filter_by(id=placement.id).first():
        program.placements.append(placement)
        db.session.commit()
    flash("Placement mapped to program", "success")
    return redirect(url_for("contracts.view_contract", contract_id=program.campaign.contract_id))

# Placements (reusable)
@bp.route("/placements/create", methods=["GET","POST"])
def create_placement():
    if request.method == "POST":
        name = request.form.get("name")
        channel = request.form.get("channel")
        pl = Placement(name=name, channel=channel)
        db.session.add(pl)
        db.session.commit()
        flash("Placement created", "success")
        return redirect(url_for("contracts.list_contracts"))
    return render_template("contracts/forms/placement_form.html")
