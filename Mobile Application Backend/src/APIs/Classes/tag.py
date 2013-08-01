from google.appengine.ext import ndb
import logging
import user_event


class Tag(ndb.Model):
    
    permanent = ndb.BooleanProperty(indexed = False)
    name = ndb.StringProperty()
    number = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    """
    Creates the default tags for an event - created as descendant of the user given by the userKey parameter
    """
    @classmethod
    def createDefaultTags(cls, userKey):
        
        #create the tag objects that are defaults - all are descendants of the user key given
        sportsTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 0, name = "Sports")
        musicTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 1, name = "Music")
        nightLifeTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 2, name = "Night Life")
        holidaysTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 3, name = "Holidays")
        festivalTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 4, name = "Festivals")
        
        #puts the tags in the database
        ndb.put_multi([sportsTag, musicTag, nightLifeTag, holidaysTag, festivalTag])
    
    """
    Adds tag key to user event object given a string with the tags name
    """
    
    @classmethod
    def addTagToEvent(cls, eventKey, userKey, tagName):
        
        """need to modify tagName here first (capitalize first letter, etc.)"""
        
        tagOb = cls.getTagObjectFromString(userKey, tagName)
            
        #create new tag if tag doesn't exists
        if not tagOb:
            tagOb = Tag(parent = ndb.Key(urlsafe=userKey), permanent = False, name=tagName)
            tagOb.put()
        
        
        tagKey = tagOb.key.urlsafe()
        
        #adds tag to userEvent
        return user_event.UserEvent.addTagObToEvent(eventKey, userKey, tagKey)
        
    
    """
    Removes tag key from user event object given a string with the tags name
    """
    @classmethod
    def removeTagFromEvent(cls, eventKey, userKey, tagName):
        
        """need to modify tagName here first (capitalize first letter, etc.)"""

        
        tagOb = cls.getTagObjectFromString(userKey, tagName)
        
        #no tag by tagName
        if not tagOb:
            return False
        
        tagKey = tagOb.key.urlsafe()
        
        if not user_event.UserEvent.removeTagObFromEvent(eventKey, userKey, tagKey):
            return False
        
        #checks to see if there are other events from same tag
        eventKeyList = user_event.UserEvent.getAllEventsFromTagOb(userKey, tagKey)
        
        logging.info(len(eventKeyList))
        
        #if no other events, remove tag if it isn't permanent
        if(len(eventKeyList) == 0 and (tagOb.permanent==False)):
            logging.info('trying to delete')
            logging.info(tagOb)
            tagOb.key.delete()
            tagOb.put()
        return True

    @classmethod
    def getTagObjectFromString(cls, userKey, tagName):
        """need to modify tagName here first (capitalize first letter, etc.)"""
        tagOb = None
        
        #tries finding existing tag
        tagObList = cls.query(ancestor=ndb.Key(urlsafe=userKey)).filter(cls.name == tagName).fetch()
        for tagOb in tagObList:
            tagOb = tagOb
        
        #no tag by tagName
        if tagOb is None:
            return False
        
        return tagOb
