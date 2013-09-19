from google.appengine.ext import ndb
import logging
import user_event
import utilities
from random import choice


class Tag(ndb.Model):
    
    permanent = ndb.BooleanProperty(indexed = False)
    name = ndb.StringProperty()
    number = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    color = ndb.StringProperty(indexed=False)
    
    """Random colors to be added to each tag"""
    colorArr = ["blue", "red", "black", "green", "yellow", "pink", "orange"]
    
    
    """
    Creates the default tags for an event - created as descendant of the user given by the userKey parameter
    """
    @classmethod
    def createDefaultTags(cls, userKey):
        
        #create the tag objects that are defaults - all are descendants of the user key given
        sportsTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 0, name = "Sports", color="blue")
        musicTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 1, name = "Music", color="red")
        nightLifeTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 2, name = "Night Life", color="black")
        holidaysTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 3, name = "Holidays", color="green")
        festivalTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 4, name = "Festivals", color="yellow")
        
        #puts the tags in the database
        ndb.put_multi([sportsTag, musicTag, nightLifeTag, holidaysTag, festivalTag])
    
    """
    Adds tag key to user event object given a string with the tags name
    """
    
    @classmethod
    def addTagToEvent(cls, eventKey, userKey, tagName):
        
        #clean tag name
        tagName = utilities.cleanString(tagName)
        
        
        tagOb = cls.getTagObjectFromString(userKey, tagName)
            
        #create new tag if tag doesn't exists
        tagColor = "Tag Exists" #returns this in the API call if the tag exists so it didnt need to add a new color to the tag
        if not tagOb:
            tagColor = choice(Tag.colorArr)
            tagOb = Tag(parent = ndb.Key(urlsafe=userKey), permanent = False, name=tagName, color = tagColor)
            tagOb.put()
        
        
        tagKey = tagOb.key.urlsafe()
        
        returnArray = []
        
        returnArray.append(user_event.UserEvent.addTagObToEvent(eventKey, userKey, tagKey))
        returnArray.append(tagColor)
            
        #adds tag to userEvent
        return returnArray
        
    
    """
    Removes tag key from user event object given a string with the tags name
    """
    @classmethod
    def removeTagFromEvent(cls, eventKey, userKey, tagName):
        
        #clean tag name
        tagName = utilities.cleanString(tagName)
        
        #Use this to check if the tag exists on that specific event that is needed
        userEventOb = cls.getUserEventForEventFromTagName(userKey, tagName, eventKey)
        
        if not userEventOb:
            return False
        
        tagOb = cls.getTagObjectForEventFromString(userKey, tagName)
        
        #no tag by tagName
        if not tagOb:
            return False
        
        tagKey = tagOb.key.urlsafe()
        
        #checks to see if there are other events from same tag
        eventKeyList = user_event.UserEvent.getAllEventsFromTagOb(userKey, tagKey)
        
        logging.info(len(eventKeyList))
        
        #if no other events, remove tag if it isn't permanent
        if(len(eventKeyList) == 1 and (tagOb.permanent==False)):
            tagOb.key.delete()
        
        
        if not user_event.UserEvent.removeTagObFromEvent(eventKey, userKey, tagKey):
            return False
        
        return True
    
    """
    Get tag object from key 
    """
    @classmethod
    def getTagObjectFromKey(cls, userKey, tagKey):
        
        tagKeyOb = ndb.Key(urlsafe = tagKey)
        tagOb = tagKeyOb.get()
        return tagOb
    
    """
    Get a user event object, for a specific event if it exists - not in general for the user - just the user event object if the tag exists on that event
    """
    @classmethod
    def getUserEventForEventFromTagName(cls, userKey, tagName, eventKey):
        
        #clean tag name
        tagName = utilities.cleanString(tagName)
        
        tagOb = cls.getTagObjectFromString(userKey, tagName)
        
        #tries to find the existing tag with the tag name for the event

        userEventOb = user_event.UserEvent.getUserEventWithTagObAndEventKey(userKey = userKey, tagKey = tagOb.key.urlsafe(), eventKey = eventKey)
        
        if not userEventOb:
            return False
        
        return userEventOb
    
    """
    Get a tag object, for a specific event if it exists - not in general for the user - just if it exists on that event
    """
    @classmethod
    def getTagObjectForEventFromString(cls, userKey, tagName, eventKey):
        
        #clean tag name
        tagName = utilities.cleanString(tagName)
        
        tagOb = None
        
        #tries to find the existing tag with the tag name for the event
        tagObList = cls.query(ancestor = ndb.Key(urlsafe =userKey)).filter(cls.name == tagName).filter(cls.eventKey == ndb.Key(urlsafe = eventKey))
        for tagOb in tagObList:
            tagOb = tagOb
            
        if tagOb is None:
            return False
        
        return tagOb
    
    """
    Gets the tag object given a string - doesn't matter the event - only if it exists in general for the user
    """
    @classmethod
    def getTagObjectFromString(cls, userKey, tagName):
        
        #clean tag name
        tagName = utilities.cleanString(tagName)
        
        tagOb = None
        
        #tries finding existing tag
        tagObList = cls.query(ancestor=ndb.Key(urlsafe=userKey)).filter(cls.name == tagName).fetch()
        for tagOb in tagObList:
            tagOb = tagOb
        
        #no tag by tagName
        if tagOb is None:
            return False
        
        return tagOb
    
    """
    Gets all the tag objects of a user and returns them in a list
    """
    @classmethod
    def getTagObjectsFromUser(cls,userKey):
        
        tagObList = cls.query(ancestor=ndb.Key(urlsafe=userKey)).fetch()
        return tagObList
