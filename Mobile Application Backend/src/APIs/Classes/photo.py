from google.appengine.ext import ndb

class Photo(ndb.Model):
    
    photo = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty()
    eventReference = ndb.KeyProperty()#event added to
    userReference = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = 0, 1, 2)
    
    
    #NEED PHOTO BLOB OBJECT SOMEWHERE SOMEHOW