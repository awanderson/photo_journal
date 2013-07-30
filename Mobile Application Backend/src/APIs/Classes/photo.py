from google.appengine.ext import ndb

class Photo(ndb.Model):
    
    photo = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty()
    eventKey = ndb.KeyProperty()#event added to
    userKey = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = 0, 1, 2)
    
    
    #NEED PHOTO BLOB OBJECT SOMEWHERE SOMEHOW
    
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        pass
        