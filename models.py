from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class ExerciseModel(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    typ = db.Column(db.String())

    def __init__(self, name, typ):
        self.name = name
        self.typ = typ

    def __repr__(self):
        return f"<Car {self.name}>"