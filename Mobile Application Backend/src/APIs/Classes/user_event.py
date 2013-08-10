from google.appengine.ext import ndb
import logging
import utilities
import event
    
class UserEvent(ndb.Model):
    eventKey = ndb.KeyProperty()
    tagKey = ndb.KeyProperty(repeated = True)
    pinnedPhotoKey = ndb.KeyProperty(repeated = True)
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    updated = ndb.DateTimeProperty(auto_now=True, indexed = False)
    
    
    """
    adds an event to a user's journal
    """
    @classmethod
    def addUserEvent(cls, eventKey, userKey):
        
        #makes sure userEvent doesn't already exists
        #gets userEvent Object
        userEventOb = cls.getUserEventObject(eventKey, userKey)
        
        if userEventOb:
            logging.info(userEventOb)
            return False
        
        userEventObject = UserEvent(parent = ndb.Key(urlsafe=userKey), eventKey = ndb.Key(urlsafe=eventKey))
        userEventObject.put()
        return True
    
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
    Returns a list of all event keys strings for a specific user
    """
    @classmethod
    def getAllUserEvents(cls, userKey):
        
        #gets userEvent Object
        userEventObjectList = cls.query(ancestor = ndb.Key(urlsafe=userKey)).fetch()
        
        eventKeyList = []
        
        #puts event key in new list
        for userEventOb in userEventObjectList:
            eventKeyList.append(userEventOb.eventKey.urlsafe())
            
        return eventKeyList
    
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
    
    
    """
    adds a photo to a users pinned photos for a specific event
    """
    @classmethod
    @ndb.transactional(xg = True)
    def pinPhoto(cls, eventKey, userKey, photoKey):
       
        #gets the user's user event object
        userEventObject = cls.getUserEventObject(eventKey = eventKey, userKey = userKey)
        
        #creates the photokey object representing the photo to be stored in the database
        photoKeyObject = ndb.Key(urlsafe = photoKey)
        
        photoObject = photoKeyObject.get()
        
        #makes sure the picture is public and not owned by the user before "pinning" it, not owned
        if photoObject.privacySetting == 2 and photoObject.userKey != ndb.Key(urlsafe = userKey):
        
            #checks if the photo key is already in the pinned list for the event
            if photoKeyObject in userEventObject.pinnedPhotoKey:
                logging.info("Photo Already Pinned")
            
                #if not already in the list, adds the photokey to the list
            else:
                userEventObject.pinnedPhotoKey.append(photoKeyObject)
        
        #store the modified user event object back in the database with the pinned photo reference
            userEventObject.put()
        
        #doesn't do anything because the photo is private
        else:
            logging.info("Photo is private or photo is owned by user")
            return False
        
    """
    removes a photo from a users pinned photos for a specific event
    """
    @classmethod
    @ndb.transactional(xg = True, propogation = ndb.TransactionOptions.ALLOWED)
    def removePinnedPhoto(cls, eventKey, userKey, photoKey):
            
        #gets the user's event object
        userEventObject = cls.getUserEventObject(eventKey = eventKey, userKey = userKey)
            
        #try to remove the photo from the pinned photo list
        try:
            userEventObject.pinnedPhotoKey = utilities.removeValuesFromList(userEventObject.pinnedPhotoKey, ndb.Key(urlsafe = photoKey))
            userEventObject.put()
            
        #user events has no pinned photos, so can't remove pinned photos
        except:
            return True
        
    """
    remove all pinned photo references - used when a photo is deleted from an event
    """
    @classmethod
    def removeAllPinnedPhotosForPhoto(cls, eventKey, photoKey):
        
        #gets all user event objects with the photo key specified somewhere in the pinned photo list
        userEventObjects = cls.searchUserEventsWithPinnedPhoto(photoKey = photoKey, eventKey = eventKey)
        
        for userEventObject in userEventObjects:
            
            #try to remove the photo from the pinned photo list
            try:
                userEventObject.pinnedPhotoKey = utilities.removeValuesFromList(userEventObject.pinnedPhotoKey, ndb.Key(urlsafe = photoKey))
                userEventObject.put()
            
                #user events has no pinned photos, so can't remove pinned photos
            except:
                return True
        
    
    """
    finds all user events with the specified photo in the pinned photos (helper event because non-transactional (not an ancestor query))
    """
    @classmethod
    @ndb.non_transactional()
    def searchUserEventsWithPinnedPhoto(cls, photoKey, eventKey):
        return cls.query().filter(cls.eventKey == ndb.Key(urlsafe = eventKey), cls.pinnedPhotoKey == ndb.Key(urlsafe = photoKey)).fetch()
        
