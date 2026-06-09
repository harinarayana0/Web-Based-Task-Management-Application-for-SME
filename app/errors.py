"""
Error handlers for ServiceLink application.
Provides custom error pages and logging for common HTTP errors.
"""

from flask import render_template
import logging


def register_error_handlers(app):
    """
    Register error handlers for the application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        app.logger.warning(f'404 error: {error}')
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        app.logger.error(f'500 error: {error}')
        # Rollback database session in case of error
        from app import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 Forbidden errors"""
        app.logger.warning(f'403 error: {error}')
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        app.logger.warning(f'400 error: {error}')
        return render_template('errors/400.html'), 400
