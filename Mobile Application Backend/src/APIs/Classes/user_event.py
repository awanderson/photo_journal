from google.appengine.ext import ndb
import logging
    
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
        
    @classmethod
    def addTagObToEvent(cls, eventKey, userKey, tagKey):
        
        userEventOb = None
        
        #gets userEvent Object
        userEventObjectList = cls.query(ancestor = ndb.Key(urlsafe=userKey)).filter(cls.eventKey == ndb.Key(urlsafe=eventKey)).fetch()
        logging.info(len(userEventObjectList))
        
        for userEventOb in userEventObjectList:
            userEventOb = userEventOb
        
        
        #can't find userEvent object
        if userEventOb is None:
            return False
        
        tagKeyOb = ndb.Key(urlsafe=userKey)
        
        #sees if tag is already in userevent
        if tagKeyOb in userEventOb.tagKey:
            return True
        
        #tries appending to existing list first
        try:
            userEventOb.tagKey.append(tagKeyOb)
        
        #no list, just set tagKey equal to single value
        except:
            userEventOb.tagKey = tagKeyOb
        
        return True
            
        
    
    @classmethod
    def removeTagObFromEvent(cls, eventKey, userKey, tagOb):
        
        pass