from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

from Classes import event
from Classes import user
from Classes import user_event
from Classes import tag
from Classes import search
from Classes import photo

"""

Class Specifc Error Messages

10 => No Events With That Tag
11 => No Such Token Exists
"""

#message for specifying a specific event already in the database
class eventKey(messages.Message):
    eventKey = messages.StringField(1, required = True)
    userName = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)
    

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
    eventKey = messages.StringField(8, required = False)
    authToken = messages.StringField(9, required = False)
    userName = messages.StringField(10, required = False)
    
    
"""
Used when returning events to the client application
"""
class returnEventObjects(messages.Message):       
    #creates a list of event message objects to be returned
    events = messages.MessageField(fullEventObject, 1, repeated=True, required=False)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)


"""
Used in getEventsFromTag to carry tag object
"""
class tagMessage(messages.Message):
    tagName = messages.StringField(1, required = True)
    authToken = messages.StringField(2, required = True)
    userName = messages.StringField(3, required = True)


class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = False)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)

class searchMessage(messages.Message):
    query = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    userName = messages.StringField(3, required=True)
    date = messages.StringField(4, required=False)




@endpoints.api(name='eventService', version='v0.0150', description='API for event methods', hostname='engaged-context-254.appspot.com')    
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
            event.Event.createNewEvent(request.name, request.description, request.location, request.startDate, request.endDate, request.privacySetting, userKey)
        except:
            return callResult(booleaValue = False, errorNumber = 3, errorMessage = "Database Transaction Failed")
        
        #everything works and database is written to
        return callResult(booleanValue = True)
    
    """
    Dual Purpose Method
    1. If Event is private, it deletes the event object and the user event objects from the database and any of the pictures associated with it, also does the tag stuff
    2. If event is public or exclusive...
    Doesnt actually delete the user event objects from the database? Those get deleted in the get events method?
    """   
    @endpoints.method(eventKey, callResult, name='Event.removeEvent', path='removeEvent', http_method='POST')   
    def removeEvent(self, request):
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorNumber = 1, errorMessage = "User Validation Failed")
        
        #gets the event object from the database
        eventObject = ndb.Key(urlsafe=request.eventKey).get()
        
        #checks to see if the event is private
        if eventObject.privacySetting == 0:
            
            #remove the private event and all its corresponding objects in the database
            try:
                event.Event.removePrivateEvent(eventKey = request.eventKey, userKey = userKey)
                
                #CHANGE LOCATION BACK INTO A TRANSACTION ONCE SDK IS FIXED
                #this is called here because there is a bug in googles code that wont allow blobinfo objects to be gotten by key within a transaction
                photo.Photo.removeUsersPhotosFromEvent(eventKey = request.eventKey, userKey = userKey)
                return callResult(errorNumber = 200, errorMessage = "Success")
            except:
                return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
        
        #checks to see if the event is exclusive
        elif eventObject.privacySetting == 1:
            pass
            
        #checks to see if the event is public
        elif eventObject.privacySetting == 2:
            
            try:
                event.Event.removePublicEvent(eventKey = eventKey, userKey = userKey)
                
                return callResult(errorNumber = 200, errorMessage = "Success")
            except:
                return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")

    
    #@endpoints.method(eventId, fullEventObject, name='Event.getEvent', path='getEvent', http_method='POST')
    #def getEvent(self, request):
    
    #PHOTO SIZE PARAMETER
        #transactionSucceeded = True
       # eventObject = event.Event().getEventById(request.eventId)
       # return fullEventObject(name = eventObject.name, startDate = eventObject.startDate, endDate = eventObject.endDate, description = eventObject.description, location = eventObject.location, privacySetting = event.Event().convertPrivacyIntegerToEnum(eventObject.privacySetting), creatorId = eventObject.creatorId, eventId = eventId)
        
   
   
    """
    Gets all the events with info for a tag string
    """
    @endpoints.method(tagMessage, returnEventObjects, name='Event.getEventsFromTag', path='getEventsFromTag', http_method='POST')     
    def getEventsFromTag(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken=="") or (request.tagName == ""):
            return returnEventObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnEventObjects(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #gets tag key string
        tagKey = tag.Tag.getTagObjectFromString(userKey, request.tagName).key.urlsafe()
        
        #not tag key means no tag exists, return error
        if not tagKey:
            return returnEventObjects(errorNumber = 11, errorMessage = "No Such Token Exists")
        
        #gets list of all events with tag
        eventKeyList = user_event.UserEvent.getAllEventsFromTagOb(userKey, tagKey)
        
        #no events, return no info
        if(len(eventKeyList) == 0):
            return returnEventObjects(errorNumber = 10, errorMessage="No Events With That Tag")
        
        #defines list variable to hold event info
        eventInfoList = []
        
        #goes through list and gets info for a specific key
        for eventKey in eventKeyList:
            
            #gets event info from key
            eventInfo = event.Event.getEventInfo(ndb.Key(urlsafe=eventKey))
            #creates protorpc object
            fullEvent = fullEventObject(name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3], privacySetting = eventInfo[4])
            eventInfoList.append(fullEvent)
            
        return returnEventObjects(events = eventInfoList)
        
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
        
    @endpoints.method(searchMessage, returnEventObjects, name='Events.searchEvents', path='searchEvents', http_method='POST')
    def searchEvents(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken=="") or (request.query == ""):
            return returnEventObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnEventObjects(errorNumber = 1, errorMessage = "User Validation Failed")
        
        eventKeyList = search.Search.queryEvents(request.query, request.date)
        
        #defines list variable to hold event info
        eventInfoList = []
        
        for eventKey in eventKeyList:
            
            #gets event info from key
            eventInfo = event.Event.getEventInfo(ndb.Key(urlsafe=eventKey))
            #creates protorpc object
            fullEvent = fullEventObject(name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3], privacySetting = eventInfo[4])
            eventInfoList.append(fullEvent)
            
        return returnEventObjects(events = eventInfoList)
        
