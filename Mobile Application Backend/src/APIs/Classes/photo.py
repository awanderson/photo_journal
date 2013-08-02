from google.appengine.ext import ndb
from google.appengine.ext import blobstore
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
    
    """@classmethod
    def getByUploadIdentifier(cls, uploadIdentifier):
        
        return cls.query().filter(cls.uploadIdentifier == uploadIdentifier).fetch()
        
        
    
    generates a random 9 digit integer that is unused
    
    @classmethod
    def generateUploadIdentifier(cls):
        
        newNumber = True
        
        while newNumber:
            newUploadIdentifier = random.randrange(100000000, 999999999, 1)
            
            Object = cls.query().filter(cls.uploadIdentifier == newUploadIdentifier).fetch()
           
            if not Object:
                newNumber = False
        
        return newUploadIdentifier"""



class Photo(ndb.Model):
    blobKey = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty(auto_now_add = True)
    userKey = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2])
    
    
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        for photo in photoObjects:
            
            #retreives the blobinfo object and then deletes the corresponding blob along with the blobinfo object
            blobInfoObject = blobstore.get(photo.blobKey)
            blobInfoObject.delete()
            
            #deletes the photo objects - the descendants under events
            photo.Key().delete()
            
     
    @classmethod
    @ndb.transactional(xg = True) 
    def addNewPhotoUsingTemp(cls, tempPhotoKey, blobInfoObject):   
            
        tempPhotoKeyObject = ndb.Key(urlsafe = tempPhotoKey)
        
        tempPhotoObject = tempPhotoKeyObject.get()   
        
        newPhoto = Photo(parent = tempPhotoObject.eventKey, privacySetting = tempPhotoObject.privacySetting, userKey = tempPhotoKeyObject.parent(), blobKey = blobInfoObject.key())
        
        newPhoto.put()
        
        tempPhotoKeyObject.delete()
        
   
            
        