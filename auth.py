from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from db import Database
from models import User

auth = Blueprint("auth", __name__)

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")
    remember = True if request.form.get("remember") else False

    user = User.get_user(email,"email")

    # Checks if the user exists
    # Takes the user-supplied password, hashes it, and compares it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.")
        return redirect(url_for("auth.login")) # If the user doesn't exist or password is wrong, reload the page

    # If the above check passes, then we know the user has the right credentials, thus login
    login_user(user, remember=remember)
    return redirect(url_for("main.workouts"))

@auth.route("/signup")
def signup():
    return render_template("signup.html")

@auth.route("/signup", methods=["POST"])
def signup_post():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    timezone = request.form.get("timezone")

    db = Database()
    emails = db.select(
        "SELECT email FROM public.user"
    )
    if emails != []: 
        # Need to reformat since the actual list of emails is held within the returned tuple
        emails = emails[0] 

    if email in emails: 
        # If a user with the same email is found, we want to redirect back to signup page
        flash("Email address already exists")
        return redirect(url_for("auth.signup"))

    # If the email is not already used, then we want to hash the password and add the user to the database
    password=generate_password_hash(password, method="sha256")
    db.add(
        """INSERT INTO public.user (email, password, name, timezone) 
        VALUES(%s, %s, %s, %s)""", 
        (email, password, name, timezone)
    )

    return redirect(url_for("auth.login"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

