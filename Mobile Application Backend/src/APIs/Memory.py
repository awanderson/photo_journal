"""
Memory Specific Errors

 - None - 
"""

from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

from Classes import user
from Classes import memory

#message for creating a new event
class newMemory(messages.Message):
    title = messages.StringField(1, required = True)
    content = messages.StringField(2, required = True)
    eventKey = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)
    authToken = messages.StringField(5, required = True)

#specifies a specific memory
class memoryKey(messages.Message):
    memoryKey = messages.StringField(1, required = True)
    userName = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)
    
#returns the outcome of the api call, if there are errors or not
class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)


@endpoints.api(name = 'memoryService', version = 'v0.021', description = 'API for memory methods', hostname = 'engaged-context-254.appspot.com')
class MemoryApi(remote.Service):

    @endpoints.method(newMemory, callResult, name = 'Memory.addMemory', path = 'addMemory', http_method = 'POST')
    def addMemory(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorNumber = 1, errorMessage = "User Validation Failed")
        
        #check to make sure there is a title and content to the memory
        if request.title == "" or request.content == "":
            return callResult(booleanValue = False, errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        #create the new memory object
        memory.Memory.addMemoryToEvent(request.title, request.content, request.eventKey, userKey)
        
        #return the result of the Api call 
        return callResult(booleanValue = True)
         
    
    @endpoints.method(memoryKey, callResult, name = 'Memory.removeMemory', path = 'removeMemory', http_method = 'POST')
    def removeMemory(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(booleanValue = False, errorNumber = 1, errorMessage = "User Validation Failed")
        
        #delete the memory from the event
        memory.Memory.removeMemoryByKey(request.memoryKey)
        
        #return the result of the Api call
        return callResult(booleanValue = True)
        
        
            
            
