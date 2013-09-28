"""
Photo API Custom Error Codes

10 - Upload URL Generation Failed (There was a problem generating the url to upload the photos to. Possibly a time-out error.)
11 - Private Photo\Owned By User (The photo trying to be acted upon is private)
"""

from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
from google.appengine.ext import blobstore

from Classes import user
from Classes import photo
from Classes import user_event

class photoSpecifier(messages.Message):
    photoKey = messages.StringField(1, required = True)
    authToken = messages.StringField(2, required = True)
    userName = messages.StringField(3, required = True)


class uploadUrlGet(messages.Message):
    eventKey = messages.StringField(1, required = True)
    privacySetting = messages.IntegerField(2, default = 0, required = False)
    caption = messages.StringField(3, required = False)
    authToken = messages.StringField(4, required = True)
    userName = messages.StringField(5, required = True)
    
class uploadUrlReturn(messages.Message):
    uploadUrl = messages.StringField(1, required = False)
    tempPhotoKey = messages.StringField(2, required = False)
    errorMessage = messages.StringField(3, required = False)
    errorNumber = messages.IntegerField(4, required = False) 
    
class callResult(messages.Message):
    errorMessage = messages.StringField(1, required = False)
    errorNumber = messages.IntegerField(2, required = False)

class pinPhotoMessage(messages.Message):
    photoKey = messages.StringField(1, required = True)
    eventKey = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)
    
class editCaptionMessage(messages.Message):
    photoKey = messages.StringField(1, required = True)
    caption = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)
    
class eventSpecifier(messages.Message):
    eventKey = messages.StringField(1, required = True)
    authToken = messages.StringField(2, required = True)
    userName = messages.StringField(3, required = True)
    
class photoObject(messages.Message):
    servingUrl = messages.StringField(1, required = True)
    caption = messages.StringField(2, required = False)
    isPinned = messages.BooleanField(3, required = False)
    pinDate = messages.StringField(4, required = False)
    dateAdded = messages.StringField(5, required = False)
    photoKey = messages.StringField(6, required = False)
    
class returnPhotoObjects(messages.Message):
    photoObjects = messages.MessageField(photoObject, 1, repeated = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)
    
    
@endpoints.api(name='photoService', version='v0.503', description='API for photo methods', hostname='engaged-context-254.appspot.com')    
class PhotoApi(remote.Service):
    
    """
    Get the required attributes in order to upload a picture to the blobstore
    """
    @endpoints.method(uploadUrlGet, uploadUrlReturn, name = 'Photo.prepareUpload', path = 'prepareUpload', http_method = 'POST')
    def prepareUpload(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #starts a call for to create an upload url
        rpcObject = blobstore.create_upload_url_async('/processupload')
        
        #create the temporary object to copy over once the photo is uploaded - descendant of user
        tempPhotoKey = photo.TempPhoto.createNewTempPhoto(request.eventKey, userKey, request.privacySetting, request.caption)
        
        
        try:
            #get the result of the create upload url call earlier
            # uploadURL = rpcObject.get_result()
            uploadURL = rpcObject.get_result()
            
            return uploadUrlReturn(errorNumber = 200, errorMessage = "Success", uploadUrl = uploadURL, tempPhotoKey = tempPhotoKey)
        
        except: 
            
            #delete the temp photo detail storage if no url generated
            ndb.Key(urlsafe = tempPhotoKey).delete()
            #if can't retrieve the url created - timeout or other error
            return uploadUrlReturn(errorNumber = 11, errorMessage = "Upload URL Generation Failed")
        
    """
    pins a photo to a users user event object
    """
    @endpoints.method(pinPhotoMessage, callResult, name='Photo.pinPhoto', path = 'pinPhoto', http_method = 'POST')
    def pinPhoto(self, request):
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        result = user_event.UserEvent.pinPhoto(userKey = userKey, photoKey = request.photoKey, eventKey = request.eventKey)
            
        if result == False:
            return callResult(errorNumber = 11, errorMessage = "Private Photo\Owned By User")
        
        else:        
            return callResult(errorNumber = 200, errorMessage = "Success")
    
    """
    removes a pinned photo from a users user event object
    """        
    @endpoints.method(pinPhotoMessage, callResult, name = 'Photo.removePinnedPhoto', path = 'removePinnedPhoto', http_method = 'POST')
    def removePinnedPhoto(self, request):
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        try:
            user_event.UserEvent.removePinnedPhoto(eventKey = request.eventKey, userKey = userKey, photoKey = request.photoKey)
            return callResult(errorNumber = 200, errorMessage = "Success")
        except:
            return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
    """
    removes a photo based on the photokey
    """
    @endpoints.method(photoSpecifier, callResult, name = 'Photo.removePhoto', path = 'removePhoto', http_method = 'POST')   
    def removePhoto(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #try:
        photoObject = ndb.Key(urlsafe = request.photoKey).get()
        photo.Photo.removePhotoByKey(photoObject = photoObject)
        return callResult(errorNumber = 200, errorMessage = "Success")
            
        #except:
            #return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
            
    @endpoints.method(editCaptionMessage, callResult, name = 'Photo.editCaption', path = 'editCaption', http_method = 'POST')
    def editCaption(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #check to make sure that the caption field isnt blank
        if (request.caption == ""):
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields")
        
        #try to edit the caption and replace it with the new caption
        try:
            photo.Photo.editCaptionByPhotoKey(photoKey = request.photoKey, caption = request.caption)
            return callResult(errorNumber = 200, errorMessage = "Success")
        
        except:
            return callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
        
    @endpoints.method(eventSpecifier, returnPhotoObjects, name = 'Photo.getUserPhotosForEvent', path = 'getUserPhotosForEvent', http_method = 'POST' )
    def getUserPhotosForEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        photoObjects = photo.Photo.getUserPhotoUrlsForEvent(request.eventKey, userKey)
        
        photoObjectList = []
        
        for photoOb in photoObjects:
            photoUrl = photoOb[0]
            photoCaption = photoOb[1]
            dateAdded = photoOb[2]
            photoKey = photoOb[3]
            
            photoObForList = photoObject(servingUrl = photoUrl, caption = photoCaption, isPinned = False, dateAdded = dateAdded, photoKey = photoKey)
            
            photoObjectList.append(photoObForList)
        
        return returnPhotoObjects(photoObjects = photoObjectList, errorNumber = 200, errorMessage = "Success")
        
    @endpoints.method(eventSpecifier, returnPhotoObjects, name = 'Photo.getPublicPhotosForEvent', path = 'getPublicPhotosForEvent', http_method = 'POST')
    def getPublicPhotosForEvent(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        photoObjects = photo.Photo.getPublicPhotoUrlsForEvent(eventKey = request.eventKey, userKey = userKey)
        
        photoObjectList = []
        
        for photoOb in photoObjects:
            photoUrl = photoOb[0]
            photoCaption = photoOb[1]
            isPinned = photoOb[2]
            photoKey = photoOb[3]
            
            photoObForList = photoObject(servingUrl = photoUrl, caption = photoCaption, isPinned = isPinned, photoKey = photoKey)
            
            photoObjectList.append(photoObForList)
        
        return returnPhotoObjects(photoObjects = photoObjectList, errorNumber = 200, errorMessage = "Success")
        
        
        
