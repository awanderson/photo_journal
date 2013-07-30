from google.appengine.ext import ndb
import user_event
import photo
from webapp2_extras.appengine.auth import models
from datetime import datetime


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
        
        startDate = cls.convertStringToDate(startDate)
        
        if (endDate == startDate):
            endDate = startDate
        else:
            endDate = cls.convertStringToDate(endDate)
            
        newEvent = Event(name = name, description = description, location = location, startDate = startDate, endDate = endDate, privacySetting = privacySetting, creatorKey = ndb.Key(urlsafe = creatorKey) )
        eventKey = newEvent.put()
        user_event.UserEvent.addUserEvent(creatorKey, eventKey.urlsafe())
        
    """
    Completely removes an event that is private - not complete
    """
    @classmethod   
    @ndb.transactional(xg=True)
    def removePrivateEvent(cls, eventKey, userKey):
        
        #removes the main event object
        cls.removeEventBykey(eventKey)
        
        #deletes the user event object
        user_event.UserEvent.removeUserEvent(eventKey, userKey)
        
        #deletes any photos corresponding to the event
        
        #deletes any memories related to the event
        
    
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
    Converts a string of the form "MONTH DATE, YEAR" to a Python DateTime object.
    @param inputDate: an input string of the format MONTH DATE, YEAR
    @return: a python DATETIME object corresponding to the input string
    """
    @classmethod
    def convertStringToDate(cls, inputDate):
        
        newDateObject = datetime.strptime(inputDate, '%B %d, %Y')
        return newDateObject

        
        