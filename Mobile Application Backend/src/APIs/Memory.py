from protorpc import messages
from protorpc import remote
from google.appengine.ext import endpoints

#message for creating a new event
class newMemory(messages.Message):
    title = messages.StringField(1, required = False)
    content = messages.StringField(2, required = True)
    eventKey = messages.StringField(3, required = True)


@endpoints.api(name = 'memoryService', version = 'v0.01', description = 'API for memory methods', hostname = 'engaged-context-254.appspot.com')
class MemoryApi(remote.Service):

    @endpoints.method()
    def addMemoryToEvent(self,):
        pass
    
    @endpoints.method()
    def removeMemoryFromEvent(self, ):
        pass