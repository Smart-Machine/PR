import os

from flask import request, render_template
from app.extensions import db
from app.scooters import bp
from app.models.electro_scooter import ElectroScooter


@bp.route("/", methods=["GET"])
def index():
    electro_scooters = ElectroScooter.query.all()
    return render_template("electro_scooters/index.html", electro_scooters=electro_scooters)


@bp.route("/<int:id>", methods=["GET"])
def get_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)
    if not electro_scooter:
        return render_template("notfound.html")
    return render_template("electro_scooters/index.html", electro_scooters=[electro_scooter])


@bp.route("/", methods=["POST"])
def create_scooter():
    data = request.get_json()
    electro_scooter = ElectroScooter(
        data.get("name"), data.get("battery_level"))

    db.session.add(electro_scooter)
    db.session.commit()

    return render_template("electro_scooters/index.html", electro_scooters=[electro_scooter])


@bp.route("/<int:id>", methods=["PUT"])
def update_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)
    if not electro_scooter:
        return render_template("notfound.html")

    data = request.get_json()

    if electro_scooter:
        electro_scooter.name = data.get("name", electro_scooter.name)
        electro_scooter.battery_level = data.get(
            "battery_level", electro_scooter.battery_level)
        db.session.commit()

        return render_template("electro_scooters/index.html", electro_scooters=[electro_scooter])
    return render_template("notfound.html")


@bp.route("/<int:id>", methods=["DELETE"])
def delete_scooter_by_id(id):
    electro_scooter = ElectroScooter.query.get(id)

    auth = request.headers.get("Authorization")
    if auth == os.getenv("AUTHORIZATION_KEY") and electro_scooter:
        db.session.delete(electro_scooter)
        db.session.commit()
        return render_template("electro_scooters/index.html", electro_scooters=[electro_scooter])
    
    return render_template("notfound.html")
