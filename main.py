from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from .db import Database
import datetime
import pytz

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/profile")
@login_required
def profile():
    db = Database()

    query = "SELECT * FROM workout WHERE user_id = " + str(current_user.id)
    workouts = db.select(query)

    timezone = current_user.timezone
    index = 0
    for workout in workouts:
        # Read the timestamps from the database and shift to the user's timezone
        timestamp = datetime.datetime.strptime(workout[3], "%Y-%m-%d %H:%M:%S.%f%z")
        timestamp = timestamp.astimezone(pytz.timezone(timezone))
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        # Change between list and tuple since tuples are not editable
        workout = list(workout)
        workout[3] = str(timestamp)
        workout = tuple(workout)
        workouts[index] = workout
        index += 1
        
    return render_template("profile.html", workouts=workouts, name=current_user.name)

@main.route("/newlog/")
@login_required
def log_workout():
    workout_id = request.args.get("workout_id")
    
    db = Database()

    query = "SELECT name FROM workout WHERE id = " + str(workout_id)
    name = db.select(query)
    if name == []:
        # Sets the name if the workout being created for the first time
        name = "New Workout"
    else:
        # Grabs the name if the workout is old
        name = name[0][0]

    # Query the sets in the workout to be rendered
    query = "SELECT * FROM set WHERE workout_id = " + str(workout_id)
    sets = db.select(query)

    return render_template("newlog.html", name=name, sets=sets, workout_id=workout_id)

@main.route("/newlog/", methods=["POST"])
def log_post():
    names = request.form.getlist("name")
    types = request.form.getlist("typ")
    weights = request.form.getlist("weight")
    reps = request.form.getlist("reps")
    sets = request.form.getlist("sets")
    workout_id = int(request.form.get("workout_id"))


    # Creates the name for the workout
    name = ""
    for typ in types:
        if typ not in name:
            if name == "":
                name = name + typ
            else:
                name = name + "/" + typ
    name = name + " Workout"

    # Creates the timestamp relative to a timezone
    timestamp = str(pytz.utc.localize(datetime.datetime.utcnow())) + "00"

    db = Database()
    
    if workout_id == 0: 
        # If the workout is being created for the first time, then add the workout to the database
        db.add(
        """INSERT INTO workout (user_id, name, timestamp) 
            VALUES(%s, %s, %s)""", 
            (current_user.id, name, timestamp)
        )

        workout_id = db.select("SELECT LASTVAL()")[0][0]

    else:
        # If the workout is old, then delete the old sets from the workout and update the workout information
        query = "DELETE FROM set WHERE workout_id = " + str(workout_id)
        db.delete(query)

        db.update("UPDATE workout SET name = %s WHERE id = %s", (name, str(workout_id)))

    # Adds all of the sets to the database
    for x in range(len(names)):
        db.add(
            """INSERT INTO set (name, typ, weight, reps, user_id, workout_id, sets) 
            VALUES(%s, %s, %s, %s, %s, %s, %s)""", 
            (names[x], types[x], weights[x], reps[x], current_user.id, workout_id, sets[x])
        )

    return redirect(url_for("main.profile"))

@main.route("/deletelog/")
def del_workout():
    workout_id = request.args.get("workout_id")
    print(workout_id)
    
    db = Database()

    query = "DELETE FROM workout WHERE id = " + str(workout_id)
    db.delete(query)
    
    query = "DELETE FROM set WHERE workout_id = " + str(workout_id)
    db.delete(query)

    return redirect(url_for("main.profile"))
