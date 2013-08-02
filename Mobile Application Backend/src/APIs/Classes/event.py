from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from datetime import datetime


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
        
        #removes the main event object
        cls.removeEventBykey(eventKey)
        
        #removes tags from the user events object before deleting the user event - used to check to delete the tag if there are no more events that use that tag
        userEventObject = user_event.UserEvent.getUserEventObject(eventKey, userKey)
        
        for tag in userEventObject.tagKey:
            #gets the actual tag object that is a descendant from the user that holds the name of the tag
            tagObject =  tag.key().get()
           
            #deletes the tag reference in the user event, and also the tag if it is not used anywhere else in other events
            tag.Tag.removeTagFromEvent(eventKey, userKey, tagName = tagObject.name)
           
        
        #deletes the user event object
        user_event.UserEvent.removeUserEvent(eventKey, userKey)
        
        #deletes any photos corresponding to the event
        photo.Photo.removeUsersPhotosFromEvent(eventKey, userKey)
        
        #deletes any memories related to the event
        memory.Memory.removeUserMemoriesFromEvent(eventKey, userKey)
        
        #deletes search document
        #search.DocumentManager.removeEventDoc(eventKey)
    
    @classmethod
    @ndb.transactional(xg=True)
    def removeExclusiveEvent(cls, eventKey):
        pass
    
    
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
        
        
        
        
        
