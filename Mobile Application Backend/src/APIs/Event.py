'''
Created on Jul 23, 2013

@author: jacobforster
'''

from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from protorpc import message_types
from google.appengine.ext import endpoints

#message for specifying a specific event already in the database
class eventSpecifier(messages.Message):
    eventKey = messages.StringField(1, required=True)
    userKey = messages.StringField(2, required=True)
    eventDate = message_types.DateTimeField(3, required=False)

#message for createNewEvent method 
class fullEventObject(messages.Message):
    privacySetting = messages.IntegerField(1)
    
class boolean(messages.Message):
    booleanValue = messages.BooleanField(1, required=True)

@endpoints.api(name='eventService', version='v0.0123', description='API for event methods', hostname='engaged-context-254.appspot.com')    
class EventApi(remote.Service):
    
    @endpoints.method(eventSpecifier, boolean, name='Event.addEvent', path='addEvent', http_method='POST')
    def addEvent(self, request):
        pass
        #adds an existing event to a user's journal
        
       
        
    @endpoints.method(fullEventObject, boolean, name='Event.createEvent', path='createEvent', http_method='POST')
    def createEvent(self, request):
        pass
        #creates a new event based off the given parameters
        
       
        
    @endpoints.method(eventSpecifier, boolean, name='Event.removeEvent', path='removeEvent', http_method='POST')   
    def removeEvent(self, request):
        pass
        
        