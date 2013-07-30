from google.appengine.ext import ndb

class Memory(ndb.Model):
    
    title = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty(indexed = False)
    eventKey = ndb.KeyProperty()#event added to
    userKey = ndb.KeyProperty()#user who added memory
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    """
    Adds a (new) memory to an event
    """
    @classmethod
    def addMemoryToEvent(cls, title, content, eventKey, userKey):
        
        #create the new memory object to put in the databse, linked to the event and creator key
        newMemory = Memory(title = title, content = content, eventKey = ndb.Key(urlsafe = eventKey), userKey = ndb.Key(urlsafe = userKey))
        newMemory.put()
        
    
    """
    Deletes a memory from an event
    """
    @classmethod
    def removeMemoryByKey(cls, memoryKey):
        
        #delete the event based off the key of the memory object
        ndb.Key(urlsafe = memoryKey).delete()
        
        
        