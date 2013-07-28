from google.appengine.ext import ndb
import user_event
from datetime import datetime

class Event(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty(choices=[0, 1, 2]) #0 is default 0=private 1=exclusive 2=public
    creatorKey = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add = True)
    
    def addEventToUserJournal(self):
        pass
    
    """
    Creates a new event tied to a specific user based on the input parameters
    @param name: the name of the event
    @param description: the event creator's description of the event
    @param location: the location of the event - for now it is just a string, there is no computation done on it
    @param startDate: the start date of the event - input as a string MONTH DATE, YEAR
    @param endDate: the end date of the event - input as a string MONTH DATE, YEAR (if event is one day long, startDate and endDate should be equal)
    @param privacySetting: an integer that determines if event is private (default 0), exclusive (1), or public (2)
    @param creatorKey: the key to the user object in the database that determines who the event belongs to
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
        user_event.UserEvent().addEventToUser(creatorKey, eventKey.urlsafe())
        
        
    @ndb.transactional
    def removeEventBykey(self, eventKey):
        
        eventKey = ndb.Key('Event', eventKey)
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
    
    """
    Converts the privacySetting integer from the database to the correct enum value to put in the event message object
    @param integer: the integer from the database
    """
    def convertPrivacyIntegerToEnum(self, integer):
        if integer == 0:
            return "PRIVATE"
        elif integer == 1:
            return "EXCLUSIVE"
        elif integer == 2:
            return "PUBLIC"
        
        