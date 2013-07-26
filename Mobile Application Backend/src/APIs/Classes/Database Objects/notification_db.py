from google.appengine.ext import ndb


#descendant of the user class

class EventInvitationNotification(ndb.Model):
    
    inviter = ndb.KeyProperty() #user who invited the person
    event = ndb.KeyProperty() #event invited to
    dateInvited = ndb.DateProperty()
    