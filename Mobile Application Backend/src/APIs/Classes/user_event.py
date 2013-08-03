from google.appengine.ext import ndb
import logging
import utilities
    
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
    deletes an event from a user's journal - not checked if working (modified, still haven't checked if working)
    """
    @classmethod
    def removeUserEvent(cls, eventKey, userKey):
        
        #gets userEvent Object
        userEventOb = cls.getUserEventObject(eventKey, userKey)
        
        if not userEventOb:
            return False
        
        #deletes the user event
        userEventOb.key.delete()
        return True
    
    
    """
    Adds a tag object to a specific user event object
    """    
    @classmethod
    def addTagObToEvent(cls, eventKey, userKey, tagKey):
        
        #gets userEvent Object
        userEventOb = cls.getUserEventObject(eventKey, userKey)
        
        if not userEventOb:
            return False
        
        tagKeyOb = ndb.Key(urlsafe=tagKey)
        
        
        #sees if tag is already in userevent
        if tagKeyOb in userEventOb.tagKey:
            logging.info('Tag already Exists')
            return True
        
        #Appends to tagKey list
        userEventOb.tagKey.append(tagKeyOb)
        
        #no list, just set tagKey equal to single value
        
        userEventOb.put()
        return True
            
        
    """
    Removes a tag object from a specific user event object
    """
    @classmethod
    def removeTagObFromEvent(cls, eventKey, userKey, tagKey):
        
        #gets userEvent Object
        userEventOb = cls.getUserEventObject(eventKey, userKey)
        
        if not userEventOb:
            return False
        
        tagKeyOb = ndb.Key(urlsafe=tagKey)
        
        try:
            userEventOb.tagKey = utilities.removeValuesFromList(userEventOb.tagKey, tagKeyOb)
            userEventOb.put()
            
        #user events has no tags, so can't remove tags
        except:
            return True
        
        return True
    
    """
    Returns list of all events keys strings for a specific user and tag
    """
    @classmethod
    def getAllEventsFromTagOb(cls, userKey, tagKey):
        
        #gets userEvent Object
        userEventObjectList = cls.query(ancestor = ndb.Key(urlsafe=userKey)).filter(cls.tagKey == ndb.Key(urlsafe=tagKey)).fetch()
        
        eventKeyList = []
        
        #puts event key in new list
        for userEventOb in userEventObjectList:
            eventKeyList.append(userEventOb.eventKey.urlsafe())
            
            
        return eventKeyList
    
    """
    helper method to get user_event_object from event key and user key
    """
    @classmethod
    def getUserEventObject(cls, eventKey, userKey):
        userEventOb = None
        
        #gets userEvent Object
        userEventObjectList = cls.query(ancestor = ndb.Key(urlsafe=userKey)).filter(cls.eventKey == ndb.Key(urlsafe=eventKey)).fetch()
        
        for userEventOb in userEventObjectList:
            userEventOb = userEventOb
        
        #can't find userEvent object
        if userEventOb is None:
            return False
        
        return userEventOb
        
