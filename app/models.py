from datetime import datetime
from enum import Enum
from . import db

class UseCaseEnum(str, Enum):
    RFP = "RFP"
    PROGRAM_MAPPING = "PROGRAM_MAPPING"
    INTERNAL = "INTERNAL"

programs_placements = db.Table(
    "programs_placements",
    db.Column("program_id", db.Integer, db.ForeignKey("programs.id"), primary_key=True),
    db.Column("placement_id", db.Integer, db.ForeignKey("placements.id"), primary_key=True),
)

client_target_lists = db.Table(
    "client_target_lists",
    db.Column("client_id", db.Integer, db.ForeignKey("clients.id"), primary_key=True),
    db.Column("target_list_id", db.Integer, db.ForeignKey("target_lists.id"), primary_key=True),
)

class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    pharma = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=False)
    agency = db.Column(db.String(120))
    indication = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    contracts = db.relationship("Contract", backref="client", lazy=True)
    target_lists = db.relationship(
        "TargetList",
        secondary=client_target_lists,
        back_populates="clients",
        lazy="dynamic",
    )

class Contract(db.Model):
    __tablename__ = "contracts"
    id = db.Column(db.Integer, primary_key=True)
    contract_uid = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    flight_start = db.Column(db.Date)
    flight_end = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaigns = db.relationship("Campaign", backref="contract", lazy=True, cascade="all, delete-orphan")

class Campaign(db.Model):
    __tablename__ = "campaigns"
    id = db.Column(db.Integer, primary_key=True)
    contract_id = db.Column(db.Integer, db.ForeignKey("contracts.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text)

    programs = db.relationship("Program", backref="campaign", lazy=True, cascade="all, delete-orphan")

class Program(db.Model):
    __tablename__ = "programs"
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaigns.id"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default="DRAFT")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    placements = db.relationship(
        "Placement",
        secondary=programs_placements,
        back_populates="programs",
        lazy="dynamic",
    )

    program_target_lists = db.relationship(
        "ProgramTargetList",
        backref="program",
        lazy=True,
        cascade="all, delete-orphan",
    )

class Placement(db.Model):
    __tablename__ = "placements"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    channel = db.Column(db.String(80))  # email, app, web, dx, etc.
    status = db.Column(db.String(50), default="PLANNED")
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    programs = db.relationship(
        "Program",
        secondary=programs_placements,
        back_populates="placements",
        lazy="dynamic",
    )

class TargetList(db.Model):
    __tablename__ = "target_lists"
    id = db.Column(db.Integer, primary_key=True)
    list_uid = db.Column(db.String(40), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    use_case = db.Column(db.Enum(UseCaseEnum), nullable=False)
    s3_key = db.Column(db.String(512), nullable=False)
    file_ext = db.Column(db.String(16))
    uploaded_by = db.Column(db.String(120))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    clients = db.relationship(
        "Client",
        secondary=client_target_lists,
        back_populates="target_lists",
        lazy="dynamic",
    )

class ProgramTargetList(db.Model):
    __tablename__ = "program_target_lists"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    target_list_id = db.Column(db.Integer, db.ForeignKey("target_lists.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    target_list = db.relationship("TargetList")
