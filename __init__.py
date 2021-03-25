from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from os import environ, path
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, ".env"))
    app.config["SECRET_KEY"] = environ.get("SECRET_KEY")

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.get_user(int(user_id),"id")

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app