from flask import Flask
import os
from routes import main


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'for dev')
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    # Database Setup
    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["SQLALCHEMY_DATABASE_URI"] =\
    "sqlite:///" + os.path.join(basedir, "pelican.db")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from extensions import db
    db.init_app(app)
    with app.app_context():
        db.create_all()

    app.register_blueprint(main)

    return app