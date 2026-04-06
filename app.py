"""Flask application factory and entry point.

Creates and configures the Flask app, initializes Firebase,
and registers all route blueprints.
"""

from flask import Flask
from config import Config
from services.firebase_client import initialize_firebase


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns:
        A fully configured Flask app instance with all blueprints registered.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Firebase Admin SDK
    try:
        initialize_firebase(app.config["FIREBASE_CREDENTIALS"])
    except Exception as e:
        app.logger.error(f"Failed to initialize Firebase: {e}")

    # Register blueprints
    from routes.main_routes import main_bp
    from routes.student_routes import student_bp
    from routes.export_routes import export_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp, url_prefix="/students")
    app.register_blueprint(export_bp)

    # Context processor — inject config values into all templates
    @app.context_processor
    def inject_globals():
        return {
            "departments": Config.DEPARTMENTS,
            "years": [1, 2, 3, 4],
            "app_name": "SNU-ERP V2",
        }

    # Error boundaries
    from flask import render_template

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app


# Entry point for development
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
