'''
Created on Sep 21, 2013

@author: jacobforster
'''
import webapp2


class PrivacyPolicy(webapp2.RequestHandler):
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write('This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.')


application = webapp2.WSGIApplication([('/privacypolicy', PrivacyPolicy)], debug = True)