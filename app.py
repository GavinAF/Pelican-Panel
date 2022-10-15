from flask import Flask
import os
from routes import main

def create_app():
    app = Flask(__name__)

    # Set secret key
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'for dev')

    # Make templates auto-reload
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.register_blueprint(main)

    return app