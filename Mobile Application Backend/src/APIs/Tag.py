from google.appengine.ext import ndb
from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

from Classes import user
from Classes import tag
from Classes import user_event


"""
Error Messages

10 => Issue Adding Tag To Event
11 => Issued Removing Tag From Event
"""

#main message for class
class tagMessage(messages.Message):
    tagName = messages.StringField(1, required=True)
    eventKey = messages.StringField(2, required=True)
    authToken = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)


class callResult(messages.Message):
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)   

#used on get methods when only need to validate user
class validateUserMessage(messages.Message):
    userName = messages.StringField(1, required=True)
    authToken = messages.StringField(2, required=True)
    
class tagRefObject(messages.Message):
    
    tagName = messages.StringField(1 ,required=True)
    eventCount = messages.IntegerField(2, required=True)
    eventKeys = messages.StringField(3, repeated=True)
    
class returnTagRefObjects(messages.Message):
    #creates a list of eventref message objects to be returned
    tagRefs = messages.MessageField(tagRefObject, 1, repeated=True)
    errorMessage = messages.StringField(2, required=False)
    errorNumber = messages.IntegerField(3, required=False)

    
    
@endpoints.api(name='tagService', version='v0.5', description='API for tag methods', hostname='engaged-context-254.appspot.com')    
class TagApi(remote.Service):
    
    
    """
    Adds tag to event given event key, user auth, and a string with the tag name. If tag doesn't exist, creates tag
    """
    @endpoints.method(tagMessage, callResult, name='Tag.addTagToEvent', path='addTagToEvent', http_method='POST')
    def addTagToEvent(self, request):
        
        #checks for blank fields
        if (request.tagName == "") or (request.eventKey == "") or (request.authToken == "") or (request.userName == ""):
            return callResult(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorMessage = "User Validation Failed", errorNumber = 1)
        
        
        returnBool = tag.Tag.addTagToEvent(request.eventKey, userKey, request.tagName)
        
        if returnBool:
            return callResult(errorNumber = 200)
        else:
            return callResult(errorNumber = 10, errorMessage = "Issue Adding Tag To Event")
    """
    Removes tag from event given event key, user auth, and a string with the tag name. If a tag has no events, then deletes tag
    """
    @endpoints.method(tagMessage,callResult, name='Tag.removeTagFromEvent', path='removeTagFromEvent', http_method='POST')
    def removeTagFromEvent(self, request):
        
        #checks for blank fields
        if (request.tagName == "") or (request.eventKey == "") or (request.authToken == "") or (request.userName == ""):
            return callResult(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorMessage = "User Validation Failed", errorNumber = 1)
        
        returnBool = tag.Tag.removeTagFromEvent(request.eventKey, userKey, request.tagName)
        
        if returnBool:
            return callResult(errorNumber = 200)
        else:
            return callResult(errorNumber = 11, errorMessage = "Issued Removing Tag From Event")
    """
    gets all tags from a user auth, returning a list with the tag name, number of events, and a list of the events key
    """
    @endpoints.method(validateUserMessage, returnTagRefObjects, name='Tag.getAllUserTags', path='getAllUserTags', http_method='POST')
    def getAllUserTags(self,request):
        
        #checks for blank fields
        if (request.authToken == "") or (request.userName == ""):
            return returnTagRefObjects(errorMessage = "Missing Required Fields", errorNumber=2)
        
        #validates user
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return returnTagRefObjects(errorMessage = "User Validation Failed", errorNumber = 1)
        
        tagRefList = []
        
        #gets a list of all tags objects for a given user
        tagObList = tag.Tag.getTagObjectsFromUser(userKey)
        
        for tagOb in tagObList:
            
            eventList = user_event.UserEvent.getAllEventsFromTagOb(userKey, tagOb.key.urlsafe())
            
            tagRef = tagRefObject(tagName = tagOb.name, eventCount = len(eventList), eventKeys = eventList)
            
            tagRefList.append(tagRef)
            
        return returnTagRefObjects(tagRefs = tagRefList, errorNumber = 200)   
        
