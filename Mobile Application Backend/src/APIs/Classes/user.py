from google.appengine.ext import ndb
from webapp2_extras import security
from DatabaseObjects import user_db
from webapp2_extras.appengine.auth import models



class User():
    
    @staticmethod
    def signUpUser(userName, email, raw_password, phone = None):
        
        
        #inserts into db
        unique_properties = ['email_address']
        user_data = models.User.create_user(userName, unique_properties, password_raw = raw_password, email_address = email)
        
        #this means email/username is already registered, send back error message
        if not user_data[0]:
            error = [False,"User already exists in Database. Please use a different email and/or username", 10]
            return error
        
        #gets user data if successful, variable can't be user, causes error
        user_ob = user_data[1]
        
        #gets user id to use in other api calls
        user_id = user_ob.get_id()
        
        #creates user token
        return_data = [True, models.User.create_auth_token(user_id)]
        
        #returns id of user
        return return_data


    @staticmethod
    def loginUser(userName, raw_password):
        
        qry = User.query()