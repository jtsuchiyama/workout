from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import ExerciseModel, Set

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/newlog')
@login_required
def log_workout():
    return render_template('newlog.html')

@main.route('/newlog', methods=['POST'])
def log_post():
    name = request.form.get('name')
    typ = request.form.get('typ')
    weight = request.form.get('weight')
    reps = request.form.get('reps')
    completion = request.form.get('completion')

    if completion == None:
        completion = "false"

    new_log = Set(name=name, typ=typ, weight=weight, reps=reps, completion=completion)
    db.session.add(new_log)
    db.session.commit()

    return redirect(url_for('main.profile'))


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