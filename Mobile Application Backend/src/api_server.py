'''
Created on Jul 14, 2013

@author: jacobforster
'''
from google.appengine.ext import endpoints

from APIs import User
from APIs import Event
from APIs import Memory
from APIs import Tag


application = endpoints.api_server([Event.EventApi, User.UserApi, Memory.MemoryApi, Tag.TagApi], restricted=False)