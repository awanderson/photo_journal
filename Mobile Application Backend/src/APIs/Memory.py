from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

#message for creating a new event
class newMemory(messages.Message):
    title = messages.StringField(1, required = False)
    content = messages.StringField(2, required = True)
    eventKey = messages.StringField(3, required = True)
    userName = messages.StringField(4, required = True)
    authToken = messages.StringField(5, required = True)
    
class callResult(messages.Message):
    booleanValue = messages.BooleanField(1, required = True)
    errorMessage = messages.StringField(2, required = False)
    errorNumber = messages.IntegerField(3, required = False)


@endpoints.api(name = 'memoryService', version = 'v0.01', description = 'API for memory methods', hostname = 'engaged-context-254.appspot.com')
class MemoryApi(remote.Service):

    @endpoints.method(newMemory, callResult, name = 'Memory.addMemoryToEvent', path = 'addMemoryToEvent', http_method = 'POST')
    def addMemoryToEvent(self,):
        pass
    
    #@endpoints.method()
    #def removeMemoryFromEvent(self, ):
      #  pass