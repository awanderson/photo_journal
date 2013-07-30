from google.appengine.ext import ndb

class Memory(ndb.Model):
    
    title = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty(indexed = False)
    dateAdded = ndb.DateTimeProperty(indexed = False)
    eventKey = ndb.KeyProperty()#event added to
    userKey = ndb.KeyProperty()#user who added memory
    
    """
    Adds a (new) memory to an event
    """
    @classmethod
    def addMemoryToEvent(cls, title, content, eventKey, userKey):
        newMemory = Memory(title = title, content = content, eventKey = ndb.Key(urlsafe = eventKey), userKey = ndb.Key(urlsafe = userKey))
        newMemory.put()
        
        