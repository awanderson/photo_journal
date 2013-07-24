'''
Created on Jul 10, 2013

@author: jacobforster
'''

#TEST GITHUB COMMIT test again third test
#development api explorer located at localhost:8080/_ah/api/explorer - uses googles own server and passes your localhost as the base so basically accessing your locahost from google's server.. nice
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
#from webapp2_extras.appengine.auth import models
from webapp2_extras import security
from webapp2_extras import sessions
from webapp2_extras import auth 
from Classes import user

#this allows python to search classes folder
import os
#sys.path.insert(0, '/_ah/api/Classes')

#imports custom user class from classes folder
#import user

import time

#this is the actual object (message) that we will be transferring
class UserMessage(messages.Message):
    username = messages.StringField(1, required=True)
    password = messages.StringField(2, required=True)
    email = messages.StringField(3, required=True)
    user_id = messages.IntegerField(4, required=False)
    auth_token = messages.StringField(5, required=False)
    error_message = messages.StringField(6, required=False)
    error_number = messages.IntegerField(7, required=False)
    
    
    #need a name for service, version number? and human readable description
@endpoints.api(name='userService', version='v0.1915', description='API for User methods', hostname='engaged-context-254.appspot.com')    
class UserApi(remote.Service):
    
    
    #this method signs the user up, pretty self explanatory
    @endpoints.method(UserMessage, UserMessage, name='User.signup', path='signup', http_method='POST')
    def SignupUser(self, request):
        
        #sets properties which have to be unique, otherwise won't create user
        unique_properties = ['email_address', 'username']
        user_name = request.username
        password = request.password
        email = request.email
        
        #actually creates the user, inserts into db
        user_data = user.User.create_user(user_name, unique_properties, email_address = email, password_raw=password)
        
        
        #this means email is already registered, send back error message
        if not user_data[0]:
            request.error_message = "User already exists in Database. Please use a different email and/or username"
            request.error_number = 10
            return request
        
        
        #gets user data
        user = user_data[1]
        
        """
        #gets user id to use in other api calls
        request.user_id = user.get_id()
        
        #creates user token
        request.auth_token = user.User.create_auth_token(request.user_id)
        
        """
        
        return request
       


app = endpoints.api_server([UserApi], restricted=False)

