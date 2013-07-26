#development api explorer located at localhost:8080/_ah/api/explorer - uses googles own server and passes your localhost as the base so basically accessing your locahost from google's server.. nice
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
#from webapp2_extras.appengine.auth import models
from Classes import user
import time
import logging
from webapp2_extras import auth
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError


#this is the actual object (message) that we will be transferring
class UserMessage(messages.Message):
    username = messages.StringField(1, required=False)
    password = messages.StringField(2, required=True)
    email = messages.StringField(3, required=False)
    user_id = messages.IntegerField(4, required=False)
    auth_token = messages.StringField(5, required=False)
    error_message = messages.StringField(6, required=False)
    error_number = messages.IntegerField(7, required=False)
    
    
    #need a name for service, version number? and human readable description
@endpoints.api(name='userService', version='v0.1916', description='API for User methods', hostname='engaged-context-254.appspot.com')  
class UserApi(remote.Service):
    
    
    
    
    #this method signs the user up, pretty self explanatory
    @endpoints.method(UserMessage, UserMessage, name='User.signup', path='signup', http_method='POST')
    def SignupUser(self, request):
        
        #makes sure required fields aren't blank
        if (request.username == "") or (request.password == "") or (request.email == ""):
        
            request.error_message = "Missing a required field"
            request.error_number = 11
            return request
        
        #sets properties which have to be unique, otherwise won't create user
        unique_properties = ['email_address']
        
        username = request.username
        password = request.password
        email = request.email
        
        
        #actually creates the user, inserts into db
        user_data = user.User.create_user(username, unique_properties, email_address = email, password_raw=password, user_name=username)
        
        #this means email is already registered, send back error message
        if not user_data[0]:
            request.error_message = "User already exists in Database. Please use a different email and/or username"
            request.error_number = 10
            return request
        
        #gets user data if successful, variable can't be user, causes error
        user_ob = user_data[1]
        
        #gets user id to use in other api calls
        request.user_id = user_ob.get_id()
        
        #creates user token
        request.auth_token = user.User.create_auth_token(request.user_id)
        
        
        return request
    
    #login method using password and email/username
    @endpoints.method(UserMessage, UserMessage, name='User.login', path='login', http_method='POST')
    def LoginUser(self, request):
        
        logging.getLogger().setLevel(logging.DEBUG)
        
        #tries using email password combo first
        username = request.username
        password = request.password
        try:
            #auth_ob = auth.Auth(request)
            user_ob = auth.Auth.get_user_by_password(username, password)
            request.error_message = str(user_ob)
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            logging.error("test")
            request.error_message = "issue logging in user"
        
        """
        try:
            
        except (InvalidAuthIdError, InvalidPasswordError) as e:
            #request.error_message = e;
            return request
        """
        return request
    
    def getSettings(self, request):
        pass
        #returns an object with all user settings
        
    def setSettings(self, request):
        pass
    
    def addFriend(self, request):
        pass
        #receives both user keys
        #returns boolean if added to database
        
    def removeFriend(self):
        pass
        #receives both user keys
        
    def checkUserExist(self):
        pass
        #helper function to check each user - actually in the class
    def checkUsersExist(self):
        pass
        #either json or infinite message recursion 