from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('app.config.Config')

    # Initialize extensions
    CORS(app)

    # Import routes
    from . import routes
    routes.init_app(app)

    return app