from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    #enabling Cors
    CORS(app)
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Initialize SQLAlchemy and Migrate
    db.init_app(app)
    migrate.init_app(app, db)

    
    # Import models to register them with SQLAlchemy
    with app.app_context():
        from app.models import User, Order, Supplier, Entity, Role
        # db.create_all()  # Uncomment only if not using migrations

        # Import routes
        from app import routes

    return app
