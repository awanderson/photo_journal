from google.appengine.ext import ndb
from webapp2_extras.appengine.auth import models
from datetime import datetime
import logging

import user_event
import photo
import memory
import utilities
import search
import tag
import notification


class Event(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2]) #0 is default 0=private 1=exclusive 2=public
    creatorKey = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    updated = ndb.DateTimeProperty(auto_now=True, indexed = False)
    
    friendsInvited = ndb.KeyProperty(repeated=True)
    
    
    """
    Adds a user event to a users journal if the event is public, or user is on the invite list of 
    an exclusive event
    """
    @classmethod
    def addEventToUserJournal(cls, eventKey, userKey):
        
        
        eventOb = ndb.Key(urlsafe=eventKey).get()
        
        #personal event, can't add to somebody's else's journal
        if(eventOb.privacySetting == 0):
            logging.info("wrong privacy settings")
            return False
        
        #invite only event, makes sure user is on list
        elif eventOb.privacySetting == 1:
            if ndb.Key(urlsafe=userKey) not in eventOb.friendsInvited:
                logging.info("not on invite list")
                return False
            
        logging.info("calling user event")
        #creates user event connecting user to event            
        return user_event.UserEvent.addUserEvent(eventKey, userKey)
        

    
    """
    Creates a new event tied to a specific user based on the input parameters
    @param startDate: the start date of the event - input as a string MONTH DATE, YEAR
    @param endDate: the end date of the event - input as a string MONTH DATE, YEAR (if event is one day long, startDate and endDate should be equal)
    @param privacySetting: an integer that determines if event is private (default 0), exclusive (1), or public (2)
    """
    @classmethod
    #@ndb.transactional(xg=True)
    def createNewEvent(cls, name, description, location, startDate, endDate, privacySetting, creatorKey, friendsInvited):
        
        startDate = utilities.convertStringToDate(startDate)
        
        if (endDate == startDate):
            endDate = startDate
        else:
            endDate = utilities.convertStringToDate(endDate)
            
        newEvent = Event(name = name, description = description, location = location, startDate = startDate, endDate = endDate, privacySetting = privacySetting, creatorKey = ndb.Key(urlsafe = creatorKey) )
        eventKey = newEvent.put()
        user_event.UserEvent.addUserEvent(eventKey.urlsafe(), creatorKey)
        
        #adds search document - only adds public events to search document
        if(privacySetting == 2):
            search.DocumentManager.addEventDoc(eventKey.urlsafe(), name, description, privacySetting, creatorKey, startDate, endDate)
        
        eventOb = eventKey.get()
        
        #exclusive event, create notifications to invite members
        if(privacySetting == 1):
            
            #goes through every friend invited
            for friendKey in friendsInvited:
                #creates notification
                notification.Notification.addNotification(eventKey.urlsafe(), friendKey, creatorKey, name)
                
                #adds to event invite list
                eventOb.friendsInvited.append(ndb.Key(urlsafe=friendKey))
              
            #saves event object with correct friendsInvited list
            eventOb.put()
            
        return True
        
    """
    Completely removes an event
    """
    @classmethod   
    @ndb.transactional(xg=True)
    def removeEvent(cls, eventKey, userKey, eventObject):
        
        userKeyObject = ndb.Key(urlsafe = userKey)
        
        if eventObject.privacySetting == 0:
            #removes the main event object
            cls.removeEventBykey(eventKey)
        
        elif eventObject.privacySetting == 1 and eventObject.creatorKey == userKeyObject:
            #removes the users key from the event's creator key field
            cls.changeCreatorToAdmin(eventKey = eventKey)
        
        elif eventObject.privacySetting == 2 and eventObject.creatorKey == userKeyObject:
            #removes the users key from the event's creator key field
            cls.changeCreatorToAdmin(eventKey = eventKey)
            
        #removes tags from the user events object before deleting the user event - used to check to delete the tag if there are no more events that use that tag
        userEventObject = user_event.UserEvent.getUserEventObject(eventKey = eventKey, userKey = userKey)
        
        for tagKey in userEventObject.tagKey:
            
            #gets the actual tag object that is a descendant from the user that holds the name of the tag
            tagObject =  tagKey.get()
           
            #deletes the tag reference in the user event, and also the tag if it is not used anywhere else in other events
            tag.Tag.removeTagFromEvent(eventKey = eventKey, userKey = userKey, tagName = tagObject.name)
           
        
        #deletes the user event object
        user_event.UserEvent.removeUserEvent(eventKey = eventKey, userKey = userKey)
        
        #deletes any photos corresponding to the event
        photo.Photo.removeUsersPhotosFromEvent(eventKey = eventKey, userKey = userKey)
        
        #deletes any memories related to the event
        memory.Memory.removeUserMemoriesFromEvent(eventKey = eventKey, userKey = userKey)
        
        if eventObject.creatorKey == userKeyObject:
            
            #deletes search document
            search.DocumentManager.removeEventDoc(eventKey = eventKey)       
        
    
    @classmethod
    def removeEventBykey(cls, eventKey):
        
        eventKey = ndb.Key(urlsafe = eventKey)
        eventKey.delete()
        
    @ndb.transactional    
    def getEventById(self, eventId):
        
        eventKey = ndb.Key('Event', eventId)
        return eventKey.get()
     
    """
    gets info for event given an event key object
    """
    @classmethod
    def getEventInfo(cls, eventKeyOb):   
       
        eventOb = eventKeyOb.get()
       
        if(eventOb is None):
            return False
        return[eventOb.name, eventOb.description, utilities.convertDateToString(eventOb.startDate), utilities.convertDateToString(eventOb.endDate), eventOb.privacySetting, eventOb.updated]
    
    """
    changes the creater of an event to the admin user
    """
    @classmethod
    def changeCreatorToAdmin(cls, eventKey):
        
        #gets the event object based on the key
        eventObject = ndb.Key(urlsafe = eventKey).get()
        
        #gets the user object that represents our admin account
        adminUserObject = cls.getAdminUser()
        
        #changes the creator key field in the event object to the key of the admin user
        eventObject.creatorKey = adminUserObject.key
        
        #puts the object back into the database
        eventObject.put()
    
    """
    gets the admin user object - a helper function because it can't be in a transaction (not an ancestor query)
    """
    @classmethod
    @ndb.non_transactional()
    def getAdminUser(cls):
        adminUserObject = models.User.get_by_auth_id("admin")
        if not adminUserObject:
            return False
        else:
            return adminUserObject
        
        """
    Adds a friend to invite list and generates a notification
    """
    @classmethod
    def addInviteToEvent(cls, eventKey, friendKey):
        
        eventOb = ndb.Key(urlsafe=eventKey).get()
        #not an invite event
        if(eventOb.privacySetting != 1):
            return False
        
        #make sure friend is not already invited to event
        if ndb.Key(urlsafe=friendKey) in eventOb.friendsInvited:
            return False
        
        name = eventOb.name
        creatorKey = eventOb.creatorKey.urlsafe()
        #creates notification
        notification.Notification.addNotification(eventKey, friendKey, creatorKey, name)
                
        #adds to event invite list
        eventOb.friendsInvited.append(ndb.Key(urlsafe=friendKey))
        
        #puts appended object into database
        eventOb.put()
        
        return True
    
    """
    Removes a friend from an event db object
    """
    @classmethod
    def removeInviteFromEvent(cls, eventKey, userKey):
    
        eventOb = ndb.Key(urlsafe=eventKey).get()
    
        #removes user key object from friends invited list
        eventOb.friendsInvited = utilities.removeValuesFromList(eventOb.friendsInvited, ndb.Key(urlsafe=userKey))
    
        eventOb.put()
    
        return True
    
    @classmethod
    def checkSync(cls, eventKey, userKey, lastSynced):
        
        #gets event object
        eventOb = ndb.Key(urlsafe=eventKey).get()
        #gets last synced in right format for comparing to backend date
        lastSynced = utilities.convertStringToDate(lastSynced)
        
        #event out of date, return information
        if(eventOb.updated > lastSynced):
            return [True, eventOb.name, eventOb.description, utilities.convertDateToString(eventOb.startDate), utilities.convertDateToString(eventOb.endDate), eventOb.privacySetting, eventOb.location]
        
        else:
            return [False]   
