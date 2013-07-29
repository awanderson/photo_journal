from google.appengine.ext import ndb

class Tag(ndb.Model):
    
    permanent = ndb.BooleanProperty(indexed = False)
    name = ndb.StringProperty()
    number = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now_add = True, indexed = False)
    
    
    """
    Creates the default tags for an event - created as descendant of the user given by the userKey parameter
    """
    @classmethod
    def createDefaultTags(cls, userKey):
        
        #create the tag objects that are defaults - all are descendants of the user key given
        sportsTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 0, name = "Sports")
        musicTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 1, name = "Music")
        nightLifeTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 2, name = "Night Life")
        holidaysTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 3, name = "Holidays")
        festivalTag = Tag(parent = ndb.Key(urlsafe=userKey), permanent = True, number = 4, name = "Festivals")
        
        #puts the tags in the database
        ndb.put_multi([sportsTag, musicTag, nightLifeTag, holidaysTag, festivalTag])
    
    @classmethod
    def addTagToEvent(cls, tagKey, eventKey):
        pass