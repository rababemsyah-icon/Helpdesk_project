from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Import des modèles pour que SQLAlchemy/Alembic les détectent
    from app import models

    # Enregistrer les blueprints
    from app.auth.routes import auth_bp
    from app.tickets.routes import tickets_bp
    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(admin_bp)

    # --- AJOUT IMPORTANT : La route de la page d'accueil ---
    @app.route('/')
    def home():
        return "Bienvenue sur mon Helpdesk !"

    return app