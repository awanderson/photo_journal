from google.appengine.ext import ndb
import event
import user_event


class Notification(ndb.Model):
    
    eventKey = ndb.KeyProperty()
    creatorKey = ndb.KeyProperty(indexed=False)
    eventName = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    @classmethod
    def addNotification(cls, eventKey, userKey, creatorKey, eventName):
        
        #create notification
        newNotification = Notification(parent = ndb.Key(urlsafe=userKey),eventKey = ndb.Key(urlsafe=eventKey), creatorKey = ndb.Key(urlsafe=creatorKey), eventName = eventName)
        newNotification.put()
        
    
    @classmethod
    def respondToNotification(cls, notificationKey, userKey, response):
        
        notification = ndb.Key(urlsafe=notificationKey).get()
        
        #going to event
        if(response):
            
            #add exclusive event
            user_event.UserEvent.addUserEvent(notification.eventKey.urlsafe(), userKey)
            
        #not going to event  
        else:
            #remove name from exclusive event invite list
            event.Event.removeInviteFromEvent(notification.eventKey.urlsafe(), userKey)
            
        #delete notification
        ndb.Key(urlsafe=notificationKey).delete()
        
        return True
        
    @classmethod
    def getUserNotifications(cls, userKey):
        
        return Notification.query(ancestor=ndb.Key(urlsafe=userKey)).fetch()
        
            
    @classmethod
    def getNotification(cls, notificationKey):
        
        notificationOb = notificationKey.get()
        
        return [notificationOb.eventKey, notificationOb.eventName, notificationOb.creatorKey, notificationOb.created]