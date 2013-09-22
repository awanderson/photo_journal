'''
Created on Sep 21, 2013

@author: jacobforster
'''
import webapp2


class TermsOfService(webapp2.RequestHandler):
    
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('This will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of serviceThis will be a terms of service.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.This will be a privacy policy.')


application = webapp2.WSGIApplication([('/termsofservice', TermsOfService)], debug = True)