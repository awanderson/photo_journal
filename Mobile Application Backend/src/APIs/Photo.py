"""
Photo API Custom Error Codes

10 - Upload URL Generation Failed (There was a problem generating the url to upload the photos to. Possibly a time-out error.)

"""

from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
from google.appengine.ext import blobstore

import random

from Classes import user
from Classes import photo

class fullPhotoObject(messages.Message):
    photo = messages.BytesField(1, required = True)
    eventKey = messages.StringField(2, required = True)
    userKey = messages.StringField(3, required = True)
    privacySetting = messages.IntegerField(4, default = 0, required = False)
    authToken = messages.StringField(5, required = True)
    userName = messages.StringField(6, required = True)

class photoSpecifier(messages.Message):
    photoKey = messages.StringField(1, required = True)
    authToken = messages.StringField(2, required = True)
    userName = messages.StringField(3, required = True)


class uploadUrlGet(messages.Message):
    eventKey = messages.StringField(1, required = True)
    privacySetting = messages.IntegerField(2, default = 0, required = False)
    authToken = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)
    
class uploadUrlReturn(messages.Message):
    uploadUrl = messages.StringField(1, required = False)
    tempPhotoKey = messages.StringField(2, required = False)
    errorMessage = messages.StringField(3, required = False)
    errorNumber = messages.IntegerField(4, required = False)
    
        
#used on get methods when only need to validate user
class validateUserMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True) 
    

    

class callResult(messages.Message):
    errorMessage = messages.StringField(1, required = False)
    errorNumber = messages.IntegerField(2, required = False)

@endpoints.api(name='photoService', version='v0.0116', description='API for photo methods', hostname='engaged-context-254.appspot.com')    
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
        tempPhotoKey = photo.TempPhoto.createNewTempPhoto(request.eventKey, userKey, request.privacySetting)
        
        
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
            
    
    #def pinPhoto(self):
        pass
        #receives photo key, event key, user tolkien
    @endpoints.method(photoSpecifier, callResult, name = 'Photo.removePhoto', path = 'removePhoto', http_method = 'POST')   
    def removePhoto(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return uploadUrlReturn(errorNumber = 1, errorMessage = "User Validation Failed")
        
        try:
            photo.Photo.removePhotoByKey(request.photoKey)
            callResult(errorNumber = 200, errorMessage = "Success")
            
        except:
            callResult(errorNumber = 3, errorMessage = "Database Transaction Failed")
            
        
        
        
        
        