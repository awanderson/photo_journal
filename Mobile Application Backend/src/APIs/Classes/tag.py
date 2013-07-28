from google.appengine.ext import ndb

class Tag(ndb.Model):
    
    def __init__(self):
        self.permanent = ndb.BooleanProperty(indexed = False)
        self.name = ndb.StringProperty()
        self.number = ndb.IntegerProperty()
        self.created = ndb.DateTimeProperty(auto_now_add = True)
    
    def createDefaultTags(self):
        
        sportsTag = Tag(permanent = True, number = 0, name = "Sports")
        musicTag = Tag(permanent = True, number = 1, name = "Music")
        nightLifeTag = Tag(permanent = True, number = 2, name = "Night Life")
        holidaysTag = Tag(permanent = True, number = 3, name = "Holidays")
        festivalTag = Tag(permanent = True, number = 4, name = "Festivals")
        
        