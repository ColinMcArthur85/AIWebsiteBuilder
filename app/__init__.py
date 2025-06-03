from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Load configuration
    # Import the default configuration bundled with the project.  The
    # original code attempted to load ``app.config.Config`` which
    # requires the presence of a ``config.py`` file.  However the
    # repository only ships ``config_template.py``.  Loading the
    # non‑existent module would raise ``ModuleNotFoundError`` and the
    # application would fail to start.  Use the template configuration
    # by default so the app can run out‑of‑the‑box.
    app.config.from_object('app.config_template.Config')

    # Initialize extensions
    CORS(app)

    # Import routes
    from . import routes
    routes.init_app(app)

    return app
