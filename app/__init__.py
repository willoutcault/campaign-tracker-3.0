from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, generate_csrf
from dotenv import load_dotenv
from .config import Config

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()

def create_app():
    load_dotenv()  # <-- ensures SECRET_KEY from .env is available when using python run.py
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    @app.context_processor
    def inject_csrf():
        return dict(csrf_token=generate_csrf)

    from .blueprints.clients import bp as clients_bp
    from .blueprints.contracts import bp as contracts_bp
    from .blueprints.target_lists import bp as tl_bp

    app.register_blueprint(clients_bp, url_prefix="/clients")
    app.register_blueprint(contracts_bp, url_prefix="/contracts")
    app.register_blueprint(tl_bp, url_prefix="/target-lists")

    @app.route("/")
    def index():
        return render_template("base.html")

    return app
