from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .db import Database
import datetime
import pytz

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

    timezone = current_user.timezone
    index = 0
    for workout in workouts:
        timestamp = datetime.datetime.strptime(workout[3], "%Y-%m-%d %H:%M:%S.%f%z")
        timestamp = timestamp.astimezone(pytz.timezone(timezone))
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        workout = list(workout)
        workout[3] = str(timestamp)
        workout = tuple(workout)
        workouts[index] = workout
        index += 1
        
    return render_template('profile.html', workouts=workouts, name=current_user.name)

@main.route('/newlog/')
@login_required
def log_workout():
    workout_id = request.args.get("workout_id")
    
    db = Database()

    query = "SELECT name FROM workout WHERE id = " + str(workout_id)
    name = db.select(query)
    if name == []:
        name = "New Workout"
    else:
        name = name[0][0]

    query = "SELECT * FROM set WHERE workout_id = " + str(workout_id)
    sets = db.select(query)

    return render_template('newlog.html', name=name, sets=sets, workout_id=workout_id)

@main.route('/newlog/', methods=['POST'])
def log_post():
    names = request.form.getlist('name')
    types = request.form.getlist('typ')
    weights = request.form.getlist('weight')
    reps = request.form.getlist('reps')
    workout_id = int(request.form.get('workout_id'))

    name = ""
    for typ in types:
        if typ not in name:
            if name == "":
                name = name + typ
            else:
                name = name + "/" + typ
    name = name + " Workout"

    timestamp = str(pytz.utc.localize(datetime.datetime.utcnow())) + "00"

    db = Database()
    
    if workout_id == 0: 
        db.add(
        """INSERT INTO workout (user_id, name, timestamp) 
            VALUES(%s, %s, %s)""", 
            (current_user.id, name, timestamp)
        )

        workout_id = db.select("SELECT LASTVAL()")[0][0]

    else:
        query = "DELETE FROM set WHERE workout_id = " + str(workout_id)
        db.delete(query)

        db.update("UPDATE workout SET name = %s WHERE id = %s", (name, str(workout_id)))

    for x in range(len(names)):
        db.add(
            """INSERT INTO set (name, typ, weight, reps, user_id, workout_id) 
            VALUES(%s, %s, %s, %s, %s, %s)""", 
            (names[x], types[x], weights[x], reps[x], current_user.id, workout_id)
        )

    return redirect(url_for('main.profile'))