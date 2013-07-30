from google.appengine.ext import ndb
    
    
class UserEvent(ndb.Model):
    eventKey = ndb.KeyProperty()
    tagKey = ndb.KeyProperty(repeated = True)
    pinnedPictureReference = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    """
    adds an event to a user's journal
    """
    @classmethod
    def addUserEvent(cls, eventKey, userKey):
        userEventObject = UserEvent(parent = ndb.Key(urlsafe=userKey), eventKey = ndb.Key(urlsafe=eventKey))
        userEventObject.put()
    
    """
    deletes an event from a user's journal - not checked if working
    """
    @classmethod
    def removeUserEvent(cls, eventKey, userKey):
        
        #queries for the userEvent object that is an ancestor of the user with the journal and has a reference to the event they want deleted
        userEventObject = cls.query(ancestor = ndb.Key(urlsafe=userKey)).filter(cls.eventKey == ndb.Key(urlsafe=eventKey))
        
        #deletes the user event
        userEventObject.Key.delete()