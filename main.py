from flask import Blueprint, render_template, request
from . import db
from .models import ExerciseModel

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/exercise', methods=['POST', 'GET'])
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