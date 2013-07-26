from google.appengine.ext import ndb

class event_db(ndb.Model):
    
    name = ndb.StringProperty()
    startDate = ndb.DateProperty()
    endDate = ndb.DateProperty()
    description = ndb.StringProperty(indexed=False)
    location = ndb.StringProperty(indexed=False)#just for the user, doesnt do anything fancy, just saves the text or something
    privacySetting = ndb.IntegerProperty() #0 is default 0=private 1=exclusive 2=public
    
    
    
    