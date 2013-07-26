'''
Created on Jul 25, 2013

@author: jacobforster
'''

from google.appengine.ext import ndb

class PhotoDB(ndb.Model):
    
    photo = ndb.BlobKeyProperty()
    dateAdded = ndb.DateTimeProperty()
    eventReference = ndb.KeyProperty()#event added to
    userReference = ndb.KeyProperty()#user who uploaded photo
    privacySetting = ndb.IntegerProperty(choices = 0, 1, 2)
    
    
    #NEED PHOTO BLOB OBJECT SOMEWHERE SOMEHOW
    
    