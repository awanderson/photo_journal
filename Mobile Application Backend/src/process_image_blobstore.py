import webapp2

from google.appengine.ext import ndb

from APIs.Classes import photo


from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


class WebForm(webapp2.RequestHandler):
    
    def get(self):
        upload_url = blobstore.create_upload_url('/processupload')
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('<html><body>')
        self.response.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
        self.response.write("""Upload File: <input type="file" name="photo"><br>Temp Photo Key<input type="text" name="tempPhotoKey"><br> <input type="submit"
        name="submit" value="Submit"> </form></body></html>""")

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    
    def post(self):
        
        photoUpload = self.get_uploads('photo')
        
        blobInfoObject = photoUpload[0]
        
        tempPhotoKey = self.request.get('tempPhotoKey')
       
        tempPhotoKeyObject = ndb.Key(urlsafe = tempPhotoKey)
        
        tempPhotoObject = tempPhotoKeyObject.get()
       
        photo.Photo.createNewPhoto(photoKey = blobInfoObject.key(), eventKey = tempPhotoObject.eventKey.urlsafe(), userKey = tempPhotoKeyObject.parent(), privacySetting = tempPhotoObject.privacySetting)
        
        tempPhotoKeyObject.delete()
    
    

application = webapp2.WSGIApplication([('/processupload', UploadHandler), ('/uploadimage', WebForm)], debug = True)
