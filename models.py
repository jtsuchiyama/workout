from flask_login import UserMixin
from .db import Database

class User(UserMixin): # inherits is_authenticated, is_actgive, is_anonymous, get_id()
    def __init__(self,id,email,password,name):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

    @staticmethod
    def get_user(param, type): # returns the user data based on if an email or id is passed
        db = Database()
        if type == "email":
            emails = db.select(
                "SELECT email FROM public.user"
            )

            if emails != []: # reformat to a list if need to check emails
                emails = emails[0] 

            if param in emails: # if a user with the same email is found, then we want to return the user data
                data = db.select(
                    "SELECT * FROM public.user WHERE email='%s'" % (param)
                )[0]

        elif type == "id":
            ids = db.select(
                "SELECT id FROM public.user"
            )

            if ids != []:
                ids = ids[0]

            if param in ids:
                data = db.select(
                    "SELECT * FROM public.user WHERE id='%d'" % (param)
                )[0]

        user = User(data[0],data[1],data[2],data[3])
        return user
        