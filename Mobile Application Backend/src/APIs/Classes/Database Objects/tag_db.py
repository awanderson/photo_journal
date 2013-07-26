from google.appengine.ext import ndb

class TagDB(ndb.Model):
    permanent = ndb.BooleanProperty(indexed = False)
    name = ndb.StringProperty()
