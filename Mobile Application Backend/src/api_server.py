'''
Created on Jul 14, 2013

@author: jacobforster
'''
from google.appengine.ext import endpoints

from APIs import User, Event, Memory, Photo


application = endpoints.api_server([Event.EventApi, User.UserApi, Memory.MemoryApi, Photo.PhotoApi], restricted=False)