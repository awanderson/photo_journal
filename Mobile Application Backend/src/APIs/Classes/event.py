from google.appengine.ext import ndb
from datetime import datetime

class Event(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty(choices=[0, 1, 2]) #0 is default 0=private 1=exclusive 2=public
    creatorId = ndb.StringProperty()
    
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
    @ndb.transactional
    def createNewEvent(self, name, description, location, startDate, endDate, privacySetting, creatorId):
        
        startDate = self.convertStringToDate(startDate)
        
        if (endDate == startDate):
            endDate = startDate
        else:
            endDate = self.convertStringToDate(endDate)
            
        newEvent = Event(name = name, description = description, location = location, startDate = startDate, endDate = endDate, privacySetting = privacySetting, creatorId = creatorId)
        newEvent.put()
        
    @ndb.transactional
    def removeEvent(self, eventId):
        pass
        
    """
    Converts a string of the form "MONTH DATE, YEAR" to a Python DateTime object.
    @param inputDate: an input string of the format MONTH DATE, YEAR
    @return: a python DATETIME object corresponding to the input string
    """
    def convertStringToDate(self, inputDate):
        
        newDateObject = datetime.strptime(inputDate, '%B %d, %Y')
        return newDateObject
        
        
        
         #takes the event key and the user key as input parameters and then adds an event reference object as a descendant of the user class that is defined
        #using the user reference key
        #if the date of the event is not transferred in the message then look up event date and add that to the event reference object, or just add date transmitted
        #returns a boolean value if added successfully or not
        
        #basically copies the event message containing all the information and creates a new event object with it
        #check what number the tags are in the user or add the new tags to the user property in the database
        #returns a boolean value if created successfully or not
        
        #removes an event from a users collection and possibly from the database if the event is personal or if it is public and no one has subscribed to it