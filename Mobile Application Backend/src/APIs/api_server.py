'''
Created on Jul 14, 2013

@author: jacobforster
'''
from google.appengine.ext import endpoints

import User
#import other_api


application = endpoints.api_server([User.UserApi], restricted=False)