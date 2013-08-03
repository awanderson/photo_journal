from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from datetime import datetime
from webapp2_extras.appengine.auth import models

import user_event
import photo
import memory
import utilities
import search
import tag


class Event(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2]) #0 is default 0=private 1=exclusive 2=public
    creatorKey = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    def addEventToUserJournal(self):
        pass
    
    """
    Creates a new event tied to a specific user based on the input parameters
    @param startDate: the start date of the event - input as a string MONTH DATE, YEAR
    @param endDate: the end date of the event - input as a string MONTH DATE, YEAR (if event is one day long, startDate and endDate should be equal)
    @param privacySetting: an integer that determines if event is private (default 0), exclusive (1), or public (2)
    """
    @classmethod
    @ndb.transactional(xg=True)
    def createNewEvent(cls, name, description, location, startDate, endDate, privacySetting, creatorKey):
        
        startDate = utilities.convertStringToDate(startDate)
        
        if (endDate == startDate):
            endDate = startDate
        else:
            endDate = utilities.convertStringToDate(endDate)
            
        newEvent = Event(name = name, description = description, location = location, startDate = startDate, endDate = endDate, privacySetting = privacySetting, creatorKey = ndb.Key(urlsafe = creatorKey) )
        eventKey = newEvent.put()
        user_event.UserEvent.addUserEvent(eventKey.urlsafe(), creatorKey)
        
        #adds search document - only had personal events to search document
        search.DocumentManager.addEventDoc(eventKey.urlsafe(), name, description, privacySetting, creatorKey, startDate, endDate)
              
        return True
        
    """
    Completely removes an event that is private - not complete
    """
    @classmethod   
    @ndb.transactional(xg=True)
    def removePrivateEvent(cls, eventKey, userKey):
        pass
        
        #removes the main event object
        cls.removeEventBykey(eventKey)
        
        #removes tags from the user events object before deleting the user event - used to check to delete the tag if there are no more events that use that tag
        userEventObject = user_event.UserEvent.getUserEventObject(eventKey = eventKey, userKey = userKey)
        
        for tagKey in userEventObject.tagKey:
            
            #gets the actual tag object that is a descendant from the user that holds the name of the tag
            tagObject =  tagKey.get()
           
            #deletes the tag reference in the user event, and also the tag if it is not used anywhere else in other events
            tag.Tag.removeTagFromEvent(eventKey = eventKey, userKey = userKey, tagName = tagObject.name)
           
        
        #deletes the user event object
        user_event.UserEvent.removeUserEvent(eventKey = eventKey, userKey = userKey)
        
        #Dont call this function here because there is a bug in google's sdk where you cant get a blobinfo object by key in a transaction - so called in the API
        #deletes any photos corresponding to the event
        #photo.Photo.removeUsersPhotosFromEvent(eventKey = eventKey, userKey = userKey)
        
        #deletes any memories related to the event
        memory.Memory.removeUserMemoriesFromEvent(eventKey = eventKey, userKey = userKey)
        
        #deletes search document
        search.DocumentManager.removeEventDoc(eventKey = eventKey)
    
    @classmethod
    @ndb.transactional(xg=True)
    def removeExclusiveEvent(cls, eventKey):
        pass
    
    @classmethod
    @ndb.transaction(xg=True)
    def removePublicEvent(cls, eventKey, userKey):
        
        #removes the users key from the event's creator key field
        cls.changeCreatorToAdmin(eventKey = eventKey)
        
        #copy over the stuff from the event, make it a helper function?
        
    
    @classmethod
    def removeEventBykey(cls, eventKey):
        
        eventKey = ndb.Key(urlsafe = eventKey)
        eventKey.delete()
        
    @ndb.transactional    
    def getEventById(self, eventId):
        
        eventKey = ndb.Key('Event', eventId)
        return eventKey.get()
     
    """
    gets info for event given an event key object
    """
    @classmethod
    def getEventInfo(cls, eventKeyOb):   
       
        eventOb = eventKeyOb.get()
       
        return[eventOb.name, eventOb.description, utilities.convertDateToString(eventOb.startDate), utilities.convertDateToString(eventOb.endDate), eventOb.privacySetting]
        
    @classmethod
    def changeCreatorToAdmin(cls, eventKey):
        
        eventObject = ndb.Key(urlsafe = eventKey).get()
        
        adminUserObject = models.User.get_by_auth_id("admin")
        
        eventObject.creatorKey = adminUserObject.key()
        
        
        
