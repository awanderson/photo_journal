'''
Created on Jul 19, 2013

this is the change.....

@author: jacobforster
'''

from protorpc import messages
from protorpc import message_types
from protorpc import remote
from google.appengine.ext import endpoints


#message for specifying a specific event already in the database
class eventSpecifier(messages.Message):
    eventKey = messages.StringField(1, required=True)
    userKey = messages.StringField(2, required=True)
    eventDate = messages.DateTimeField(3, required=False)

#message for createNewEvent method 
class fullEventObject(messages.Message):
    privacySetting = messages.IntegerField(1)
    
class boolean(messages.Message):
    booleanValue = messages.BooleanField(1, required=True)
    


@endpoints.api(name='eventServices',
               version'.01',
               description='API for all methods directly relating to the events object in the database',
               hostname='engaged-context-254.appspot.com'
               )
class EventAPI(remote.service):
    
    @endpoints.method(eventSpecifier, boolean, name='event.addEvent', path='addEvent', http_method='POST')
    def addEvent(self, request):
        #adds an existing event to a user's journal
        
        #takes the event key and the user key as input parameters and then adds an event reference object as a desendant of the user class that is defined
        #using the user reference key
        #if the date of the event is not transferred in the message then look up event date and add that to the event reference object, or just add date transmitted
        #returns a boolean value if added successfully or not
    
    @endpoints.method(fullEventObject, boolean, name='event.createEvent', path='createEvent', http_method='POST')
    def createEvent(self, request):
        #creates a new event based off the given parameters
        
        #basically copies the event message containing all the information and creates a new event object with it
        #check what number the tags are in the user or add the new tags to the user property in the database
        #returns a boolean value if created successfully or not
       
    @endpoints.method(eventSpecifier, boolean, name'event.removeEvent', path='removeEvent', http_method='POST')   
    def removeEvent(self, request):
        #removes an event from a users collection and possibly from the database if the event is personal or if it is public and no one has subscribed to it
        
        DOES IT DELETE THE PICTURES AND EVERYTHING ASSOCIATED WITH IT?????
        
        
        
        
        
        
        