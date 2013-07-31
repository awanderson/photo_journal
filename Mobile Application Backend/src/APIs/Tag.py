from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

from Classes import user
from Classes import tag


#main message for class
class tagMessage(messages.Message):
    tagName = messages.StringField(1, required=True)
    eventKey = messages.StringField(2, required=True)
    authToken = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)


class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)   



@endpoints.api(name='tagService', version='v0.01', description='API for tag methods', hostname='engaged-context-254.appspot.com')    
class TagApi(remote.Service):
    
    
    
    @endpoints.method(tagMessage, callResult, name='Tag.addTagToEvent', path='addTagToEvent', http_method='POST')
    def addTagToEvent(self, request):
        
        #checks for blank fields
        if (request.tagName == "") or (request.eventKey == "") or (request.authToken == "") or (request.userName == ""):
            return callResult(booleanValue = False, errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorMessage = "User Validation Failed", errorNumber = 1)
        
        
        returnBool = tag.Tag.addTagToEvent(request.eventKey, userKey, request.tagName)
        
        return callResult(booleanValue = returnBool)
    
    @endpoints.method(tagMessage,callResult, name='Tag.removeTagFromEvent', path='removeTagFromEvent', http_method='POST')
    def removeTagFromEvent(self, request):
        
        #checks for blank fields
        if (request.tagName == "") or (request.eventKey == "") or (request.authToken == "") or (request.userName == ""):
            return callResult(booleanValue = False, errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorMessage = "User Validation Failed", errorNumber = 1)
        
        returnBool = tag.Tag.removeTagFromEvent(request.eventKey, userKey, request.tagName)
        
        return callResult(booleanValue = returnBool)
        