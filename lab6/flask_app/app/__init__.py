from flask import Flask

from config import Config
from app.extensions import db
from app.util.seeder import Seeder


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    db.create_all(app=app)

    Seeder.init(app, silence_mode=True)
    Seeder.seed_electro_scooter(10)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.scooters import bp as scooters_bp
    app.register_blueprint(scooters_bp, url_prefix="/scooter")

    return app
