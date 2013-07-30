'''
Created on Jul 23, 2013

@author: jacobforster
'''
from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from protorpc import message_types
from google.appengine.ext import endpoints

from Classes import event
from Classes import user

#message for specifying a specific event already in the database
class eventKey(messages.Message):
    eventKey = messages.StringField(1, required=True)

"""
A full event object
"""
class fullEventObject(messages.Message):

    name = messages.StringField(1, required = True)
    startDate = messages.StringField(2, required = True)
    endDate = messages.StringField(3, required = True)
    description = messages.StringField(4, required = False)
    location = messages.StringField(5, required = False)
    privacySetting = messages.IntegerField(6, default = 0, required = False)
    authToken = messages.StringField(8, required = True)
    userName = messages.StringField(9, required = True)
    eventKey = messages.StringField(10, required = False)
    
"""
Used when returning events to the client application
"""
class returnEventObjects(messages.Message):       
    #creates a list of event message objects to be returned
    events = messages.MessageField(fullEventObject, 1, repeated=True)
    
class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)
    

@endpoints.api(name='eventService', version='v0.0144', description='API for event methods', hostname='engaged-context-254.appspot.com')    
class EventApi(remote.Service):
    
    # @endpoints.method(EventSpecifier, Boolean, name='Event.addEvent', path='addEvent', http_method='POST')
    # def addEvent(self, request):
    #    pass
        #adds an existing event to a user's journal
        
       
    """
    Creates an event with the given parameters in the newEventObject message
    """
    @endpoints.method(fullEventObject, callResult, name='Event.createEvent', path='createEvent', http_method='POST')
    def createEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorNumber = 1, errorMessage = "User Validation Failed")
        
        #Check if fields are blank
        if request.name == "" or request.startDate == "" or request.endDate == "":
            return callResult(booleanValue = False, errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        #create the event
        try:
            event.Event().createNewEvent(request.name, request.description, request.location, request.startDate, request.endDate, request.privacySetting, userKey)
        except ndb.transactional().TransactionFailedError:
            return callResult(booleaValue = False)
            
        return callResult(booleanValue = True)
    
    """
    Dual Purpose Method
    1. If Event is private, it deletes the event object and the user event objects from the database and any of the pictures associated with it, also does the tag stuff
    2. If event is public or exclusive...
    Doesnt actually delete the user event objects from the database? Those get deleted in the get events method?
    """   
    @endpoints.method(eventKey, callResult, name='Event.removeEvent', path='removeEvent', http_method='POST')   
    def removeEvent(self, request):
        
        #gets the event object from the database
        eventObject = ndb.Key(urlsafe=request.eventKey).get()
        
        #checks to see if the event is private
        if eventObject.privacySetting == 0:
            event.Event().removeEventBykey(request.eventKey)
            
        
        transactionSucceeded = True
        event.Event().removeEventById(request.eventId)
        return callResult(booleanValue = transactionSucceeded)
    
    #@endpoints.method(eventId, fullEventObject, name='Event.getEvent', path='getEvent', http_method='POST')
    def getEvent(self, request):
        #transactionSucceeded = True
        eventObject = event.Event().getEventById(request.eventId)
       # return fullEventObject(name = eventObject.name, startDate = eventObject.startDate, endDate = eventObject.endDate, description = eventObject.description, location = eventObject.location, privacySetting = event.Event().convertPrivacyIntegerToEnum(eventObject.privacySetting), creatorId = eventObject.creatorId, eventId = eventId)
        
    #@endpoints.method(eventSpecifier, fullEventObject, name='Event.getEventsFromRange', path='removeEvent', http_method='POST')
    def getEventsFromRange(self, request):
        pass
        #to get a range of events from a user.. search the descendants
        
    def getEventsFromTag(self, request):
        pass
    #gets all event from a tag
    
    def getAllUserEvents(self, request):
        pass
    #recieves an optional parameter of how mny event objects to return
    
    #has a message that has all not required properties of the event attributes
    #use "if messageAttribute is not None" - described in protorpc library overview
    
    def replyToInvitation(self, request):
        pass
        #put zero or one to accept or reject
        #send event and user reference
        
    def searchEvents(self, request):
        pass
    #passed the title and date
    #search by date first
    
    def addTag(self, request):
        pass
        #passed the event key and tag index number and user key
        
    def removeTag(self, request):
        pass
        #same as the add tag
        #only removes tags from events... if no more events with tag delete the tag from the user db
        #cant remove the default tags
        