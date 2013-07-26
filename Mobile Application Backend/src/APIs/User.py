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
class userMessage(messages.Message):
    userName = messages.StringField(1, required=False)
    password = messages.StringField(2, required=False)
    email = messages.StringField(3, required=False)
    userId = messages.IntegerField(4, required=False)
    authToken = messages.StringField(5, required=False)
    errorMessage = messages.StringField(6, required=False)
    errorNumber = messages.IntegerField(7, required=False)
    

class authTokenMessage(messages.Message):
    authToken = messages.StringField(1, required=False)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)

class checkFriendsMessage(messages.Message):
    authToken = messages.StringField(1, required=False)
    

class boolean(messages.Message):
    booleanValue = messages.BooleanField(1, required=True)

    #need a name for service, version number? and human readable description
@endpoints.api(name='userService', version='v0.1920', description='API for User methods', hostname='engaged-context-254.appspot.com')  
class UserApi(remote.Service):
    
    
    
    @endpoints.method(userMessage, authTokenMessage, name='User.signup', path='signup', http_method='POST')
    def SignupUser(self, request):
        
        #makes sure required fields aren't blank
        if (request.userName == "") or (request.password == "") or (request.email == ""):
        
            returnData = authTokenMessage(errorMessage = "Missing a required field", errorNumber=11)
            return returnData
        
        #calls backend function, returns token of user
        userData = user.User.signUpUser(request.userName, request.email, request.password)
        
        if not userData[0]:
            returnData = authTokenMessage(errorMessage = userData[1], errorNumber = userData[2])
            return returnData
        
        #get auth token
        returnData = authTokenMessage(authToken = userData[1])
        
        return returnData
    
    #login method using password and email/username
    @endpoints.method(userMessage, authTokenMessage, name='User.login', path='login', http_method='POST')
    def LoginUser(self, request):
        
        #makes sure required fields aren't blank (can put either userName or email in userName field because frontend doesn't know which one user submitted
        if (request.password == "") or (request.userName == ""):
            returnData = authTokenMessage(errorMessage = "Missing a required field", errorNumber=11)
            return returnData
        
        #calls user backend function, returns token of user
        userData = user.User.loginUser(request.userName, request.password)
        
        if not userData[0]:
            returnData = authTokenMessage(errorMessage = userData[1], errorNumber = userData[2])
            return returnData
        
        #get auth token
        returnData = authTokenMessage(authToken = userData[1])
        return returnData
        
        
    #logout method, simply deletes authtoken from backend
    @endpoints.method(userMessage, boolean, name='User.logout', path='logout', http_method='POST')    
    def LogoutUser(self,request):
        
        if (request.userName == "") or (request.authToken == ""):
            returnData = boolean(booleanValue=False)
            return returnData
        
        #calls method in user class, returns boolean if token was deleted
        userData = user.User.logoutUser(request.userName, request.authToken)
        
        returnData = boolean(booleanValue=userData)
        return returnData
        
        
        
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