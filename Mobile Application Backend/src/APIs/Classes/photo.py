from google.appengine.ext import ndb
import random

class TempPhoto(ndb.Model):
    eventKey = ndb.KeyProperty()#event added to
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2])
    
    @classmethod
    def createNewTempPhoto(cls, eventKey, userKey, privacySetting):
            
        #uploadIdentifier = cls.generateUploadIdentifier()    
            
        newPhoto = TempPhoto(parent = ndb.Key(urlsafe = userKey), eventKey = ndb.Key(urlsafe = eventKey), privacySetting = privacySetting)
        tempPhotoKey = newPhoto.put()
        
        return tempPhotoKey.urlsafe()
    
    @classmethod
    def getByUploadIdentifier(cls, uploadIdentifier):
        
        return cls.query().filter(cls.uploadIdentifier == uploadIdentifier).fetch()
        
        
    """
    generates a random 9 digit integer that is unused
    """
    @classmethod
    def generateUploadIdentifier(cls):
        
        newNumber = True
        
        while newNumber:
            newUploadIdentifier = random.randrange(100000000, 999999999, 1)
            
            Object = cls.query().filter(cls.uploadIdentifier == newUploadIdentifier).fetch()
           
            if not Object:
                newNumber = False
        
        return newUploadIdentifier



class Photo(ndb.Model):
    photoKey = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty(auto_now_add = True)
    userKey = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2])
    
    
    #NEED PHOTO BLOB OBJECT SOMEWHERE SOMEHOW
    
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        pass
        
    @classmethod
    def createNewPhoto(cls, eventKey, userKey, privacySetting, photoKey):   
            
        newPhoto = Photo(parent = ndb.Key(urlsafe = eventKey), privacySetting = privacySetting, userKey = userKey, photoKey = photoKey)
        
        newPhoto.put()
        
   
            
        