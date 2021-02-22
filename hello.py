from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:poke3271@localhost/Exercise'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template("index.html")

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

@app.route('/exercise', methods=['POST', 'GET'])
def handle_exercise():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            new_exercise = ExerciseModel(name=data['name'], typ=data['typ'])
            db.session.add(new_exercise)
            db.session.commit()
            return {"message": f"exercise {new_exercise.name} has been created successfully."}
        else:
            return {"error": "The request payload is not in JSON format"}

    elif request.method == 'GET':
        exercises = ExerciseModel.query.all()
        results = [
            {
                "name": exercise.name,
                "typ": exercise.typ,
            } for exercise in exercises]

        return {"count": len(results), "exercises": results}

