from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from app.routes import main_routes, auth_routes, tournament_routes, profile_routes, chat_routes, admin_routes
    app.register_blueprint(main_routes)
    app.register_blueprint(auth_routes)
    app.register_blueprint(tournament_routes)
    app.register_blueprint(profile_routes)
    app.register_blueprint(chat_routes)
    app.register_blueprint(admin_routes)

    return app