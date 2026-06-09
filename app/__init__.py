"""
Application factory and initialization.
This module creates and configures the Flask application instance.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import config
import logging
from logging.handlers import RotatingFileHandler
import os

# Initialize extensions
# These will be attached to the app in create_app()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_name='development'):
    """
    Application factory pattern.
    Creates and configures the Flask application.
    
    Args:
        config_name (str): Configuration to use ('development', 'testing', 'production')
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import main_bp, auth_bp, provider_bp, client_bp, api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(provider_bp, url_prefix='/provider')
    app.register_blueprint(client_bp, url_prefix='/client')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # Configure logging
    configure_logging(app)
    
    # Create upload folder if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    return app


def configure_logging(app):
    """
    Configure application logging.
    Logs are written to file in production and to stdout in development.
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure file handler
        file_handler = RotatingFileHandler(
            'logs/servicelink.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('ServiceLink startup')


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.
    Loads a user from the database given the user ID stored in the session.
    
    Args:
        user_id (str): User ID from session
    
    Returns:
        User: User object or None
    """
    from app.models import User
    return User.query.get(int(user_id))
