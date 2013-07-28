from google.appengine.ext import ndb
from webapp2_extras import security
from webapp2_extras.appengine.auth import models
import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError



class User():
    
    @classmethod
    def signUpUser(cls, userName, email, rawPassword, phone = None):
        
        
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


    @classmethod
    def loginUser(cls,userName, rawPassword):
        
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
        
    @classmethod
    def logoutUser(cls, userName, authToken):
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        #actually deletes token
        userOb.delete_auth_token(userOb.key.id(), authToken)
        
        return True
    
    #adds a friend to user object
    @classmethod
    def addFriend(cls, userKey, friendKey):
        #tests if user is already friend
        testOb = ndb.query(models.User.friends == friendKey)
        #Object returned, friend already existed, return 
        if testOb != None:
            return "Friend already exists"
        
        
        userOb = ndb.key(userKey)
        userOb.friends.append(friendKey)
        userOb.put()
        return "Friend didn't exist"
    
    #returns boolean to determine if user exists in DB and is logged in with token
    @classmethod     
    def validateUser(cls, userName, authToken):    
        
        #gets user object for id
        userOb = models.User.get_by_auth_id(userName)
        
        
        #validates token, returns object if true, false if not
        userTokenOb = userOb.validate_token(userOb.key.id(), 'auth', authToken)
        
        if userTokenOb is not None:
            return userOb.key.urlsafe()
        else:
            return False
        
