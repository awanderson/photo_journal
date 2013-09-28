from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import images

import user_event
import utilities

class TempPhoto(ndb.Model):
    eventKey = ndb.KeyProperty(indexed = False)#event added to
    privacySetting = ndb.IntegerProperty(choices = [0, 2], indexed = False)
    caption = ndb.StringProperty(indexed = False)
    
    @classmethod
    def createNewTempPhoto(cls, eventKey, userKey, privacySetting, caption):   
            
        newPhoto = TempPhoto(parent = ndb.Key(urlsafe = userKey), eventKey = ndb.Key(urlsafe = eventKey), privacySetting = privacySetting, caption = caption)
        tempPhotoKey = newPhoto.put()
        
        return tempPhotoKey.urlsafe()



class Photo(ndb.Model):
    blobKey = ndb.BlobKeyProperty()
    caption = ndb.StringProperty(indexed = False)
    dateAdded = ndb.DateTimeProperty(auto_now_add = True)
    updated = ndb.DateTimeProperty(auto_now=True, indexed = False)
    userKey = ndb.KeyProperty(indexed = True)#user who uploaded photo
    servingUrl = ndb.StringProperty(indexed = False)
    privacySetting = ndb.IntegerProperty(choices = [0, 2], indexed = True)
    
    """
    removes all of a specified users photos from a specific event
    """
    @classmethod
    def removeUsersPhotosFromEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        for photoOb in photoObjects:
            #removes the photo entities and the blobstore entities
            cls.removePhotoByKey(photoObject = photoOb, eventKey = eventKey)   
            
    """
    removes all of the users  
    """
    @classmethod
    def removeUsersPrivatePhotosFromEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).filter(cls.privacySetting == 0).fetch()
        
        for photoOb in photoObjects:
            #removes the photo entities and blobstore entities
            cls.removePhotoByKey(photoObject = photoOb, eventKey = eventKey)
           
    """
    adds a new photo to the database and links everything together given the blobinfo object and the temp photo object key
    """
    @classmethod
    @ndb.transactional(xg = True) 
    def addNewPhotoUsingTemp(cls, tempPhotoKey, blobInfoObject):   
        
        
        #gets the temporary photo object in order to copy properties into the new object
        tempPhotoKeyObject = ndb.Key(urlsafe = tempPhotoKey)
        
        tempPhotoObject = tempPhotoKeyObject.get() 
        
        #gets the serving url that the image will be served at in order to store in photo object
        servingUrl = images.get_serving_url(blobInfoObject)
        
        #create the new (permanent) photo object
        newPhoto = Photo(parent = tempPhotoObject.eventKey, caption = tempPhotoObject.caption, servingUrl = servingUrl, privacySetting = tempPhotoObject.privacySetting, userKey = tempPhotoKeyObject.parent(), blobKey = blobInfoObject.key())
        
        newPhoto.put()
        
        #delete the old temporary photo object
        tempPhotoKeyObject.delete()
    
    """
    removes a photo object and the blobstore object it references (completely deletes a photo basically)
    can be passed either a photoKeyString or an actual Photo object - passing photoKey Does not WORK!!!
    """
    @classmethod
    @ndb.transactional(xg=True, propagation = ndb.TransactionOptions.ALLOWED)
    def removePhotoByKey(cls, photoKey = False, photoObject = False, eventKey = None):
        
        photoObject
        #if not passed the actual photoObject
        if photoObject == False:
            #gets the photo object from the database and then deletes it
            photoObject = ndb.Key(urlsafe = photoKey).get()
            photoKeyOb = ndb.Key(urlsafe = photoKey)#deletes the photo object if it was passed a string
            photoKeyOb.delete()
            
        #if passed the actual photoObject  
        else:
            photoKey = photoObject.key
            photoKey.delete()
            
        
        #retrieves the blobinfo object and then deletes the corresponding blob along with the blobinfo object
        blobInfoObject = cls.getBlobInfoObject(photoObject.blobKey)
        cls.deleteBlobWithBlob(blobInfoObject)
        
        #deletes all pinned references to a photo in all user event objects for an event
        user_event.UserEvent.removeAllPinnedPhotosForPhoto(eventKey = eventKey, photoKey = photoKey.urlsafe())
    
    """
    helper function = bug in sdk, getting blob info by key has to be non transactional -can't be gotten in a transaction
    """
    @classmethod
    @ndb.non_transactional()
    def getBlobInfoObject(cls, blobKey):
        return blobstore.BlobInfo.get(blobKey)
    
    @classmethod
    @ndb.non_transactional()
    def deleteBlobWithBlob(cls, blobInfoObject):
        blobInfoObject.delete()
    
    
    """
    edits a caption given a certain photo
    """
    @classmethod
    @ndb.transactional()
    def editCaptionByPhotoKey(cls, photoKey, caption):
        
        photoObject = ndb.Key(urlsafe = photoKey).get()
        
        photoObject.caption = caption
        
        photoObject.put()
    
    
    """
    Gets a list of all the user's photo urls based on the event key
    """
    @classmethod
    def getUserPhotoUrlsForEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.userKey == ndb.Key(urlsafe = userKey)).fetch()
        
        photoList = []
        
        for photo in photoObjects:
            photoObject = []
            photoObject.append(photo.servingUrl)
            photoObject.append(photo.caption)
            stringDateAdded = utilities.convertDateToString(photo.dateAdded)
            photoObject.append(stringDateAdded)
            photoObject.append(photo.key.urlsafe())
            
            photoList.append(photoObject)
            
        return photoList
        
        
    """
    Gets a list of all public photo urls for an event
    """
    @classmethod
    def getPublicPhotoUrlsForEvent(cls, eventKey, userKey):
        
        photoObjects = cls.query(ancestor = ndb.Key(urlsafe = eventKey)).filter(cls.privacySetting == 2).fetch()
        
        userEventObject = user_event.UserEvent.getUserEventObject(eventKey, userKey)
        
        pinnedPhotos = userEventObject.pinnedPhotoKey
        
        pinnedPhotosStrings = []
        
        for photoKey in pinnedPhotos:
            
            pinnedPhotosStrings.append(photoKey.urlsafe())
        
        photoList = []
        
        for photo in photoObjects:
            if (photo.userKey.urlsafe() != userKey):
                photoObject = []
                photoObject.append(photo.servingUrl)
                photoObject.append(photo.caption)
            
                isPinned = False
                if photo.key.urlsafe() in pinnedPhotosStrings:
                    isPinned = True
            
                photoObject.append(isPinned)
                photoObject.append(photo.key.urlsafe())
                
                photoList.append(photoObject)
            
        return photoList
   
            
        
