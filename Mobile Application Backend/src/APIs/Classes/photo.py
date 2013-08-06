from google.appengine.ext import ndb
from google.appengine.ext import blobstore

class TempPhoto(ndb.Model):
    eventKey = ndb.KeyProperty(indexed = False)#event added to
    privacySetting = ndb.IntegerProperty(choices = [0, 2], indexed = False)
    
    @classmethod
    def createNewTempPhoto(cls, eventKey, userKey, privacySetting):   
            
        newPhoto = TempPhoto(parent = ndb.Key(urlsafe = userKey), eventKey = ndb.Key(urlsafe = eventKey), privacySetting = privacySetting)
        tempPhotoKey = newPhoto.put()
        
        return tempPhotoKey.urlsafe()



class Photo(ndb.Model):
    blobKey = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty(auto_now_add = True)
    userKey = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = [0, 2])
    
    """
    removes all of a specified users photos from a specific event
    """
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        for photoOb in photoObjects:
            #removes the photo entitities and the blobstore entities
            cls.removePhotoByKey(photoObject = photoOb, eventKey = eventKey)     
        
            
    """
    adds a new photo to the database and links everything together given the blobinfo object and the temp photo object key
    """
    @classmethod
    @ndb.transactional(xg = True) 
    def addNewPhotoUsingTemp(cls, tempPhotoKey, blobInfoObject):   
            
        tempPhotoKeyObject = ndb.Key(urlsafe = tempPhotoKey)
        
        tempPhotoObject = tempPhotoKeyObject.get()   
        
        newPhoto = Photo(parent = tempPhotoObject.eventKey, privacySetting = tempPhotoObject.privacySetting, userKey = tempPhotoKeyObject.parent(), blobKey = blobInfoObject.key())
        
        newPhoto.put()
        
        tempPhotoKeyObject.delete()
    
    """
    removes a photo object and the blobstore object it references (completely deletes a photo basically)
    can be passed either a photoKeyString or an actual Photo object
    """
    @classmethod
    @ndb.transactional(xg=True)
    def removePhotoByKey(cls, photoKey = False, photoObject = False, eventKey = None):
        
        #if not passed the actual photoObject
        if photoObject == False:
            #gets the photo object from the database and then deletes it
            photoObject = ndb.Key(urlsafe = photoKey).get()
            
        #if passed the actual photoObject  
        else:
            photoObject.key.delete()
        
        #retrieves the blobinfo object and then deletes the corresponding blob along with the blobinfo object
        blobInfoObject = blobstore.BlobInfo.get(photoObject.blobKey)
        blobInfoObject.delete()
        
        
        
   
            
        