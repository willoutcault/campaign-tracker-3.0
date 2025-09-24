from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from .. import db
from ..models import TargetList, Client, UseCaseEnum
from ..storage_s3 import S3Storage
import uuid

bp = Blueprint("target_lists", __name__)

@bp.route("/")
def list_target_lists():
    rows = TargetList.query.order_by(TargetList.uploaded_at.desc()).all()
    return render_template("target_lists/list.html", rows=rows)

@bp.route("/upload", methods=["GET","POST"])
def upload_target_list():
    if request.method == "POST":
        title = request.form.get("title")
        use_case = request.form.get("use_case")
        client_ids = request.form.getlist("client_ids")
        file = request.files.get("file")
        if not file:
            flash("No file selected", "danger")
            return redirect(url_for("target_lists.upload_target_list"))

        storage = S3Storage(
            bucket=current_app.config["AWS_S3_BUCKET"],
            region=current_app.config["AWS_REGION"],
            access_key=current_app.config.get("AWS_ACCESS_KEY_ID"),
            secret_key=current_app.config.get("AWS_SECRET_ACCESS_KEY"),
            prefix=current_app.config.get("AWS_S3_PREFIX", ""),
        )
        key = storage.put_file(file, logical_name=file.filename)
        tl = TargetList(
            list_uid=uuid.uuid4().hex[:12],
            title=title,
            use_case=UseCaseEnum(use_case),
            s3_key=key,
            file_ext=(file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else None),
            uploaded_by="system",
        )
        db.session.add(tl)
        db.session.flush()

        if client_ids:
            for cid in client_ids:
                client = Client.query.get(int(cid))
                if client and not client.target_lists.filter_by(id=tl.id).first():
                    client.target_lists.append(tl)
        db.session.commit()
        flash("Target list uploaded", "success")
        return redirect(url_for("target_lists.list_target_lists"))

    clients = Client.query.order_by(Client.pharma.asc()).all()
    return render_template("target_lists/upload.html", clients=clients, use_cases=list(UseCaseEnum))
