'''
Created on Jul 14, 2013

@author: jacobforster
'''
from google.appengine.ext import endpoints

from APIs import User
from APIs import Event


application = endpoints.api_server([Event.EventApi, User.UserApi], restricted=False)