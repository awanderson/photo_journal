'''
Created on Jul 14, 2013

@author: jacobforster
'''
from google.appengine.ext import ndb


class userModel(ndb.Model):
    userName = ndb.StringProperty(required = True)
    email = ndb.StringProperty()
    phoneNumber = ndb.IntegerProperty()
