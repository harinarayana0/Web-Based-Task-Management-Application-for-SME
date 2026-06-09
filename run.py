"""
Application entry point for ServiceLink.
This file initializes and runs the Flask application.
"""

import os
from app import create_app, db
from app.models import User, Service, Booking, Review

# Get configuration from environment variable, default to 'development'
config_name = os.getenv('FLASK_CONFIG', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """
    Creates a shell context for Flask CLI.
    Automatically imports database and models for easier debugging.
    """
    return {
        'db': db,
        'User': User,
        'Service': Service,
        'Booking': Booking,
        'Review': Review
    }


@app.cli.command()
def test():
    """
    Run the unit tests.
    Usage: flask test
    """
    import pytest
    pytest.main(['-v', 'tests/'])


@app.cli.command()
def init_db():
    """
    Initialize the database.
    Usage: flask init-db
    """
    db.create_all()
    print("Database initialized successfully!")


@app.cli.command()
def seed_db():
    """
    Seed the database with sample data.
    Usage: flask seed-db
    """
    from scripts.seed_data import seed_database
    seed_database()
    print("Database seeded successfully!")


if __name__ == '__main__':
    # Run the application
    # Debug mode is controlled by configuration
    app.run(host='0.0.0.0', port=5000)
