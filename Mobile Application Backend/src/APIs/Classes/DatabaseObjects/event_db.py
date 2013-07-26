from google.appengine.ext import ndb

class EventDB(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty(choices = 0, 1 , 2) #0 is default 0=private 1=exclusive 2=public
    originalAuthor = ndb.KeyProperty()
    
    
    
    