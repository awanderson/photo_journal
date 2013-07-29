from google.appengine.ext import ndb

class UserEvent(ndb.Model):
    eventKey = ndb.KeyProperty()
    tagKey = ndb.KeyProperty(repeated = True)
    pinnedPictureReference = ndb.KeyProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    #memory = ndb.StructuredProperty()
    
    """
    adds an event to a user's journal
    """
    def addEventToUser(self, userKeyString, eventKeyString):
        userEventObject = UserEvent(parent = ndb.Key(urlsafe=userKeyString), eventKey = ndb.Key(urlsafe=eventKeyString))
        userEventObject.put()