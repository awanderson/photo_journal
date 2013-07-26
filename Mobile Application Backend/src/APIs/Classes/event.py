from DatabaseObjects import event_db
from google.appengine.ext import ndb

class Event():
    
    def __init__(self):
        pass
    
    def addEventToUserJournal(self):
        pass
    
    
    @ndb.transactional
    def createNewEvent(self, name, description, location, startDate, endDate, privacySetting, creatorKey):
        
        newEvent = event_db.EventDB(name = name, description = description, location = location, startDate = startDate, endDate = endDate, privacySetting = privacySetting, originalAuthor = creatorKey)
        newEvent.put()
        
         #takes the event key and the user key as input parameters and then adds an event reference object as a desendant of the user class that is defined
        #using the user reference key
        #if the date of the event is not transferred in the message then look up event date and add that to the event reference object, or just add date transmitted
        #returns a boolean value if added successfully or not
        
        #basically copies the event message containing all the information and creates a new event object with it
        #check what number the tags are in the user or add the new tags to the user property in the database
        #returns a boolean value if created successfully or not
        
        #removes an event from a users collection and possibly from the database if the event is personal or if it is public and no one has subscribed to it