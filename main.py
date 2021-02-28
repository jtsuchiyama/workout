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
    return render_template('profile.html', name=current_user.name)

@main.route('/newlog')
@login_required
def log_workout():
    return render_template('newlog.html')

@main.route('/newlog', methods=['POST'])
def log_post():
    names = request.form.getlist('name')
    types = request.form.getlist('typ')
    weights = request.form.getlist('weight')
    reps = request.form.getlist('reps')

    db = Database()
    
    date = "3"
    db.add(
        """INSERT INTO workout (date) 
            VALUES(%s)""", 
            (date)
    )
    
    workout_id = db.select("SELECT LASTVAL()")[0][0]

    for x in range(len(names)):
        db.add(
            """INSERT INTO set (name, typ, weight, reps, user_id, workout_id) 
            VALUES(%s, %s, %s, %s, %s, %s)""", 
            (names[x], types[x], weights[x], reps[x], current_user.id, workout_id)
        )

    return redirect(url_for('main.profile'))