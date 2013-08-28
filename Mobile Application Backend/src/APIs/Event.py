from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
import logging

from Classes import event
from Classes import user
from Classes import user_event
from Classes import tag
from Classes import search
from Classes import photo
from Classes import notification

"""

Class Specifc Error Messages

10 => No Events With That Tag
11 => No Such Token Exists
12 => Issue Adding Event
13 => No Event Info Exists For That Key
14 => Can Only Edit Private Events
"""

#message for specifying a specific event already in the database
class eventKey(messages.Message):
    eventKey = messages.StringField(1, required = True)
    userName = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)
    

"""
A full event object
Need to return full friend object with friend info
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
    friendsInvited = messages.StringField(11, repeated=True, required=False)
    attending = messages.BooleanField(12, required=False)
    errorNumber = messages.IntegerField(13, required=False)
    errorMessage = messages.IntegerField(14, required=False)

"""
Event object return from sync
"""
class syncEventObject(messages.Message):
    
    isChanged = messages.BooleanField(1, required=True)
    name = messages.StringField(2, required=False)
    description = messages.StringField(3, required=False)
    eventKey = messages.StringField(4, required=False)
    startDate = messages.StringField(5, required=False)
    endDate = messages.StringField(6, required=False)
    privacySetting = messages.IntegerField(7, required = False)
    location = messages.StringField(8, required = False)
    

class returnSyncObject(messages.Message):
    
    isChanged = messages.BooleanField(1, required=True)
    events = messages.MessageField(syncEventObject, 2, repeated=True, required=False)
    errorMessage = messages.StringField(3, required=False)
    errorNumber = messages.IntegerField(4, required=False)
    

"""
sync request message
"""
class syncRequestMessage(messages.Message):
    
    lastSynced = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    userName = messages.StringField(3, required=True)

"""
get specific event info message
"""
class eventInfoMesssage(messages.Message):
    eventKey = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    userName = messages.StringField(3, required=True)
    
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
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)
    eventKey = messages.StringField(4, required=False)

class searchMessage(messages.Message):
    query = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    userName = messages.StringField(3, required=True)
    date = messages.StringField(4, required=False)

class inviteeMessage(messages.Message):
    friendKey = messages.StringField(1, required=True)
    eventKey = messages.StringField(2, required=True)
    authToken = messages.StringField(3, required=True)
    userName = messages.StringField(4, required=True)

#used on get methods when only need to validate user
class validateUserMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    
    
class notificationResponse(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    notificationKey = messages.StringField(3, required=True)
    response = messages.BooleanField(4, required=True)
    
    
@endpoints.api(name='eventService', version='v0.504', description='API for event methods', hostname='engaged-context-254.appspot.com')    
class EventApi(remote.Service):
    
    """
    Adds a public or invite only event to a users journal
    """
    @endpoints.method(eventKey, callResult, name='Event.addEvent', path='addEvent', http_method='POST')
    def addEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #Check if fields are blank
        if request.eventKey == "":
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        if event.Event.addEventToUserJournal(request.eventKey, userKey):
            return callResult(errorNumber = 200, errorMessage = "Success", eventKey=request.eventKey)
        
        else:
            return callResult(errorNumber = 12, errorMessage="Issue Adding Event", eventKey=request.eventKey)
       
    """
    Creates an event with the given parameters in the newEventObject message
    """
    @endpoints.method(fullEventObject, callResult, name='Event.createEvent', path='createEvent', http_method='POST')
    def createEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #Check if fields are blank
        if request.name == "" or request.startDate == "" or request.endDate == "":
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        #create the event
        # try:
        eventKey = event.Event.createNewEvent(request.name, request.description, request.location, request.startDate, request.endDate, request.privacySetting, userKey, request.friendsInvited)
        #except:
        #   return callResult(booleanValue = False, errorNumber = 3, errorMessage = "Database Transaction Failed")
        
        #everything works and database is written to
        return callResult(errorNumber = 200, eventKey=eventKey)
    
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
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #gets the event object from the database
        eventObject = ndb.Key(urlsafe=request.eventKey).get()
            
        #remove the private event and all its corresponding objects in the database
        try:
            event.Event.removeEvent(eventKey = request.eventKey, userKey = userKey, eventObject = eventObject)
            
            return callResult(errorNumber = 200, errorMessage = "Success")
        
        except:
            
            return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
        
    
    #@endpoints.method(eventId, fullEventObject, name='Event.getEvent', path='getEvent', http_method='POST')
    #def getEvent(self, request):
    
    #PHOTO SIZE PARAMETER
        #transactionSucceeded = True
       # eventObject = event.Event().getEventById(request.eventId)
       # return fullEventObject(name = eventObject.name, startDate = eventObject.startDate, endDate = eventObject.endDate, description = eventObject.description, location = eventObject.location, privacySetting = event.Event().convertPrivacyIntegerToEnum(eventObject.privacySetting), creatorId = eventObject.creatorId, eventId = eventId)
        
   
    @endpoints.method(fullEventObject, callResult, name="Event.editEvent", path="editEvent", http_method="POST")
    def editEvent(self, request):
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        returnBool = event.Event.editEvent(request.eventKey, request.name, request.startDate, request.endDate, request.location, request.description)
        
        if(returnBool):
            return callResult(errorNumber = 200)
        
        else:
            return callResult(errorNumber = 14, errorMessage = "Can Only Edit Private Events")
        
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
            
            fullEvent = fullEventObject(name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3],
                                             privacySetting = eventInfo[4], eventKey=eventKey,  location=eventInfo[6])
            eventInfoList.append(fullEvent)
            
        return returnEventObjects(errorNumber = 200, events = eventInfoList)
    
    
    """
    Gets event info for a given key
    """
    @endpoints.method(eventInfoMesssage, fullEventObject, name="Event.getEventInfo", path='getEventInfo', http_method='POST')
    def getEventInfo(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken=="" or (request.eventKey =="")):
            return fullEventObject(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return fullEventObject(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #gets event info from key
        eventInfo = event.Event.getEventInfo(ndb.Key(urlsafe=request.eventKey))
        
        if eventInfo:
            #creates protorpc object
            fullEvent = fullEventObject(errorNumber = 200, name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3],
                                             privacySetting = eventInfo[4], eventKey=request.eventKey,  location=eventInfo[6])
            
            return fullEvent
        
        else:
            return fullEventObject(errorNumber = 13, errorMessage = "No Event Info Exists For That Key");     
        
    """
    Gets all the events of a specific user
    """    
    @endpoints.method(validateUserMessage, returnEventObjects, name = 'Event.getAllUserEvents', path='getAllUserEvents', http_method='POST')
    def getAllUserEvents(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken==""):
            return returnEventObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnEventObjects(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #gets list of all events with tag
        eventKeyList = user_event.UserEvent.getAllUserEvents(userKey)
        
        #no events, return no info
        if(len(eventKeyList) == 0):
            return returnEventObjects(errorNumber = 10, errorMessage="No Events From User")
        
        #defines list variable to hold event info
        eventInfoList = []
        
        #goes through list and gets info for a specific key
        for eventKey in eventKeyList:
            
            #gets event info from key
            eventInfo = event.Event.getEventInfo(ndb.Key(urlsafe=eventKey))
            
            if eventInfo:
                #creates protorpc object
                fullEvent = fullEventObject(name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3],
                                             privacySetting = eventInfo[4], eventKey=eventKey, location=eventInfo[6])
                eventInfoList.append(fullEvent)
            
        return returnEventObjects(errorNumber = 200, events = eventInfoList)
    
    @endpoints.method(notificationResponse, callResult, name="Event.replyToInvitation", path="replyToInvitation")
    def replyToInvitation(self, request):
        
        #checks for blank fields
        if(request.userName=="") or (request.authToken=="") or (request.notificationKey == ""):
            return returnEventObjects(errorMessage = "Missing Required Fields", errorNumber=2)  
        
        
        #checks if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnEventObjects(errorNumber = 1, errorMessage = "User Validation Failed")
        
        returnData = notification.Notification.respondToNotification(request.notificationKey, userKey, request.response)
        
        if returnData:
            return callResult(errorNumber=200)    
        else:
            return callResult(errorNumber=12, errorMessage = "Issued Updating Database")
    
        
    @endpoints.method(searchMessage, returnEventObjects, name='Event.searchEvents', path='searchEvents', http_method='POST')
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
            fullEvent = fullEventObject(name=eventInfo[0], description=eventInfo[1], startDate=eventInfo[2], endDate = eventInfo[3], privacySetting = eventInfo[4],
                                        location=eventInfo[6], eventKey=eventKey)
            #checks if user is already attending event
            if not user_event.UserEvent.getUserEventObject(eventKey, userKey):
                fullEvent.attending = False
            else:
                fullEvent.attending = True
                
            eventInfoList.append(fullEvent)
            
        return returnEventObjects(errorNumber = 200, events = eventInfoList)
    
    
    """
    Adds a friend to invite only event
    """
    @endpoints.method(inviteeMessage, callResult, name='Event.addInviteToEvent', path = 'addInviteToEvent', http_method='POST')
    def addInviteToEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #Check if fields are blank
        if request.friendKey == "" or request.eventKey == "":
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields" )
              
        returnData = event.Event.addInviteToEvent(request.eventKey, request.friendKey)
        
        if returnData:
            return callResult(errorNumber=200)    
        else:
            return callResult(errorNumber=12, errorMessage = "Issued Updating Database")
    
    """
    returns a list of events that have changed since the event given
    """
    @endpoints.method(syncRequestMessage, returnSyncObject, name='Event.syncEvents', path='syncEvents', http_method='POST')
    def syncEvents(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #Check if fields are blank
        if request.lastSynced == "":
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        #gets all users events
        eventKeyList = user_event.UserEvent.getAllUserEvents(userKey)      
        
        #no events, return no info
        if(len(eventKeyList) == 0):
            return returnEventObjects(errorNumber = 10, errorMessage="No Events From User")
        
        fullEventList = []
        
        for eventKey in eventKeyList:
            
            #gets event info if event has changed since last sync
            eventInfo = event.Event.checkSync(eventKey, userKey, request.lastSynced)
            
            fullEvent = syncEventObject()
            fullEvent.eventKey = eventKey
            #events changed, update info
            if(eventInfo[0]):
                fullEvent.isChanged = True
                fullEvent.name = eventInfo[1]
                fullEvent.description = eventInfo[2]
                fullEvent.startDate = eventInfo[3]
                fullEvent.endDate = eventInfo[4]
                fullEvent.privacySetting = eventInfo[5]
                fullEvent.location = eventInfo[6]
            
            #no change
            else:
                fullEvent.isChanged = False
            
            fullEventList.append(fullEvent)
        #returns full object
        return returnSyncObject(events = fullEventList, errorNumber = 200, isChanged = True)
