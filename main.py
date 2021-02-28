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
    name = request.form.get('name')
    typ = request.form.get('typ')
    weight = request.form.get('weight')
    reps = request.form.get('reps')
    completion = request.form.get('completion')
    if completion == "on":
        completion = "true"
    else:
        completion = "false"
        
    db = Database()
    db.add(
        """INSERT INTO set (name, typ, weight, reps, completion) 
        VALUES(%s, %s, %s, %s, %s)""", 
        (name, typ, weight, reps, completion)
    )

    return redirect(url_for('main.profile'))