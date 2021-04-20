from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from db import Database
import datetime
import pytz

import mpld3



main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route("/workouts")
@login_required
def workouts():
    db = Database()

    query = "SELECT * FROM workout WHERE user_id = " + str(current_user.id)
    workouts = db.select(query)

    timezone = current_user.timezone
    index = 0
    for workout in workouts:
        # Read the timestamps from the database and shift to the user's timezone
        timestamp = datetime.datetime.strptime(workout[3], "%Y-%m-%d %H:%M:%S.%f%z")
        timestamp = timestamp.astimezone(pytz.timezone(timezone))
        timestamp = timestamp.strftime("%m-%d-%Y %H:%M")
        

        # Change between list and tuple since tuples are not editable
        workout = list(workout)
        workout[3] = str(timestamp)
        workout = tuple(workout)
        workouts[index] = workout
        index += 1
        
    return render_template("workouts.html", workouts=workouts, name=current_user.name)

@main.route("/log/", methods=["GET"])
@login_required
def log_workout():
    workout_id = request.args.get("workout_id")

    db = Database()

    query = "SELECT EXISTS(SELECT 1 FROM workout WHERE id = " + str(workout_id) + ")"
    workout_exist = db.select(query)
    if workout_exist[0][0] == False:
        # Ensures that the next available workout ID is used
        workout_id = 0

    query = "SELECT user_id FROM workout WHERE id = " + str(workout_id)
    user_id = db.select(query)
    if user_id != []:
        # If the workout is not new
        user_id = db.select(query)
        user_id = user_id[0][0] # Reformat the query result to get the user_id associated with the workout
        if int(user_id) != current_user.id:
            # If the current user does not own the workout, then redirect them
            flash("Do not attempt to access other user's workouts")
            return redirect(url_for("main.workouts"))

    query = "SELECT * FROM workout WHERE user_id = " + str(current_user.id)
    workouts = db.select(query)

    query = "SELECT name FROM workout WHERE id = " + str(workout_id)
    name = db.select(query)
    if name == []:
        # Sets the name if the workout being created for the first time
        name = "New Workout"
    else:
        # Grabs the name if the workout is old
        name = name[0][0]

    query = "SELECT * FROM set WHERE workout_id = " + str(workout_id)
    sets = db.select(query)

    query = "SELECT * FROM run WHERE workout_id = " + str(workout_id)
    runs = db.select(query)

    sets = sets + runs

    return render_template("log.html", name=name, sets=sets, workout_id=workout_id, workouts=workouts)

@main.route("/log/", methods=["POST"])
@login_required
def log_post():
    if "load" in request.form:
        # If importing a workout into a new workout
        workout_id = request.form.get("workout_id")
        import_id = request.form.get("import_id")

        db = Database()

        query = "SELECT EXISTS(SELECT 1 FROM workout WHERE id = " + str(workout_id) + ")"
        workout_exist = db.select(query)
        if workout_exist[0][0] == False:
            # Ensures that the next available workout ID is used
            workout_id = 0

        query = "SELECT user_id FROM workout WHERE id = " + str(workout_id)
        user_id = db.select(query)
        if user_id != []:
            # If the workout is not new
            user_id = user_id[0][0] # Reformat the query result to get the user_id associated with the workout
            if int(user_id) != current_user.id:
                # If the current user does not own the workout, then redirect them
                flash("Do not attempt to access other user's workouts")
                return redirect(url_for("main.workouts"))

        query = "SELECT * FROM workout WHERE user_id = " + str(current_user.id)
        workouts = db.select(query)

        query = "SELECT name FROM workout WHERE id = " + str(workout_id)
        name = db.select(query)
        if name == []:
            # Sets the name if the workout being created for the first time
            name = "New Workout"
        else:
            # Grabs the name if the workout is old
            name = name[0][0]

        query = "SELECT * FROM set WHERE workout_id = " + str(import_id)
        sets = db.select(query)

        query = "SELECT * FROM run WHERE workout_id = " + str(import_id)
        runs = db.select(query)

        sets = sets + runs

        return render_template("log.html", name=name, sets=sets, workout_id=workout_id, workouts=workouts)

    else:
        # If logging a new workout
        names = request.form.getlist("name")
        types = request.form.getlist("typ")
        weights = request.form.getlist("weight")
        reps = request.form.getlist("reps")
        sets = request.form.getlist("sets")
        notes = request.form.getlist("note")
        workout_id = int(request.form.get("workout_id"))

        form_list = [names,types,weights,reps,sets]
        # Excluding notes since notes will not always be filled
        flag = 0
        for form in form_list:
            for entry in form:
                # Iterates through every entry
                if entry == '':
                    # If there is a blank entry, indicate with flag and break
                    flag = 1
                    break

        if flag == 1:
            # Prevents the workout from being logged if there are blanks
            flash("Make sure that all cells are filled out when logging workouts")
            return redirect(url_for("main.workouts"))

        # Creates the name for the workout
        name = ""
        type_list = ["Abs","Back","Bicep","Chest","Legs","Running","Shoulder","Tricep","Other"]
        for typ in type_list:
            if typ in types:
                if name == "":
                    name = typ
                else:
                    name = name + "/" + typ 
        name = name + " Workout"

        # Creates the timestamp relative to a timezone
        timestamp = str(pytz.utc.localize(datetime.datetime.utcnow()))

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
            query = "DELETE FROM run WHERE workout_id = " + str(workout_id)
            db.delete(query)

            db.update("UPDATE workout SET name = %s WHERE id = %s", (name, str(workout_id)))

        # Adds all of the sets to the database
        for x in range(len(names)):
            if types[x] == "Running":
                db.add(
                    """INSERT INTO run (name, typ, distance, time, user_id, workout_id, cadence, note)  
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (names[x], "Running", weights[x], reps[x], current_user.id, workout_id, sets[x], notes[x])
                )

            else:
                db.add(
                    """INSERT INTO set (name, typ, weight, reps, user_id, workout_id, sets, note) 
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""", 
                    (names[x], types[x], weights[x], reps[x], current_user.id, workout_id, sets[x], notes[x])
                )

        return redirect(url_for("main.workouts"))

@main.route("/deletelog/")
@login_required
def del_workout():
    workout_id = request.args.get("workout_id")
    
    db = Database()

    query = "DELETE FROM workout WHERE id = " + str(workout_id)
    db.delete(query)
    query = "DELETE FROM set WHERE workout_id = " + str(workout_id)
    db.delete(query)
    query = "DELETE FROM run WHERE workout_id = " + str(workout_id)
    db.delete(query)

    return redirect(url_for("main.workouts"))

