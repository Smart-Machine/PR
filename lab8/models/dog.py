from .database import db

class Dog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    breed = db.Column(db.String(100), nullable=False)

    def __init__(self, name, breed):
        self.name = name
        self.breed = breed 