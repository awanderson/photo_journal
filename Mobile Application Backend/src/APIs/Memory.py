"""
Memory Specific Errors

10 => Issue Adding Memory
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
    privacy = messages.IntegerField(6, required = False)

#specifies a specific memory
class memoryKey(messages.Message):
    memoryKey = messages.StringField(1, required = True)
    userName = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)

class editMemory(messages.Message):
    title = messages.StringField(1, required = False)
    content = messages.StringField(2, required = False)
    userName = messages.StringField(4, required = True)
    authToken = messages.StringField(5, required = True)
    memoryKey = messages.StringField(6, required = True)

#returns the outcome of the api call, if there are errors or not
class callResult(messages.Message):
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)

class fullMemory(messages.Message):
    title = messages.StringField(1, required = True)
    content = messages.StringField(2, required = True)
    created = messages.StringField(3, required = True)
    memoryKey = messages.StringField(4, required = True)
    
class returnMemories(messages.Message):
    memories = messages.MessageField(fullMemory, 1, repeated=True, required=False)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)

class eventSpecifier(messages.Message):
    eventKey = messages.StringField(1, required = True)
    userName = messages.StringField(2, required = True)
    authToken = messages.StringField(3, required = True)


@endpoints.api(name = 'memoryService', version = 'v0.501', description = 'API for memory methods', hostname = 'engaged-context-254.appspot.com')
class MemoryApi(remote.Service):

    @endpoints.method(newMemory, callResult, name = 'Memory.addMemory', path = 'addMemory', http_method = 'POST')
    def addMemory(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #check to make sure there is a title and content to the memory
        if request.title == "" or request.content == "":
            return callResult(errorNumber = 2, errorMessage = "Missing Required Fields" )
        
        #create the new memory object
        boolVal = memory.Memory.addMemoryToEvent(request.title, request.content, request.eventKey, userKey)
        
        #return the result of the Api call 
        if boolVal:
            return callResult(errorNumber = 200)
        else:
            return callResult(errorNumber = 10, errorMessage = "Issue Adding Memory")
        
         
    
    @endpoints.method(memoryKey, callResult, name = 'Memory.removeMemory', path = 'removeMemory', http_method = 'POST')
    def removeMemory(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        #delete the memory from the event
        memory.Memory.removeMemoryByKey(request.memoryKey)
        
        #return the result of the Api call
        return callResult(errorNumber = 200)
        
    @endpoints.method(editMemory, callResult, name = 'Memory.editMemory', path = 'editMemory', http_method = 'POST')
    def editMemory(self, request):
        
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        
        memory.Memory.editMemoryByKey(request.title, request.content, request.memoryKey)
        
        return callResult(errorNumber = 200)

    @endpoints.method(eventSpecifier, returnMemories, name="Memory.getUserMemoriesForEvent", path="getUserMemoriesForEvent", http_method="POST")
    def getUserMemoriesForEvent(self, request):
        #check if the user is validated
        userKey = user.User.validateUser(request.userName, request.authToken)
        if not userKey:
            return callResult(errorNumber = 1, errorMessage = "User Validation Failed")
        memoryObjects = memory.Memory.getMemoriesByEvent(request.eventKey, userKey);	
        memoryObjectList = []
        
        for memoryOb in memoryObjects:
            memoryTitle = memoryOb[0]
            memoryContent = memoryOb[1]
            memoryCreated = memoryOb[2]
            memoryKey = memoryOb[3]
            
            memoryObForList = fullMemory(title = memoryTitle, content = memoryContent, created = memoryCreated, memoryKey = memoryKey);
             
            memoryObjectList.append(memoryObForList);
        
        return returnMemories(memories = memoryObjectList, errorNumber = 200)
    
    @endpoints.method(eventSpecifier, returnMemories, name="Memory.getPublicMemoriesForEvent", path="getPublicMemoriesForEvent", http_method="POST")
    def getPublicMemoriesForEvent(self, request):
        pass
