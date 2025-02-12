from flask_login import UserMixin
from db import Database

class User(UserMixin): 
    # Inherits is_authenticated, is_actgive, is_anonymous, get_id() from UserMixin
    def __init__(self,id,email,password,name, timezone):
        self.id = id
        self.email = email
        self.password = password
        self.name = name
        self.timezone = timezone

    @staticmethod
    def get_user(param, type): 
        """Queries and returns the model for the user either through passing the email or user_id"""
        db = Database()
        if type == "email":
            emails = db.select(
                "SELECT email FROM public.user"
            )

            for email in emails:
                if email[0] == param: 
                    # If a user with the same email is found, then we want to return the user data
                    data = db.select(
                        "SELECT * FROM public.user WHERE email='%s'" % (param)
                    )[0]


        elif type == "id":
            ids = db.select(
                "SELECT id FROM public.user"
            )

            for id_ in ids:
                if id_[0] == param: 
                    # If a user with the same id is found, then we want to return the user data
                    data = db.select(
                        "SELECT * FROM public.user WHERE id='%s'" % (param)
                    )[0]

        user = User(data[0],data[1],data[2],data[3],data[4])
        return user
        