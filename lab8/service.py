import requests
import random
import time
import sys

from flask import Flask
from flask import request
from flask import jsonify

from raft.util.raft import RAFTFactory
from models.dog import Dog 
from models.database import db


service_info = {
    "host": "127.0.0.1",
    "port": int(sys.argv[1])
}

time.sleep(random.randint(1, 3))
node = RAFTFactory(service_info).create_server()
node.string()

cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

db_name = 'dogs'
if not node.leader:
    db_name += str(random.randint(1, 3))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_name}.db"
db.init_app(app)


@app.route("/api/dog", methods=["GET"])
def get_dogs():
    dogs = dog.query.all()
    response = {"dog": []}

    if len(dogs) != 0:
        for dog in dogs:
            response["dog"].append({
                "id": dog.id,
                "name": dog.name,
                "breed": dog.breed
            })
        return jsonify(response), 200

    else:
        return jsonify({"error": "No dogs in the database"}), 404


@app.route("/api/dog/<int:dog_id>", methods=["GET"])
def get_dog_by_id(dog_id):
    dog = Dog.query.get(dog_id)

    if dog is not None:
        return jsonify({
            "id": dog.id,
            "name": dog.name,
            "breed": dog.breed,
        }), 200
    else:
        return jsonify({"error": "dog not found"}), 404


@app.route("/api/dog", methods=["POST"])
def create_dog():
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            data = request.get_json()
            name = data.get("name")
            breed = data.get("breed")
            dog = Dog(name=name, breed=breed)

            db.session.add(dog)
            db.session.commit()

            if node.leader:
                for follower in node.followers:
                    requests.post(f"http://{follower['host']}:{follower['port']}/api/dog",
                                  json=request.json,
                                  headers={"Token": "Leader"})

            return jsonify({"message": "dog created successfully"}), 201
        except KeyError:
            return jsonify({"error": "Invalid request data"}), 400


@app.route("/api/dog/<int:dog_id>", methods=["PUT"])
def update_dog_by_id(dog_id):
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            dog = Dog.query.get(dog_id)
            if dog is not None:
                data = request.get_json()

                dog.name = data.get("name", dog.name)
                dog.breed = data.get("breed", dog.breed)

                db.session.commit()

                if node.leader:
                    for follower in node.followers:
                        requests.put(f"http://{follower['host']}:{follower['port']}/api/dog/{dog_id}",
                                     json=request.json,
                                     headers={"Token": "Leader"})

                return jsonify({"message": "dog updated successfully"}), 200
            else:
                return jsonify({"error": "dog not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@app.route("/api/dog/<int:dog_id>", methods=["DELETE"])
def delete_dog_by_id(dog_id):
    headers = dict(request.headers)
    if not node.leader and headers.get("Token") != "Leader":
        return {
            "message": "Access denied!"
        }, 403
    else:
        try:
            dog = Dog.query.get(dog_id)
            if dog is not None:
                password = request.headers.get("Auth")

                if password == "confirm-deletion":
                    db.session.delete(dog)
                    db.session.commit()

                    if node.leader:
                        for follower in node.followers:
                            requests.delete(f"http://{follower['host']}:{follower['port']}/api/dog/{dog_id}",
                                            headers={"Token": "Leader", "Auth": "confirm-deletion"})

                    return jsonify({"message": "dog deleted successfully"}), 200
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            else:
                return jsonify({"error": "dog not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(
        host=service_info["host"],
        port=service_info["port"]
    )
