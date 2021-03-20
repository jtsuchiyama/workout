from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .db import Database

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    db = Database()

    query = "SELECT * FROM workout WHERE user_id = " + str(current_user.id)
    workouts = db.select(query)

    return render_template('profile.html', workouts=workouts, name=current_user.name)

@main.route('/newlog/<int:workout_id>')
@login_required
def log_workout(workout_id):
    db = Database()

    query = "SELECT name FROM workout WHERE id = " + str(workout_id)
    name = db.select(query)
    if name == []:
        name = "New Workout"
    else:
        name = name[0][0]

    query = "SELECT * FROM set WHERE workout_id = " + str(workout_id)
    sets = db.select(query)

    return render_template('newlog.html', name=name, sets=sets)

@main.route('/newlog/', methods=['POST'])
def log_post():
    names = request.form.getlist('name')
    types = request.form.getlist('typ')
    weights = request.form.getlist('weight')
    reps = request.form.getlist('reps')

    name = ""
    for typ in types:
        if typ not in name:
            if name == "":
                name = name + typ
            else:
                name = name + "/" + typ
    name = name + " Workout"

    timestamp = "hi"

    db = Database()
    db.add(
        """INSERT INTO workout (user_id, name, timestamp) 
            VALUES(%s, %s, %s)""", 
            (current_user.id, name, timestamp)
    )
    
    workout_id = db.select("SELECT LASTVAL()")[0][0]

    for x in range(len(names)):
        db.add(
            """INSERT INTO set (name, typ, weight, reps, user_id, workout_id) 
            VALUES(%s, %s, %s, %s, %s, %s)""", 
            (names[x], types[x], weights[x], reps[x], current_user.id, workout_id)
        )

    return redirect(url_for('main.profile'))