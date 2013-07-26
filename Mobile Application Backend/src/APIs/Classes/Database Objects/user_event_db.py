from google.appengine.ext import ndb

class UserEventDB(ndb.Model):
    
    eventReference = ndb.KeyProperty()
    tagReference = ndb.KeyProperty(repeated = True)
    pinnedPictureReference = ndb.KeyProperty()
    memory = StructuredProperty(MemoryDB)

class MemoryDB(ndb.Model):
    title = ndb.StringProperty(indexed = False)
    content = ndb.TextProperty()