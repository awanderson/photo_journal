from google.appengine.ext import ndb
from google.appengine.ext import blobstore

class TempPhoto(ndb.Model):
    eventKey = ndb.KeyProperty(indexed = False)#event added to
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2], indexed = False)
    
    @classmethod
    def createNewTempPhoto(cls, eventKey, userKey, privacySetting):
            
        #uploadIdentifier = cls.generateUploadIdentifier()    
            
        newPhoto = TempPhoto(parent = ndb.Key(urlsafe = userKey), eventKey = ndb.Key(urlsafe = eventKey), privacySetting = privacySetting)
        tempPhotoKey = newPhoto.put()
        
        return tempPhotoKey.urlsafe()



class Photo(ndb.Model):
    blobKey = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty(auto_now_add = True)
    userKey = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = [0, 1, 2])
    
    
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        for photoOb in photoObjects:
            
            #retreives the blobinfo object and then deletes the corresponding blob along with the blobinfo object
            blobInfoObject = blobstore.BlobInfo.get(photoOb.blobKey)
            blobInfoObject.delete()
            
            
            #deletes the photo objects - the descendants under events
            photoOb.key.delete()
            
     
    @classmethod
    @ndb.transactional(xg = True) 
    def addNewPhotoUsingTemp(cls, tempPhotoKey, blobInfoObject):   
            
        tempPhotoKeyObject = ndb.Key(urlsafe = tempPhotoKey)
        
        tempPhotoObject = tempPhotoKeyObject.get()   
        
        newPhoto = Photo(parent = tempPhotoObject.eventKey, privacySetting = tempPhotoObject.privacySetting, userKey = tempPhotoKeyObject.parent(), blobKey = blobInfoObject.key())
        
        newPhoto.put()
        
        tempPhotoKeyObject.delete()
        
    @classmethod
    @ndb.transactional(xg=True)
    def removePhotoByKey(cls, photoKey):
        
        ndb.Key(urlsafe = photoKey).delete()
        
   
            
        