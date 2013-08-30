from google.appengine.ext import ndb
import utilities


class Memory(ndb.Model):
    
    title = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty(indexed = False)
    userKey = ndb.KeyProperty()#user who added memory
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    """
    Adds a (new) memory to an event
    """
    @classmethod
    def addMemoryToEvent(cls, title, content, eventKey, userKey):
        
        #create the new memory object to put in the databse, linked to the event and creator key
        newMemory = Memory(title = title, content = content, parent = ndb.Key(urlsafe = eventKey), userKey = ndb.Key(urlsafe = userKey))
        newMemory.put()
        
        return True
        
    
    """
    Deletes a memory from an event given the memory key
    """
    @classmethod
    def removeMemoryByKey(cls, memoryKey):
        
        #delete the event based off the key of the memory object
        ndb.Key(urlsafe = memoryKey).delete()
        
    """
    deletes all memories from a given 
    """
    @classmethod
    def removeUserMemoriesFromEvent(cls, eventKey, userKey):
        
        memoryObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        for memory in memoryObjects:
            memory.key.delete()
        
    
    """
    Edits a memory given a memoryKey
    """
    @classmethod
    def editMemoryByKey(cls, title, content, memoryKey):
        
        #gets memory object
        memoryOb = ndb.Key(urlsafe=memoryKey).get()
        
        #changes only non blank new fields
        if(title != ""):
            memoryOb.title = title
        if(content != ""):
            memoryOb.content = content   
        
        memoryOb.put()
        
    """
    Gets a memory given an event key and event key, returning title, content and key string
    """
    @classmethod
    def getMemoryByEvent(cls, eventKey, userKey):
    
        memoryOb = None
        
        memoryObList = cls.query(ancestor = ndb.Key(urlsafe=eventKey)).filter(Memory.userKey == ndb.Key(urlsafe = userKey)).fetch()
        for memoryOb in memoryObList:
            
            memoryOb = memoryOb
        
        if memoryOb is None:
            return None
        
        return [memoryOb.title, memoryOb.content, memoryOb.key.urlsafe()]
            
    """
    Gets a list of memories for an event
    """
    @classmethod
    def getMemoriesByEvent(cls, eventKey, userKey):
        
        memoryObList = cls.query(ancestor = ndb.Key(urlsafe=eventKey)).filter(Memory.userKey == ndb.Key(urlsafe = userKey)).fetch()
         
        memoryList = []
        
        for memory in memoryObList:
            memoryOb = []
            memoryOb.append(memory.title)
            memoryOb.append(memory.content)
            memoryOb.append(utilities.convertDateToString(memory.created))
            memoryOb.append(memory.key.urlsafe())
            
            memoryList.append(memoryOb)
            
        return memoryList
        