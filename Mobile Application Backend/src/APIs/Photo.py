from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints
from google.appengine.ext import blobstore

from Classes import user
from Classes import photo

class newPhoto(messages.Message):
    photo = messages.BytesField(1, required = True)
    eventKey = messages.StringField(2, required = True)
    userKey = messages.StringField(3, required = True)
    privacySetting = messages.IntegerField(4, default = 0, required = False)
    authToken = messages.StringField(5, required = True)
    userName = messages.StringField(6, required = True)
    
#used on get methods when only need to validate user
class validateUserMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True) 
    
class uploadUrlMessage(messages.Message):
    uploadUrl = messages.StringField(1, required = True)

class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)

@endpoints.api(name='photoService', version='v0.011', description='API for photo methods', hostname='engaged-context-254.appspot.com')    
class PhotoApi(remote.Service):
    
    
    @endpoints.method(validateUserMessage, uploadUrlMessage, name = 'Photo.getUploadUrl', path = 'getUploadUrl', http_method = 'POST')
    def getUploadUrl(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorNumber = 1, errorMessage = "User Validation Failed")
        
        uploadURL= blobstore.create_upload_url('/process_upload')
        
        return uploadUrlMessage(uploadUrl = uploadURL)
            
    
    #def pinPhoto(self):
        pass
        #receives photo key, event key, user tolkien

    #def addPhoto(self):
        #receive actual photo blob, 
        
    #def removePhoto(self):