from google.appengine.ext import ndb
from webapp2_extras import security
from webapp2_extras.appengine.auth import models
import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError



class User():
    
    @staticmethod
    def signUpUser(userName, email, rawPassword, phone = None):
        
        
        #inserts into db
        unique_properties = ['email_address']
        user_data = models.User.create_user(userName, unique_properties, password_raw = rawPassword, email_address = email, userName = userName)
        
        #this means email/username is already registered, send back error message
        if not user_data[0]:
            error = [False,"User already exists in Database. Please use a different email and/or username", 10]
            return error
        
        
        
        #gets user id to use in other api calls
        userId = user_data[1].get_id()
        
        #gets actual user object
        userOb = models.User.get_by_id(userId)
        
        #adds email as an auth id, needed later to login
        userOb.add_auth_id(email)
        
        #creates auth token
        authToken = models.User.create_auth_token(userId)
        #creates user token
        returnData = [True, authToken]
        
        #returns id of user
        return returnData


    @staticmethod
    def loginUser(userName, rawPassword):
        
        try:
            #logs in user, returns user object
            userOb = models.User.get_by_auth_password(userName, rawPassword)
            
            #generates new auth token
            authToken = userOb.create_auth_token(userOb.key.id())
            
            returnData = [True, authToken]
            return returnData
            
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            error = [False, "Issue Logging in. Please try again",12]
            return error
        
    @staticmethod
    def logoutUser(userName, authToken):
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        #actually deletes token
        userOb.delete_auth_token(userOb.key.id(), authToken)
        return True
       
    #returns boolean to determine if user exists in DB and is logged in with token
    @staticmethod     
    def validateUser(userName, authToken):    
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        
        #validates token, returns object if true, false if not
        returnData = userOb.validate_token(userOb.key.id(), 'auth', authToken)
        
        if returnData is not None:
            return True
        else:
            return False
        
