from google.appengine.ext import ndb

class MemoryDB(ndb.Model):
    
    title = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty()
    dateAdded = ndb.DateTimeProperty(indexed = False)
    eventReference = ndb.KeyProperty()#event added to
    userReference = ndb.KeyProperty()#user who added memory